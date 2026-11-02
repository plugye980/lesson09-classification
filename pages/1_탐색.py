import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from common import (
    BLUE,
    GRAY,
    RED,
    chart_label,
    footer,
    hero,
    inject_style,
    load_data,
    section_head,
    show_fig,
    style_fig,
)

st.set_page_config(
    page_title="탐색 | 뇌졸중 예측 실습실",
    page_icon=":material/neurology:",
    layout="wide",
)

df = load_data()

total = len(df)
n_stroke = int((df["stroke"] == 1).sum())
ratio = n_stroke / total * 100 if total else 0

GROUP_NO = "뇌졸중 겪지 않음"
GROUP_YES = "뇌졸중 겪음"
df["그룹"] = df["stroke"].map({0: GROUP_NO, 1: GROUP_YES})

inject_style()

hero(
    links=[
        ("분포", "#dist"),
        ("그룹 비교", "#compare"),
        ("질환별 비율", "#disease"),
        ("bmi 빈 값", "#bmi"),
        ("흡연 상태", "#smoking"),
    ],
    page_link=("홈", "./"),
    ratio=ratio,
    title="탐색",
    sub="나이, 혈당, 질환, 흡연 상태에 따라 뇌졸중이 어떻게 나타나는지 살펴본다.",
    tall=False,
)

# 1. 나이와 평균 혈당의 분포
section_head("dist", "나이와 평균 혈당의 분포", "전체 사람을 대상으로 값이 어느 구간에 많이 몰려 있는지 본다.")
c1, c2 = st.columns(2, gap="large")
with c1:
    chart_label("나이 (age)")
    fig = px.histogram(df, x="age", nbins=40, color_discrete_sequence=["#3a3b40"])
    fig.update_traces(hovertemplate="나이 %{x}<br>%{y:,}명<extra></extra>")
    fig.update_xaxes(title="나이")
    fig.update_yaxes(title="사람 수")
    show_fig(style_fig(fig))
with c2:
    chart_label("평균 혈당 (avg_glucose_level)")
    fig = px.histogram(df, x="avg_glucose_level", nbins=40, color_discrete_sequence=[BLUE])
    fig.update_traces(hovertemplate="혈당 %{x}<br>%{y:,}명<extra></extra>")
    fig.update_xaxes(title="평균 혈당")
    fig.update_yaxes(title="사람 수")
    show_fig(style_fig(fig))

# 2. 뇌졸중을 겪은 사람과 겪지 않은 사람 비교
section_head("compare", "뇌졸중을 겪은 사람과 겪지 않은 사람", "두 그룹의 나이와 평균 혈당을 상자그림으로 비교한다.")
group_colors = {GROUP_NO: GRAY, GROUP_YES: RED}
order = {"그룹": [GROUP_NO, GROUP_YES]}
c1, c2 = st.columns(2, gap="large")
with c1:
    chart_label("그룹별 나이")
    fig = px.box(df, x="그룹", y="age", color="그룹", color_discrete_map=group_colors, category_orders=order)
    fig.update_xaxes(title="")
    fig.update_yaxes(title="나이")
    show_fig(style_fig(fig))
with c2:
    chart_label("그룹별 평균 혈당")
    fig = px.box(df, x="그룹", y="avg_glucose_level", color="그룹", color_discrete_map=group_colors, category_orders=order)
    fig.update_xaxes(title="")
    fig.update_yaxes(title="평균 혈당")
    show_fig(style_fig(fig))

mean_table = (
    df.groupby("그룹")
    .agg(사람_수=("stroke", "size"), 평균_나이=("age", "mean"), 평균_혈당=("avg_glucose_level", "mean"))
    .reindex([GROUP_NO, GROUP_YES])
    .reset_index()
    .rename(columns={"사람_수": "사람 수", "평균_나이": "평균 나이", "평균_혈당": "평균 혈당"})
)
chart_label("그룹별 평균값")
st.dataframe(
    mean_table,
    hide_index=True,
    width="stretch",
    column_config={
        "사람 수": st.column_config.NumberColumn("사람 수 (명)", format="localized"),
        "평균 나이": st.column_config.NumberColumn("평균 나이 (세)", format="%.1f"),
        "평균 혈당": st.column_config.NumberColumn(format="%.1f"),
    },
)


# 3. 고혈압, 심장병 여부에 따른 뇌졸중 비율
def stroke_ratio_bar(column):
    table = df.groupby(column)["stroke"].agg(["size", "mean"]).reindex([0, 1])
    labels = ["없음", "있음"]
    rates = (table["mean"] * 100).round(1)
    fig = go.Figure(
        go.Bar(
            x=labels,
            y=rates,
            marker_color=[GRAY, RED],
            text=[f"{r:.1f}%" for r in rates],
            textposition="outside",
            customdata=table["size"],
            hovertemplate="%{x}<br>뇌졸중 비율 %{y:.1f}%<br>사람 수 %{customdata:,}명<extra></extra>",
            width=0.5,
        )
    )
    fig.update_yaxes(title="뇌졸중 비율 (%)", range=[0, max(rates) * 1.25])
    return style_fig(fig)


section_head("disease", "질환 여부에 따른 뇌졸중 비율", "고혈압과 심장병이 있는 사람과 없는 사람 가운데 뇌졸중을 겪은 사람의 비율이다.")
c1, c2 = st.columns(2, gap="large")
with c1:
    chart_label("고혈압 (hypertension)")
    show_fig(stroke_ratio_bar("hypertension"))
with c2:
    chart_label("심장병 (heart_disease)")
    show_fig(stroke_ratio_bar("heart_disease"))

# 4. bmi가 비어 있는 사람
section_head("bmi", "bmi가 비어 있는 사람", "bmi 값이 비어 있는 사람만 따로 세어 전체와 뇌졸중 비율을 견준다.")
missing = df[df["bmi"].isna()]
bmi_table = pd.DataFrame(
    {
        "구분": ["bmi가 비어 있는 사람", "전체"],
        "사람 수": [len(missing), total],
        "뇌졸중 겪은 사람 수": [int(missing["stroke"].sum()), n_stroke],
        "뇌졸중 비율": [missing["stroke"].mean() * 100 if len(missing) else 0, ratio],
    }
)
st.dataframe(
    bmi_table,
    hide_index=True,
    width="stretch",
    column_config={
        "사람 수": st.column_config.NumberColumn("사람 수 (명)", format="localized"),
        "뇌졸중 겪은 사람 수": st.column_config.NumberColumn("뇌졸중 겪은 사람 수 (명)", format="localized"),
        "뇌졸중 비율": st.column_config.NumberColumn(format="%.1f%%"),
    },
)

# 5. 흡연 상태별 사람 수
section_head("smoking", "흡연 상태별 사람 수", "smoking_status 열의 값마다 사람 수를 센다.")
smoke_table = df["smoking_status"].value_counts().rename_axis("흡연 상태").reset_index(name="사람 수")
st.dataframe(
    smoke_table,
    hide_index=True,
    width="stretch",
    column_config={"사람 수": st.column_config.NumberColumn("사람 수 (명)", format="localized")},
)

footer("탐색")
