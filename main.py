import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DATA_URL = "https://raw.githubusercontent.com/plugye980/stroke-data/refs/heads/main/stroke.csv"
RECORD_DIR = Path(__file__).parent / "내_기록"
RECORD_FILE = RECORD_DIR / "기록.json"

st.set_page_config(
    page_title="뇌졸중 예측 실습실",
    page_icon=":material/neurology:",
    layout="wide",
)


@st.cache_data
def load_data():
    return pd.read_csv(DATA_URL, encoding="utf-8")


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


def html(markup):
    st.markdown(markup, unsafe_allow_html=True)


def section_head(anchor, title, note=""):
    note_html = f'<p class="sec-note">{note}</p>' if note else ""
    html(f'<div class="sec-head" id="{anchor}"><h2 class="serif">{title}</h2>{note_html}</div>')


df = load_data()

if "record" not in st.session_state:
    st.session_state.record = load_record()
record = st.session_state.record

total = len(df)
n_cols = df.shape[1]
n_stroke = int((df["stroke"] == 1).sum())
ratio = n_stroke / total * 100 if total else 0

# 전체 스타일
html(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@200;300;400&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

:root {
    --bg: #111112;
    --panel: #1b1b1d;
    --line: rgba(255, 255, 255, 0.08);
    --text: #f2f2f0;
    --muted: #a3a3a8;
    --accent: #d8342b;
    --blue: #2f4fd1;
    --gutter: 4vw;
}

.stApp { background: var(--bg); }
[data-testid="stMain"], [data-testid="stAppViewBlockContainer"], [data-testid="stMainBlockContainer"] { padding-top: 0 !important; }
.block-container > div > div:first-child { margin-top: 0; }
header[data-testid="stHeader"] { display: none; }
.block-container {
    max-width: none;
    padding: 0 var(--gutter) 5rem;
}
.stApp, .stApp p, .stApp li, .stApp label { color: var(--text); font-family: 'Noto Sans KR', sans-serif; }
.serif { font-family: 'Noto Serif KR', serif !important; font-weight: 300 !important; letter-spacing: -0.03em; }
.icon {
    font-family: 'Material Symbols Rounded';
    font-weight: normal; font-style: normal; line-height: 1;
    display: inline-block; vertical-align: middle;
    -webkit-font-feature-settings: 'liga'; font-feature-settings: 'liga';
}

/* 히어로 */
.hero {
    position: relative;
    margin: -1rem calc(-1 * var(--gutter)) 0;
    min-height: clamp(560px, 82vh, 820px);
    padding: 0 var(--gutter) 3.5rem;
    background:
        radial-gradient(ellipse 70% 60% at 62% 30%, #a9acb2 0%, #7c7f86 30%, #45474c 62%, #1d1e20 100%);
    display: flex; flex-direction: column; justify-content: flex-end;
    overflow: hidden;
}
.nav {
    position: absolute; top: 1.1rem; left: var(--gutter); right: var(--gutter);
    display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem;
}
.nav-left { display: flex; align-items: center; gap: 2.2rem; flex-wrap: wrap; }
.logo { white-space: nowrap; display: flex; align-items: center; gap: .4rem; color: #fff; font-weight: 500; font-size: 1rem; }
.logo .icon { font-size: 1.4rem; }
.nav a { color: rgba(255,255,255,.85) !important; text-decoration: none; font-size: .82rem; }
.nav a:hover { color: #fff !important; }
.cta {
    background: #fff; border-radius: 4px; padding: .55rem .6rem .55rem .9rem;
    display: flex; align-items: center; gap: 2.5rem;
}
.cta .icon { color: #111; font-size: 1.6rem; }
.cta-btn {
    background: #111; color: #fff; border-radius: 4px; padding: .5rem .9rem;
    font-size: .8rem; white-space: nowrap;
}
.cta-btn .dim { color: #8d8d92; }
.hero-mark {
    position: absolute; right: 6vw; top: 50%; transform: translateY(-58%);
    font-size: clamp(14rem, 34vw, 30rem);
    background: linear-gradient(160deg, #ffffff 0%, #c9ccd2 35%, #6c6f75 70%, #2b2c2f 100%);
    -webkit-background-clip: text; background-clip: text; color: transparent;
    filter: drop-shadow(0 30px 40px rgba(0,0,0,.35));
    opacity: .9;
}
.hero h1 {
    position: relative; color: #fff; margin: 0; padding: 0;
    font-size: clamp(3rem, 7.5vw, 6.5rem); line-height: 1.08;
}
.hero-sub { position: relative; color: rgba(255,255,255,.8) !important; margin: 1.4rem 0 0; font-size: .95rem; }

/* 소개 섹션 */
.intro-title { color: var(--text); font-size: clamp(2rem, 3.4vw, 3rem); line-height: 1.18; margin: 2.2rem 0 1.2rem; }
.intro-text { color: var(--muted) !important; font-size: .95rem; line-height: 1.75; max-width: 30rem; }
.float-card { display: flex; flex-direction: column; gap: 6px; margin-bottom: 1.5rem; }
.float-card > div { background: #232325; border-radius: 10px; padding: 1rem 1.1rem; }
.float-card .fc-title { color: #fff; font-weight: 500; font-size: .95rem; }
.float-card .fc-body { color: #c9c9cc; font-size: .82rem; line-height: 1.6; }
.float-card .fc-body b { color: #fff; font-weight: 500; }

/* 숫자 타일 */
.tiles {
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 1rem 0 0;
}
.tile {
    position: relative; min-height: 15rem; border-radius: 18px; overflow: hidden;
    background: linear-gradient(180deg, #1f1f21 0%, #151516 100%);
    border: 1px solid var(--line);
    padding: 1.4rem;
    display: flex; flex-direction: column; justify-content: space-between;
}
.tile-num { color: #fff; font-size: clamp(2.4rem, 4vw, 3.6rem); line-height: 1; }
.tile-unit { font-size: .45em; color: var(--muted); margin-left: .2rem; }
.pill {
    align-self: flex-start;
    background: rgba(40, 40, 42, .9); color: #fff; border: 1px solid rgba(255,255,255,.1);
    border-radius: 999px; padding: .45rem .9rem; font-size: .78rem;
}
.tile.blue {
    background: radial-gradient(ellipse 90% 80% at 50% 0%, #4f6cf0 0%, #2a43b8 40%, #13205e 100%);
    border: none; border-top-left-radius: 120px;
}
.tile.red { background: linear-gradient(135deg, #e0412f 0%, #8f1b14 100%); border: none; }

/* 섹션 머리 */
.sec-head { margin: 5rem 0 1.2rem; display: flex; align-items: flex-end; justify-content: space-between; gap: 2rem; flex-wrap: wrap; }
.sec-head h2 { color: var(--text); font-size: clamp(1.9rem, 3vw, 2.7rem); margin: 0; padding: 0; line-height: 1.15; }
.sec-note { color: var(--muted) !important; font-size: .85rem; margin: 0; max-width: 26rem; }

/* 위젯 */
[data-testid="stDataFrame"], [data-testid="stDataEditor"] { border-radius: 12px; overflow: hidden; }
.stTextArea textarea { border-radius: 12px; min-height: 9rem; }

.footer { margin-top: 4rem; padding-top: 1.2rem; border-top: 1px solid var(--line);
    display: flex; justify-content: space-between; color: var(--muted); font-size: .78rem; }

@media (max-width: 900px) {
    .tiles { grid-template-columns: repeat(2, 1fr); }
    .tile { min-height: 11rem; }
    .tile { padding: 1rem; }
    .pill { font-size: .7rem; padding: .4rem .7rem; }
    .nav-links { display: none; }
    .hero-mark { right: -8vw; opacity: .5; }
}
@media (max-width: 520px) {
    :root { --gutter: 16px; }
    .cta { gap: .6rem; padding: .4rem; }
    .cta .icon, .cta-btn .dim { display: none; }
    .hero h1 { font-size: 2.6rem; }
}
</style>
"""
)

# 히어로 (상단 메뉴 + 큰 제목)
html(
    f"""
<div class="hero">
  <div class="nav">
    <div class="nav-left">
      <div class="logo"><span class="icon">neurology</span>뇌졸중 예측 실습실</div>
      <div class="nav-left nav-links">
        <a href="#data-intro">데이터 소개</a>
        <a href="#columns">열 정보</a>
        <a href="#preview">미리보기</a>
        <a href="#source">출처</a>
      </div>
    </div>
    <div class="cta">
      <span class="icon">monitor_heart</span>
      <div class="cta-btn">뇌졸중 발생 <span class="dim">stroke = 1</span> &nbsp;&bull;&nbsp; {ratio:.1f}%</div>
    </div>
  </div>
  <span class="icon hero-mark">neurology</span>
  <h1 class="serif">뇌졸중 예측<br>실습실</h1>
  <p class="hero-sub">건강 정보 {total:,}명의 기록으로 뇌졸중을 예측해 보는 실습 공간</p>
</div>
"""
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
            marker=dict(colors=["#2a2a2d", "#d8342b"], line=dict(color="#111112", width=3)),
            textinfo="none",
            hovertemplate="%{label}<br>%{value:,}명 (%{percent})<extra></extra>",
        )
    )
    fig.add_annotation(
        text=f"<span style='font-size:44px'>{ratio:.1f}%</span><br><span style='font-size:13px;color:#a3a3a8'>stroke = 1</span>",
        showarrow=False,
        font=dict(color="#f2f2f0", family="Noto Serif KR, serif"),
    )
    fig.update_layout(
        height=420,
        margin=dict(t=30, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.04, font=dict(color="#a3a3a8", size=12)),
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
  <div class="tile red"><div class="tile-num serif">{n_stroke:,}<span class="tile-unit" style="color:#ffd9d4">명</span></div><span class="pill">stroke가 1인 사람 수</span></div>
  <div class="tile blue"><div class="tile-num serif" style="text-align:right">{ratio:.1f}<span class="tile-unit" style="color:#c9d3ff">%</span></div><span class="pill">stroke가 1인 비율</span></div>
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

html('<div class="footer"><span>뇌졸중 예측 실습실</span><span>stroke.csv</span></div>')

# 변경 사항 저장
new_record = {"meanings": meanings, "source": source}
if new_record != record:
    save_record(new_record)
    st.session_state.record = new_record
