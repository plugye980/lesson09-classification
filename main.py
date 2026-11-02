import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from common import FONT, INK, MUTED, RED, footer, hero, html, inject_style, load_data, section_head

RECORD_DIR = Path(__file__).parent / "내_기록"
RECORD_FILE = RECORD_DIR / "기록.json"

st.set_page_config(
    page_title="뇌졸중 예측 실습실",
    page_icon=":material/neurology:",
    layout="wide",
)


def load_record():
    if RECORD_FILE.exists():
        try:
            return json.loads(RECORD_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"meanings": {}, "source": ""}


def save_record(record):
    RECORD_DIR.mkdir(parents=True, exist_ok=True)
    RECORD_FILE.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")


df = load_data()

if "record" not in st.session_state:
    st.session_state.record = load_record()
record = st.session_state.record

total = len(df)
n_cols = df.shape[1]
n_stroke = int((df["stroke"] == 1).sum())
ratio = n_stroke / total * 100 if total else 0

inject_style()

# 히어로 (상단 메뉴 + 큰 제목)
hero(
    links=[
        ("데이터 소개", "#data-intro"),
        ("열 정보", "#columns"),
        ("미리보기", "#preview"),
        ("출처", "#source"),
    ],
    page_link=("탐색", "탐색"),
    ratio=ratio,
    title="뇌졸중 예측<br>실습실",
    sub=f"건강 정보 {total:,}명의 기록으로 뇌졸중을 예측해 보는 실습 공간",
)

# 데이터 소개 (왼쪽 제목 / 가운데 그림 / 오른쪽 설명 카드)
left, mid, right = st.columns([1.05, 1.3, 0.9], gap="large", vertical_alignment="bottom")

with left:
    html(
        """
<div id="data-intro">
  <h2 class="serif intro-title">이 데이터는<br>무엇을 담고 있나</h2>
  <p class="intro-text">한 줄은 한 사람의 정보다. 성별, 나이, 고혈압과 심장병 여부, 결혼 여부,
  직업 형태, 거주 지역, 평균 혈당, BMI, 흡연 상태와 함께
  뇌졸중 발생 여부(stroke)가 기록되어 있다.</p>
</div>
"""
    )

with mid:
    fig = go.Figure(
        go.Pie(
            labels=["뇌졸중 없음 (0)", "뇌졸중 발생 (1)"],
            values=[total - n_stroke, n_stroke],
            hole=0.72,
            sort=False,
            direction="clockwise",
            marker=dict(colors=["#e6e6e9", RED], line=dict(color="#ffffff", width=3)),
            textinfo="none",
            hovertemplate="%{label}<br>%{value:,}명 (%{percent})<extra></extra>",
        )
    )
    fig.add_annotation(
        text=f"<span style='font-size:44px'>{ratio:.1f}%</span><br><span style='font-size:13px;color:{MUTED}'>stroke = 1</span>",
        showarrow=False,
        font=dict(color=INK, family="Noto Serif KR, serif"),
    )
    fig.update_layout(
        height=420,
        margin=dict(t=30, b=10, l=10, r=10),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(family=FONT),
        showlegend=True,
        legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.04, font=dict(color=MUTED, size=12)),
    )
    st.plotly_chart(fig, config={"displayModeBar": False}, theme=None)

with right:
    html(
        f"""
<div class="float-card">
  <div class="fc-title">stroke 열은 맞혀야 할 정답이다</div>
  <div class="fc-body">0은 뇌졸중이 없었던 사람, 1은 뇌졸중이 있었던 사람이다.
  전체 {total:,}명 가운데 <b>{n_stroke:,}명</b>만 1이어서, 두 값의 비율이 크게 기울어 있다.
  bmi 열에는 <b>{int(df['bmi'].isna().sum()):,}개</b>의 빈 값이 있다.</div>
</div>
"""
    )

# 큰 숫자 카드 네 개
html(
    f"""
<div class="tiles">
  <div class="tile"><div class="tile-num serif">{total:,}<span class="tile-unit">명</span></div><span class="pill">전체 사람 수</span></div>
  <div class="tile"><div class="tile-num serif">{n_cols}<span class="tile-unit">개</span></div><span class="pill">열 개수</span></div>
  <div class="tile red"><div class="tile-num serif">{n_stroke:,}<span class="tile-unit">명</span></div><span class="pill">stroke가 1인 사람 수</span></div>
  <div class="tile blue"><div class="tile-num serif" style="text-align:right">{ratio:.1f}<span class="tile-unit">%</span></div><span class="pill">stroke가 1인 비율</span></div>
</div>
"""
)

# 열 정보 표
section_head("columns", "열 정보", "우리말 뜻 칸은 교재를 보고 직접 채워 넣는다. 입력한 내용은 자동으로 저장된다.")

if "column_base" not in st.session_state:
    st.session_state.column_base = pd.DataFrame(
        {
            "열 이름": df.columns,
            "우리말 뜻": [record["meanings"].get(c, "") for c in df.columns],
            "값의 종류": [int(df[c].nunique()) for c in df.columns],
            "빈 값 개수": [int(df[c].isna().sum()) for c in df.columns],
        }
    )

edited = st.data_editor(
    st.session_state.column_base,
    key="column_editor",
    hide_index=True,
    width="stretch",
    height=(len(df.columns) + 1) * 35 + 3,
    disabled=["열 이름", "값의 종류", "빈 값 개수"],
    column_config={
        "우리말 뜻": st.column_config.TextColumn("우리말 뜻", help="교재를 보고 직접 채워 넣는다."),
    },
)

meanings = {
    row["열 이름"]: ("" if pd.isna(row["우리말 뜻"]) else str(row["우리말 뜻"]))
    for _, row in edited.iterrows()
}

# 데이터 미리보기
section_head("preview", "처음 다섯 줄", "불러온 데이터를 손대지 않고 그대로 보여 준다.")
st.dataframe(df.head(5), hide_index=True, width="stretch")

# 데이터 출처
section_head("source", "데이터 출처", "교재에 적힌 출처를 옮겨 적는다. 입력한 내용은 자동으로 저장된다.")
source = st.text_area(
    "출처",
    value=record.get("source", ""),
    placeholder="교재에 있는 데이터 출처를 적는다.",
    label_visibility="collapsed",
)

footer("stroke.csv")

# 변경 사항 저장
new_record = {"meanings": meanings, "source": source}
if new_record != record:
    save_record(new_record)
    st.session_state.record = new_record
