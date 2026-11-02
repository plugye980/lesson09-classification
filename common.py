import pandas as pd
import streamlit as st

DATA_URL = "https://raw.githubusercontent.com/plugye980/stroke-data/refs/heads/main/stroke.csv"

INK = "#141416"
MUTED = "#6b6b70"
GRAY = "#c9c9ce"
RED = "#d8342b"
BLUE = "#2f4fd1"
FONT = "Noto Sans KR, sans-serif"


@st.cache_data
def load_data():
    return pd.read_csv(DATA_URL, encoding="utf-8")


def html(markup):
    st.markdown(markup, unsafe_allow_html=True)


def section_head(anchor, title, note=""):
    note_html = f'<p class="sec-note">{note}</p>' if note else ""
    html(f'<div class="sec-head" id="{anchor}"><h2 class="serif">{title}</h2>{note_html}</div>')


def chart_label(text):
    html(f'<p class="chart-label">{text}</p>')


def style_fig(fig, height=360):
    fig.update_layout(
        height=height,
        margin=dict(t=20, b=50, l=64, r=10),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(family=FONT, color=INK, size=13),
        showlegend=False,
        bargap=0.08,
    )
    fig.update_xaxes(automargin=True, showgrid=False, linecolor="#d9d9de", ticks="outside", tickcolor="#d9d9de")
    fig.update_yaxes(automargin=True, gridcolor="#eeeef1", zeroline=False)
    return fig


def show_fig(fig):
    st.plotly_chart(fig, config={"displayModeBar": False}, theme=None)


def hero(links, page_link, ratio, title, sub, tall=True):
    link_html = "".join(f'<a href="{href}" target="_self">{label}</a>' for label, href in links)
    page_label, page_href = page_link
    size_class = "" if tall else " hero-short"
    mark = '<span class="icon hero-mark">neurology</span>' if tall else ""
    html(
        f"""
<div class="hero{size_class}">
  <div class="nav">
    <div class="nav-left">
      <a class="logo" href="./" target="_self"><span class="icon">neurology</span>뇌졸중 예측 실습실</a>
      <a class="nav-page" href="{page_href}" target="_self">{page_label}</a>
      <div class="nav-left nav-links">{link_html}</div>
    </div>
    <div class="cta">
      <span class="icon">monitor_heart</span>
      <div class="cta-btn">뇌졸중 발생 <span class="dim">stroke = 1</span> &nbsp;&bull;&nbsp; {ratio:.1f}%</div>
    </div>
  </div>
  {mark}
  <h1 class="serif">{title}</h1>
  <p class="hero-sub">{sub}</p>
</div>
"""
    )


def footer(right):
    html(f'<div class="footer"><span>뇌졸중 예측 실습실</span><span>{right}</span></div>')


def inject_style():
    html(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@200;300;400&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

:root {
    --bg: #ffffff;
    --soft: #f3f3f5;
    --line: rgba(0, 0, 0, 0.08);
    --text: #141416;
    --muted: #6b6b70;
    --gutter: 4vw;
}

.stApp { background: var(--bg); }
header[data-testid="stHeader"] { display: none; }
[data-testid="stMain"], [data-testid="stMainBlockContainer"], [data-testid="stAppViewBlockContainer"] { padding-top: 0 !important; }
.block-container { max-width: none; padding: 0 var(--gutter) 5rem; }
.stApp, .stApp p, .stApp li, .stApp label { color: var(--text); font-family: 'Noto Sans KR', sans-serif; }
.serif { font-family: 'Noto Serif KR', serif !important; font-weight: 300 !important; letter-spacing: -0.03em; }
.icon {
    font-family: 'Material Symbols Rounded';
    font-weight: normal; font-style: normal; line-height: 1;
    display: inline-block; vertical-align: middle;
    -webkit-font-feature-settings: 'liga'; font-feature-settings: 'liga';
}

/* 히어로 (어두운 영역) */
.hero {
    position: relative;
    margin: -1rem calc(-1 * var(--gutter)) 0;
    min-height: clamp(560px, 82vh, 820px);
    padding: 0 var(--gutter) 3.5rem;
    background: radial-gradient(ellipse 70% 60% at 62% 30%, #a9acb2 0%, #7c7f86 30%, #45474c 62%, #1d1e20 100%);
    display: flex; flex-direction: column; justify-content: flex-end;
    overflow: hidden;
}
.hero.hero-short { min-height: 360px; }
.nav {
    position: absolute; top: 1.1rem; left: var(--gutter); right: var(--gutter);
    display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem;
}
.nav-left { display: flex; align-items: center; gap: 2.2rem; flex-wrap: wrap; }
.nav a { color: rgba(255,255,255,.85) !important; text-decoration: none; font-size: .82rem; }
.nav a:hover { color: #fff !important; }
.nav a.logo { white-space: nowrap; display: flex; align-items: center; gap: .4rem; color: #fff !important; font-weight: 500; font-size: 1rem; }
.logo .icon { font-size: 1.4rem; }
.nav a.nav-page { color: #fff !important; border: 1px solid rgba(255,255,255,.4); border-radius: 999px; padding: .3rem .85rem; white-space: nowrap; }
.nav a.nav-page:hover { background: rgba(255,255,255,.12); }
.cta {
    background: #fff; border-radius: 4px; padding: .55rem .6rem .55rem .9rem;
    display: flex; align-items: center; gap: 2.5rem;
}
.cta .icon { color: #111; font-size: 1.6rem; }
.cta-btn { background: #111; color: #fff; border-radius: 4px; padding: .5rem .9rem; font-size: .8rem; white-space: nowrap; }
.cta-btn .dim { color: #8d8d92; }
.hero-mark {
    position: absolute; right: 6vw; top: 50%; transform: translateY(-58%);
    font-size: clamp(14rem, 34vw, 30rem);
    background: linear-gradient(160deg, #ffffff 0%, #c9ccd2 35%, #6c6f75 70%, #2b2c2f 100%);
    -webkit-background-clip: text; background-clip: text; color: transparent;
    filter: drop-shadow(0 30px 40px rgba(0,0,0,.35));
    opacity: .9;
}
.hero h1 { position: relative; color: #fff; margin: 0; padding: 0; font-size: clamp(3rem, 7.5vw, 6.5rem); line-height: 1.08; }
.hero-sub { position: relative; color: rgba(255,255,255,.8) !important; margin: 1.4rem 0 0; font-size: .95rem; }

/* 소개 영역 */
.intro-title { color: var(--text); font-size: clamp(2rem, 3.4vw, 3rem); line-height: 1.18; margin: 2.2rem 0 1.2rem; }
.intro-text { color: var(--muted) !important; font-size: .95rem; line-height: 1.75; max-width: 30rem; }
.float-card { display: flex; flex-direction: column; gap: 6px; margin-bottom: 1.5rem; }
.float-card > div { background: var(--soft); border-radius: 10px; padding: 1rem 1.1rem; }
.float-card .fc-title { color: var(--text); font-weight: 500; font-size: .95rem; }
.float-card .fc-body { color: #4a4a4f; font-size: .82rem; line-height: 1.6; }
.float-card .fc-body b { color: var(--text); font-weight: 500; }

/* 숫자 타일 */
.tiles { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 1rem 0 0; }
.tile {
    position: relative; min-height: 15rem; border-radius: 18px; overflow: hidden;
    background: var(--soft); padding: 1.4rem;
    display: flex; flex-direction: column; justify-content: space-between;
}
.tile-num { color: var(--text); font-size: clamp(2.4rem, 4vw, 3.6rem); line-height: 1; }
.tile-unit { font-size: .45em; color: var(--muted); margin-left: .2rem; }
.pill {
    align-self: flex-start; white-space: nowrap;
    background: #fff; color: var(--text); border: 1px solid var(--line);
    border-radius: 999px; padding: .45rem .9rem; font-size: .78rem;
}
.tile.red { background: linear-gradient(135deg, #e0412f 0%, #8f1b14 100%); }
.tile.blue {
    background: radial-gradient(ellipse 90% 80% at 50% 0%, #4f6cf0 0%, #2a43b8 40%, #13205e 100%);
    border-top-left-radius: 120px;
}
.tile.red .tile-num, .tile.blue .tile-num { color: #fff; }
.tile.red .tile-unit { color: #ffd9d4; }
.tile.blue .tile-unit { color: #c9d3ff; }
.tile.red .pill, .tile.blue .pill { background: rgba(0,0,0,.28); color: #fff; border-color: rgba(255,255,255,.18); }

/* 섹션 머리 */
.sec-head { margin: 5rem 0 1.2rem; display: flex; align-items: flex-end; justify-content: space-between; gap: 2rem; flex-wrap: wrap; }
.sec-head h2 { color: var(--text); font-size: clamp(1.9rem, 3vw, 2.7rem); margin: 0; padding: 0; line-height: 1.15; }
.sec-note { color: var(--muted) !important; font-size: .85rem; margin: 0; max-width: 26rem; }
.chart-label { color: var(--muted) !important; font-size: .85rem; margin: 0 0 .2rem; }

/* 위젯 */
[data-testid="stDataFrame"], [data-testid="stDataEditor"] { border-radius: 12px; overflow: hidden; }
.stTextArea textarea { border-radius: 12px; min-height: 9rem; }

.footer { margin-top: 4rem; padding-top: 1.2rem; border-top: 1px solid var(--line);
    display: flex; justify-content: space-between; color: var(--muted); font-size: .78rem; }

@media (max-width: 900px) {
    .tiles { grid-template-columns: repeat(2, 1fr); }
    .tile { min-height: 11rem; padding: 1rem; }
    .pill { font-size: .7rem; padding: .4rem .7rem; }
    .nav-links { display: none; }
    .hero-mark { right: -8vw; opacity: .5; }
}
@media (max-width: 520px) {
    :root { --gutter: 16px; }
    .cta { gap: .6rem; padding: .4rem; }
    .cta .icon, .cta-btn .dim { display: none; }
    .nav-left { gap: .8rem; }
    .nav a.logo { font-size: .9rem; }
    .hero h1 { font-size: 2.6rem; }
}
</style>
"""
    )
