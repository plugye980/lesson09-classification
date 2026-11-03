import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sklearn.linear_model import LogisticRegression
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

LOGISTIC_NAME = "로지스틱 회귀(확률로 답하는 모델)"
TREE_NAME = "의사결정트리(질문으로 답하는 모델)"
BEFORE = "맞추기 전"
AFTER = "맞춘 후"
NOT_AVAILABLE = "계산할 수 없음"
BEFORE_COLOR = "#7f7f7f"
AFTER_COLOR = "#2ca02c"

st.set_page_config(page_title="성능 높이기", page_icon=":material/neurology:", layout="wide")


@st.cache_data
def load_data():
    return pd.read_csv(DATA_URL, encoding="utf-8")


def fmt(value):
    return f"{value:,.1f}" if abs(value - round(value)) > 1e-9 else f"{value:,.0f}"


st.title("성능 높이기")

# 입력으로 쓸 속성 고르기 ('분류 모델' 페이지와 같은 자리)
selected = st.multiselect(
    "입력으로 사용할 속성",
    options=FEATURES,
    default=[f for f in FEATURES if f != "bmi"],
    format_func=lambda c: KOREAN[c],
)
if len(selected) < 2:
    st.info("속성을 두 개 이상 골라야 한다.")
    st.stop()

st.write(
    "뇌졸중(1)을 양성으로 둔다. 뇌졸중을 겪은 사람이 아주 드물어서 모델이 거의 모두 '아님'이라고 답한다. "
    "양쪽의 가중치를 맞추면(드문 쪽 한 명을 더 무겁게 세면) 결과가 어떻게 바뀌는지 본다."
)

# 데이터 나누기: id 순으로 정렬, 열 명씩 묶어 각 묶음의 앞 세 명을 테스트용으로
df = load_data().sort_values("id").reset_index(drop=True)
is_test = np.arange(len(df)) % 10 < 3
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

# 크기 맞추기는 훈련용으로만
scaler = StandardScaler().fit(X_train)
Z_train = scaler.transform(X_train)
Z_test = scaler.transform(X_test)

# 가중치를 맞추기 전과 맞춘 후의 두 모델
logistic = {
    BEFORE: LogisticRegression(random_state=RANDOM_STATE).fit(Z_train, y_train),
    AFTER: LogisticRegression(class_weight="balanced", random_state=RANDOM_STATE).fit(Z_train, y_train),
}
tree = {
    BEFORE: DecisionTreeClassifier(max_depth=3, min_samples_split=5, random_state=RANDOM_STATE).fit(X_train, y_train),
    AFTER: DecisionTreeClassifier(
        max_depth=3, min_samples_split=5, class_weight="balanced", random_state=RANDOM_STATE
    ).fit(X_train, y_train),
}
predictions = {
    LOGISTIC_NAME: {k: m.predict(Z_test) for k, m in logistic.items()},
    TREE_NAME: {k: m.predict(X_test) for k, m in tree.items()},
}


def counts(y_true, y_pred):
    tp = int(((y_true == 1) & (y_pred == 1)).sum())
    fp = int(((y_true == 0) & (y_pred == 1)).sum())
    fn = int(((y_true == 1) & (y_pred == 0)).sum())
    tn = int(((y_true == 0) & (y_pred == 0)).sum())
    return tp, fp, fn, tn


def percent(value):
    return NOT_AVAILABLE if value is None else f"{value * 100:.1f}%"


def score_column(y_true, y_pred):
    tp, fp, fn, tn = counts(y_true, y_pred)
    accuracy = (tp + tn) / (tp + fp + fn + tn)
    recall = tp / (tp + fn) if tp + fn else None
    precision = tp / (tp + fp) if tp + fp else None
    if precision is None or recall is None or precision + recall == 0:
        f1 = None
    else:
        f1 = 2 * precision * recall / (precision + recall)
    return [f"{tp:,}명", f"{fp:,}명", f"{fn:,}명", f"{tn:,}명",
            percent(accuracy), percent(recall), percent(precision), percent(f1)]


ROW_NAMES = ["TP (찾아낸 환자)", "FP (헛짚은 사람)", "FN (놓친 환자)", "TN", "정확도", "재현율", "정밀도", "F1"]

# 전·후 비교표
st.subheader("가중치를 맞추기 전과 맞춘 후")
st.write(f"테스트용 {len(test):,}명, 그중 뇌졸중인 사람 {int(y_test.sum()):,}명")
cols = st.columns(2)
for col, name in zip(cols, (LOGISTIC_NAME, TREE_NAME)):
    pred = predictions[name]
    table = pd.DataFrame(
        {BEFORE: score_column(y_test, pred[BEFORE]), AFTER: score_column(y_test, pred[AFTER])},
        index=ROW_NAMES,
    )
    tp0, fp0, fn0, _ = counts(y_test, pred[BEFORE])
    tp1, fp1, fn1, _ = counts(y_test, pred[AFTER])
    with col:
        st.markdown(f"**{name}**")
        st.table(table)
        st.write(
            f"찾아낸 환자 {tp0:,}명 → {tp1:,}명, 놓친 환자 {fn0:,}명 → {fn1:,}명, "
            f"헛짚은 사람 {fp0:,}명 → {fp1:,}명"
        )

# 로지스틱 회귀의 0.5 경계 계산에 쓰는 값
fixed = X_test.median()
mean = dict(zip(selected, scaler.mean_))
scale = dict(zip(selected, scaler.scale_))


def axis_range(values):
    lo, hi = float(values.min()), float(values.max())
    pad = (hi - lo) * 0.05 if hi > lo else 0.5
    return lo - pad, hi + pad


def boundary_parts(model, axes):
    """축이 아닌 속성을 중앙값에 세웠을 때 w·z + c = 0 의 축별 계수와 상수."""
    coef = dict(zip(selected, model.coef_[0]))
    others = [c for c in selected if c not in axes]
    const = model.intercept_[0] + sum(coef[c] * (fixed[c] - mean[c]) / scale[c] for c in others)
    return [coef[a] for a in axes], const


def to_raw(column, z):
    return z * scale[column] + mean[column]


def to_scaled(column, x):
    return (x - mean[column]) / scale[column]


def fixed_note(axes):
    others = [c for c in selected if c not in axes]
    if others:
        st.write("축이 아닌 속성은 테스트 데이터의 중앙값에 세워 두고 계산했다: "
                 + ", ".join(f"{KOREAN[c]} {fmt(fixed[c])}" for c in others))


def point_traces(axes, is_3d=False):
    traces = []
    for value, label, color in [(0, "뇌졸중 아님 (0)", "#4c78a8"), (1, "뇌졸중 (1)", "#e45756")]:
        mask = y_test == value
        coords = {k: X_test.loc[mask, a] for k, a in zip("xyz", axes)}
        if is_3d:
            traces.append(go.Scatter3d(**coords, mode="markers", name=label,
                                       marker=dict(color=color, size=3, opacity=0.8 if value == 1 else 0.35)))
        else:
            traces.append(go.Scatter(**coords, mode="markers", name=label,
                                     marker=dict(color=color, size=6, opacity=0.75 if value == 1 else 0.45)))
    return traces


# 2차원 산점도
st.subheader("두 속성으로 본 0.5 경계선")
c1, c2 = st.columns(2)
x_col = c1.selectbox("가로축", selected, index=0, format_func=lambda c: KOREAN[c])
y_col = c2.selectbox("세로축", [c for c in selected if c != x_col], index=0, format_func=lambda c: KOREAN[c])
fixed_note([x_col, y_col])

x_lo, x_hi = axis_range(X_test[x_col])
y_lo, y_hi = axis_range(X_test[y_col])
fig = go.Figure(point_traces([x_col, y_col]))

hidden = []
for key, color in [(BEFORE, BEFORE_COLOR), (AFTER, AFTER_COLOR)]:
    (wx, wy), const = boundary_parts(logistic[key], [x_col, y_col])
    if abs(wy) > 1e-12:
        line_x = np.linspace(x_lo, x_hi, 400)
        line_y = to_raw(y_col, -(wx * to_scaled(x_col, line_x) + const) / wy)
    elif abs(wx) > 1e-12:
        x_at = to_raw(x_col, -const / wx)
        line_x, line_y = np.array([x_at, x_at]), np.array([y_lo, y_hi])
    else:
        line_x, line_y = np.array([]), np.array([])
    inside = (line_x >= x_lo) & (line_x <= x_hi) & (line_y >= y_lo) & (line_y <= y_hi)
    if inside.any():
        fig.add_trace(go.Scatter(x=line_x, y=line_y, mode="lines", name=f"{key} 0.5 경계선",
                                 line=dict(color=color, width=3, dash="dash" if key == BEFORE else "solid")))
    else:
        hidden.append(key)

fig.update_layout(
    xaxis=dict(title=KOREAN[x_col], range=[x_lo, x_hi]),
    yaxis=dict(title=KOREAN[y_col], range=[y_lo, y_hi]),
    legend=dict(orientation="h", y=-0.2),
    height=560,
)
st.plotly_chart(fig)
st.caption(f"경계선은 {LOGISTIC_NAME}의 것이다.")
for key in hidden:
    st.write(f"{key}의 0.5 경계선은 그림 밖에 있어 보이지 않는다.")

# 3차원 산점도
if len(selected) >= 3:
    st.subheader("세 속성으로 본 0.5 평면")
    axes3 = st.multiselect(
        "축으로 쓸 속성 세 개",
        options=selected,
        default=selected[:3],
        max_selections=3,
        format_func=lambda c: KOREAN[c],
    )
    if len(axes3) != 3:
        st.info("축으로 쓸 속성을 세 개 골라야 한다.")
    else:
        fixed_note(axes3)
        ranges = [axis_range(X_test[a]) for a in axes3]
        fig3 = go.Figure(point_traces(axes3, is_3d=True))
        hidden3 = []
        for key, color in [(BEFORE, BEFORE_COLOR), (AFTER, AFTER_COLOR)]:
            weights, const = boundary_parts(logistic[key], axes3)
            # 계수가 가장 큰 축을 나머지 두 축으로 풀어 평면을 그린다
            solve = int(np.argmax(np.abs(weights)))
            if abs(weights[solve]) < 1e-12:
                hidden3.append(key)
                continue
            free = [i for i in range(3) if i != solve]
            g1, g2 = np.meshgrid(np.linspace(*ranges[free[0]], 40), np.linspace(*ranges[free[1]], 40))
            z_free = [to_scaled(axes3[free[0]], g1), to_scaled(axes3[free[1]], g2)]
            z_solve = -(weights[free[0]] * z_free[0] + weights[free[1]] * z_free[1] + const) / weights[solve]
            solved = to_raw(axes3[solve], z_solve)
            lo, hi = ranges[solve]
            solved = np.where((solved >= lo) & (solved <= hi), solved, np.nan)
            if np.isnan(solved).all():
                hidden3.append(key)
                continue
            grids = {free[0]: g1, free[1]: g2, solve: solved}
            fig3.add_trace(
                go.Surface(
                    x=grids[0], y=grids[1], z=grids[2],
                    colorscale=[[0, color], [1, color]], showscale=False, opacity=0.45,
                    name=f"{key} 0.5 평면", showlegend=True, hoverinfo="name",
                )
            )
        fig3.update_layout(
            scene=dict(
                xaxis=dict(title=KOREAN[axes3[0]], range=list(ranges[0])),
                yaxis=dict(title=KOREAN[axes3[1]], range=list(ranges[1])),
                zaxis=dict(title=KOREAN[axes3[2]], range=list(ranges[2])),
            ),
            legend=dict(orientation="h", y=-0.05),
            height=650,
        )
        st.plotly_chart(fig3)
        st.caption(f"평면은 {LOGISTIC_NAME}의 것이다. 마우스로 끌어 돌려 볼 수 있다.")
        for key in hidden3:
            st.write(f"{key}의 0.5 평면은 그림 밖에 있어 보이지 않는다.")
