import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

DATA_URL = "https://raw.githubusercontent.com/plugye980/stroke-data/refs/heads/main/stroke.csv"
RANDOM_STATE = 42

KOREAN = {
    "age": "나이",
    "avg_glucose_level": "평균 혈당",
    "bmi": "체질량지수",
    "hypertension": "고혈압",
    "heart_disease": "심장병",
}
FEATURES = list(KOREAN)
BINARY = {"hypertension", "heart_disease"}

LOGISTIC_NAME = "로지스틱 회귀(확률로 답하는 모델)"
TREE_NAME = "의사결정트리(질문으로 답하는 모델)"
BASELINE_NAME = "입력을 하나도 보지 않고 훈련용에서 많은 쪽으로만 답하는 모델"

st.set_page_config(page_title="분류 모델", page_icon=":material/neurology:", layout="wide")


@st.cache_data
def load_data():
    return pd.read_csv(DATA_URL, encoding="utf-8")


def fmt(value):
    return f"{value:,.1f}" if abs(value - round(value)) > 1e-9 else f"{value:,.0f}"


st.title("분류 모델")
st.write("stroke가 1이면 뇌졸중, 0이면 뇌졸중이 아니다. 뇌졸중(1)을 양성으로 둔다.")

# 입력으로 쓸 속성 고르기
selected = st.multiselect(
    "입력으로 사용할 속성",
    options=FEATURES,
    default=[f for f in FEATURES if f != "bmi"],
    format_func=lambda c: KOREAN[c],
)
if len(selected) < 2:
    st.info("속성을 두 개 이상 골라야 한다.")
    st.stop()

# 데이터 나누기: id 순으로 정렬, 열 명씩 묶어 각 묶음의 앞 세 명을 테스트용으로
df = load_data().sort_values("id").reset_index(drop=True)
position_in_group = np.arange(len(df)) % 10
is_test = position_in_group < 3
train = df[~is_test]
test = df[is_test]

X_train = train[selected].copy()
X_test = test[selected].copy()
y_train = train["stroke"].to_numpy()
y_test = test["stroke"].to_numpy()

# 체질량지수를 고른 경우에만 훈련용 중앙값으로 빈 값 채우기
if "bmi" in selected:
    bmi_median = X_train["bmi"].median()
    X_train["bmi"] = X_train["bmi"].fillna(bmi_median)
    X_test["bmi"] = X_test["bmi"].fillna(bmi_median)
    st.caption(f"체질량지수의 빈 값은 훈련용 중앙값 {bmi_median:.1f}(으)로 채웠다.")

st.caption(f"훈련용 {len(train):,}명, 테스트용 {len(test):,}명")

# 크기 맞추기는 훈련용으로만
scaler = StandardScaler().fit(X_train)
Z_train = scaler.transform(X_train)
Z_test = scaler.transform(X_test)

# 모델 학습
logistic = LogisticRegression(random_state=RANDOM_STATE).fit(Z_train, y_train)
tree = DecisionTreeClassifier(max_depth=3, min_samples_split=5, random_state=RANDOM_STATE).fit(X_train, y_train)
baseline = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)

results = [
    (LOGISTIC_NAME, logistic.predict(Z_train), logistic.predict(Z_test)),
    (TREE_NAME, tree.predict(X_train), tree.predict(X_test)),
    (BASELINE_NAME, baseline.predict(X_train), baseline.predict(X_test)),
]

# 정확도 카드
st.subheader("정확도")
cols = st.columns(3)
for col, (name, pred_train, pred_test) in zip(cols, results):
    train_acc = accuracy_score(y_train, pred_train) * 100
    test_acc = accuracy_score(y_test, pred_test) * 100
    with col.container(border=True):
        st.markdown(f"**{name}**")
        st.metric("테스트 데이터 정확도", f"{test_acc:.1f}%")
        st.caption(f"훈련 데이터 {train_acc:.1f}% · 테스트 데이터 {test_acc:.1f}%")

# 두 속성으로 그린 그림
st.subheader("두 속성으로 본 테스트 데이터")
c1, c2 = st.columns(2)
x_col = c1.selectbox("가로축", selected, index=0, format_func=lambda c: KOREAN[c])
y_options = [c for c in selected if c != x_col]
y_col = c2.selectbox("세로축", y_options, index=0, format_func=lambda c: KOREAN[c])

others = [c for c in selected if c not in (x_col, y_col)]
fixed = X_test.median()
if others:
    st.write("두 축이 아닌 속성은 테스트 데이터의 중앙값에 세워 두고 계산했다: "
             + ", ".join(f"{KOREAN[c]} {fmt(fixed[c])}" for c in others))


def axis_range(values):
    lo, hi = float(values.min()), float(values.max())
    pad = (hi - lo) * 0.05 if hi > lo else 0.5
    return lo - pad, hi + pad


x_lo, x_hi = axis_range(X_test[x_col])
y_lo, y_hi = axis_range(X_test[y_col])

fig = go.Figure()

# 의사결정트리가 나눈 칸을 옅은 색으로 칠하기
grid_x = np.linspace(x_lo, x_hi, 200)
grid_y = np.linspace(y_lo, y_hi, 200)
gx, gy = np.meshgrid(grid_x, grid_y)
grid = pd.DataFrame({c: np.full(gx.size, fixed[c]) for c in selected})
grid[x_col] = gx.ravel()
grid[y_col] = gy.ravel()
tree_answer = tree.predict(grid[selected]).reshape(gx.shape)
fig.add_trace(
    go.Heatmap(
        x=grid_x, y=grid_y, z=tree_answer, zmin=0, zmax=1,
        colorscale=[[0, "rgba(99, 140, 230, 0.15)"], [1, "rgba(230, 80, 70, 0.22)"]],
        showscale=False, hoverinfo="skip",
    )
)
fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(symbol="square", size=12, color="rgba(99, 140, 230, 0.35)"), name="트리가 '아님'이라고 답하는 칸"))
fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(symbol="square", size=12, color="rgba(230, 80, 70, 0.4)"), name="트리가 '뇌졸중'이라고 답하는 칸"))

# 테스트 데이터 점
for value, label, color in [(0, "뇌졸중 아님 (0)", "#4c78a8"), (1, "뇌졸중 (1)", "#e45756")]:
    mask = y_test == value
    fig.add_trace(
        go.Scatter(
            x=X_test.loc[mask, x_col], y=X_test.loc[mask, y_col], mode="markers", name=label,
            marker=dict(color=color, size=6, opacity=0.75 if value == 1 else 0.45),
        )
    )

# 로지스틱 회귀의 확률 0.5 선: 크기 맞춘 공간에서 w·z + b = 0
coef = dict(zip(selected, logistic.coef_[0]))
mean = dict(zip(selected, scaler.mean_))
scale = dict(zip(selected, scaler.scale_))
const = logistic.intercept_[0] + sum(coef[c] * (fixed[c] - mean[c]) / scale[c] for c in others)
wx, wy = coef[x_col], coef[y_col]

line_x, line_y = None, None
if abs(wy) > 1e-12:
    line_x = np.linspace(x_lo, x_hi, 400)
    zx = (line_x - mean[x_col]) / scale[x_col]
    zy = -(wx * zx + const) / wy
    line_y = zy * scale[y_col] + mean[y_col]
elif abs(wx) > 1e-12:
    zx = -const / wx
    x_at = zx * scale[x_col] + mean[x_col]
    line_x = np.array([x_at, x_at])
    line_y = np.array([y_lo, y_hi])

line_visible = False
if line_x is not None:
    inside = (line_x >= x_lo) & (line_x <= x_hi) & (line_y >= y_lo) & (line_y <= y_hi)
    line_visible = bool(inside.any())
    if line_visible:
        fig.add_trace(
            go.Scatter(x=line_x, y=line_y, mode="lines", name="로지스틱 회귀 확률 0.5 선", line=dict(color="black", width=2, dash="dash"))
        )

fig.update_layout(
    xaxis=dict(title=KOREAN[x_col], range=[x_lo, x_hi]),
    yaxis=dict(title=KOREAN[y_col], range=[y_lo, y_hi]),
    legend=dict(orientation="h", y=-0.2),
    height=560,
)
st.plotly_chart(fig)

if not line_visible:
    st.write("로지스틱 회귀의 확률 0.5 선은 그림 밖에 있어 보이지 않는다.")

# 의사결정트리 그림
st.subheader("의사결정트리가 던진 질문")

node_path = tree.decision_path(X_train)
node_count = np.asarray(node_path.sum(axis=0)).ravel()
node_stroke = np.asarray(node_path.T @ y_train).ravel()
t = tree.tree_


def question(node):
    feature = selected[t.feature[node]]
    if feature in BINARY:
        return f"{KOREAN[feature]}이 없는가?"
    return f"{KOREAN[feature]} ≤ {t.threshold[node]:.1f} 인가?"


lines = [
    "digraph tree {",
    'node [shape=box, style="rounded,filled", fontname="sans-serif", fontsize=11];',
    'edge [fontname="sans-serif", fontsize=10];',
]
leaves = []
for node in range(t.node_count):
    n, k = int(node_count[node]), int(node_stroke[node])
    stats = f"훈련 {n:,}명 · 뇌졸중 {k:,}명 ({k / n * 100:.1f}%)" if n else "훈련 0명"
    if t.children_left[node] == -1:
        answer = int(tree.classes_[np.argmax(t.value[node][0])])
        leaves.append(answer)
        label = f"답: {'뇌졸중' if answer == 1 else '아님'}\\n{stats}"
        color = "#f6c4bf" if answer == 1 else "#cfdcf5"
    else:
        label = f"{question(node)}\\n{stats}"
        color = "#f2f2f2"
    lines.append(f'n{node} [label="{label}", fillcolor="{color}"];')
for node in range(t.node_count):
    if t.children_left[node] != -1:
        lines.append(f'n{node} -> n{t.children_left[node]} [label="예"];')
        lines.append(f'n{node} -> n{t.children_right[node]} [label="아니오"];')
lines.append("}")
st.graphviz_chart("\n".join(lines))

used = [selected[i] for i in sorted(set(t.feature[t.feature >= 0]))]
st.write(f"답을 내는 마디는 모두 {len(leaves)}칸이고, 그중 {leaves.count(0)}칸이 '아님'이라고 답한다.")
st.write("이 나무가 실제로 물은 속성: " + (", ".join(KOREAN[c] for c in used) if used else "없음"))
