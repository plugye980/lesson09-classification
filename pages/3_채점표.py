import numpy as np
import pandas as pd
import streamlit as st
from sklearn.dummy import DummyClassifier
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
BASELINE_NAME = "훈련용에서 많은 쪽으로만 답하는 모델"
NOT_AVAILABLE = "계산할 수 없음"
LIST_LIMIT = 20

st.set_page_config(page_title="채점표", page_icon=":material/neurology:", layout="wide")


@st.cache_data
def load_data():
    return pd.read_csv(DATA_URL, encoding="utf-8")


st.title("채점표")
st.write("stroke가 1이면 뇌졸중, 0이면 뇌졸중이 아니다. 뇌졸중(1)을 양성으로 둔다.")

# 입력으로 쓸 속성 고르기 ('분류 모델' 페이지와 같은 방법)
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

# 크기 맞추기는 훈련용으로만
scaler = StandardScaler().fit(X_train)
Z_train = scaler.transform(X_train)
Z_test = scaler.transform(X_test)

# 모델 학습
logistic = LogisticRegression(random_state=RANDOM_STATE).fit(Z_train, y_train)
tree = DecisionTreeClassifier(max_depth=3, min_samples_split=5, random_state=RANDOM_STATE).fit(X_train, y_train)
baseline = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)

predictions = {
    LOGISTIC_NAME: logistic.predict(Z_test),
    TREE_NAME: tree.predict(X_test),
    BASELINE_NAME: baseline.predict(X_test),
}


def counts(y_true, y_pred):
    tp = int(((y_true == 1) & (y_pred == 1)).sum())
    fp = int(((y_true == 0) & (y_pred == 1)).sum())
    fn = int(((y_true == 1) & (y_pred == 0)).sum())
    tn = int(((y_true == 0) & (y_pred == 0)).sum())
    return tp, fp, fn, tn


def confusion_table(y_true, y_pred):
    tp, fp, fn, tn = counts(y_true, y_pred)
    return pd.DataFrame(
        {
            "예측: 아님(0)": [f"TN {tn:,}명", f"FN {fn:,}명", f"{tn + fn:,}명"],
            "예측: 뇌졸중(1)": [f"FP {fp:,}명", f"TP {tp:,}명", f"{fp + tp:,}명"],
            "합계": [f"{tn + fp:,}명", f"{fn + tp:,}명", f"{tn + fp + fn + tp:,}명"],
        },
        index=["실제: 아님(0)", "실제: 뇌졸중(1)", "합계"],
    )


def percent(value):
    return NOT_AVAILABLE if value is None else f"{value * 100:.1f}%"


def scores(y_true, y_pred):
    tp, fp, fn, tn = counts(y_true, y_pred)
    accuracy = (tp + tn) / (tp + fp + fn + tn)
    recall = tp / (tp + fn) if tp + fn else None
    precision = tp / (tp + fp) if tp + fp else None
    if precision is None or recall is None or precision + recall == 0:
        f1 = None
    else:
        f1 = 2 * precision * recall / (precision + recall)
    return {"정확도": percent(accuracy), "재현율": percent(recall), "정밀도": percent(precision), "F1": percent(f1)}


# 혼동행렬
st.subheader("혼동행렬 (테스트 데이터)")
st.caption("행은 실제, 열은 예측이다. TP는 뇌졸중을 뇌졸중으로, TN은 아님을 아님으로 맞힌 칸이고, "
           "FP는 아닌데 뇌졸중이라 한 칸, FN은 뇌졸중인데 아니라고 한 칸이다.")
c1, c2 = st.columns(2)
for col, name in zip((c1, c2), (LOGISTIC_NAME, TREE_NAME)):
    with col:
        st.markdown(f"**{name}**")
        st.table(confusion_table(y_test, predictions[name]))

# 네 지표
st.subheader("네 지표")
st.write(f"테스트용 {len(test):,}명, 그중 뇌졸중인 사람 {int(y_test.sum()):,}명")
score_table = pd.DataFrame(
    [{"모델": name, **scores(y_test, pred)} for name, pred in predictions.items()]
)
st.table(score_table.set_index("모델"))
st.caption("재현율 = TP ÷ 실제 뇌졸중인 사람 수, 정밀도 = TP ÷ 뇌졸중이라 예측한 사람 수, "
           "F1 = 2 × 정밀도 × 재현율 ÷ (정밀도 + 재현율)")

# 놓친 환자와 헛짚은 사람 목록
st.subheader("틀린 사람 목록")
model_name = st.radio("모델", [LOGISTIC_NAME, TREE_NAME], horizontal=True)
pred = predictions[model_name]
tp, fp, fn, tn = counts(y_test, pred)


def people_list(mask):
    people = test.loc[mask, ["id", "age", "avg_glucose_level", "hypertension", "heart_disease"]].copy()
    people = people.sort_values("age", ascending=False)
    people["hypertension"] = people["hypertension"].map({1: "있음", 0: "없음"})
    people["heart_disease"] = people["heart_disease"].map({1: "있음", 0: "없음"})
    return people.rename(
        columns={"id": "번호", "age": "나이", "avg_glucose_level": "평균 혈당", "hypertension": "고혈압", "heart_disease": "심장병"}
    )


missed = people_list((y_test == 1) & (pred == 0))
false_alarm = people_list((y_test == 0) & (pred == 1))

left, right = st.columns(2)
for col, title, people in [
    (left, "놓친 환자: 실제 뇌졸중인데 아니라고 예측", missed),
    (right, "헛짚은 사람: 아닌데 뇌졸중이라고 예측", false_alarm),
]:
    with col:
        st.markdown(f"**{title} (전체 {len(people):,}명)**")
        if len(people) > LIST_LIMIT:
            st.caption(f"나이가 많은 순으로 앞 {LIST_LIMIT}명만 보여 준다.")
        if len(people):
            st.dataframe(people.head(LIST_LIMIT), hide_index=True, width="stretch")
        else:
            st.write("해당하는 사람이 없다.")

same_fn = "같다" if len(missed) == fn else "다르다"
same_fp = "같다" if len(false_alarm) == fp else "다르다"
st.write(
    f"놓친 환자 {len(missed):,}명은 혼동행렬의 FN 칸 {fn:,}명과 {same_fn}. "
    f"헛짚은 사람 {len(false_alarm):,}명은 FP 칸 {fp:,}명과 {same_fp}."
)
