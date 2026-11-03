import pandas as pd
import plotly.express as px
import streamlit as st

DATA_URL = "https://raw.githubusercontent.com/plugye980/stroke-data/refs/heads/main/stroke.csv"

st.set_page_config(page_title="탐색", page_icon=":material/neurology:", layout="wide")


@st.cache_data
def load_data():
    return pd.read_csv(DATA_URL, encoding="utf-8")


df = load_data().copy()
total = len(df)
n_stroke = int((df["stroke"] == 1).sum())
ratio = n_stroke / total * 100 if total else 0

GROUP_NO = "뇌졸중 겪지 않음"
GROUP_YES = "뇌졸중 겪음"
df["그룹"] = df["stroke"].map({0: GROUP_NO, 1: GROUP_YES})
order = {"그룹": [GROUP_NO, GROUP_YES]}

st.title("탐색")
st.write("나이, 평균 혈당, 질환, 흡연 상태에 따라 뇌졸중이 어떻게 나타나는지 살펴본다.")

# 1. 나이와 평균 혈당의 분포
st.subheader("나이와 평균 혈당의 분포")
c1, c2 = st.columns(2)
with c1:
    fig = px.histogram(df, x="age", nbins=40, labels={"age": "나이"}, title="나이")
    fig.update_yaxes(title="사람 수")
    st.plotly_chart(fig)
with c2:
    fig = px.histogram(df, x="avg_glucose_level", nbins=40, labels={"avg_glucose_level": "평균 혈당"}, title="평균 혈당")
    fig.update_yaxes(title="사람 수")
    st.plotly_chart(fig)

# 2. 뇌졸중을 겪은 사람과 겪지 않은 사람 비교
st.subheader("뇌졸중을 겪은 사람과 겪지 않은 사람")
c1, c2 = st.columns(2)
with c1:
    fig = px.box(df, x="그룹", y="age", color="그룹", category_orders=order, labels={"age": "나이", "그룹": ""}, title="그룹별 나이")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)
with c2:
    fig = px.box(
        df, x="그룹", y="avg_glucose_level", color="그룹", category_orders=order,
        labels={"avg_glucose_level": "평균 혈당", "그룹": ""}, title="그룹별 평균 혈당",
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)

mean_table = (
    df.groupby("그룹")
    .agg(사람_수=("stroke", "size"), 평균_나이=("age", "mean"), 평균_혈당=("avg_glucose_level", "mean"))
    .reindex([GROUP_NO, GROUP_YES])
    .reset_index()
    .rename(columns={"사람_수": "사람 수", "평균_나이": "평균 나이", "평균_혈당": "평균 혈당"})
    .round(1)
)
st.write("그룹별 평균값")
st.dataframe(mean_table, hide_index=True)


# 3. 고혈압, 심장병 여부에 따른 뇌졸중 비율
def stroke_ratio_table(column):
    table = df.groupby(column)["stroke"].mean().reindex([0, 1]).mul(100).round(1)
    return pd.DataFrame({"구분": ["없음", "있음"], "뇌졸중 비율(%)": table.values})


st.subheader("질환 여부에 따른 뇌졸중 비율")
c1, c2 = st.columns(2)
with c1:
    fig = px.bar(stroke_ratio_table("hypertension"), x="구분", y="뇌졸중 비율(%)", text="뇌졸중 비율(%)", title="고혈압")
    fig.update_xaxes(title="고혈압")
    st.plotly_chart(fig)
with c2:
    fig = px.bar(stroke_ratio_table("heart_disease"), x="구분", y="뇌졸중 비율(%)", text="뇌졸중 비율(%)", title="심장병")
    fig.update_xaxes(title="심장병")
    st.plotly_chart(fig)

# 4. bmi가 비어 있는 사람
st.subheader("체질량지수(bmi)가 비어 있는 사람")
missing = df[df["bmi"].isna()]
bmi_table = pd.DataFrame(
    {
        "구분": ["bmi가 비어 있는 사람", "전체"],
        "사람 수": [len(missing), total],
        "뇌졸중 겪은 사람 수": [int(missing["stroke"].sum()), n_stroke],
        "뇌졸중 비율(%)": [round(missing["stroke"].mean() * 100, 1) if len(missing) else 0.0, round(ratio, 1)],
    }
)
st.dataframe(bmi_table, hide_index=True)

# 5. 흡연 상태별 사람 수
st.subheader("흡연 상태별 사람 수")
smoke_table = df["smoking_status"].value_counts().rename_axis("흡연 상태").reset_index(name="사람 수")
st.dataframe(smoke_table, hide_index=True)
