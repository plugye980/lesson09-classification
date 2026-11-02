import json
from pathlib import Path

import pandas as pd
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


df = load_data()

if "record" not in st.session_state:
    st.session_state.record = load_record()
record = st.session_state.record

# 제목과 소개
st.title(":material/neurology: 뇌졸중 예측 실습실")
st.write(
    "이 화면은 실습에 사용할 뇌졸중 데이터를 소개한다. "
    "한 줄은 한 사람의 정보이며, 성별·나이·고혈압·심장병·혈당·BMI·흡연 여부 등과 "
    "뇌졸중 발생 여부(stroke)가 기록되어 있다."
)

# 요약 숫자 카드
total = len(df)
n_cols = df.shape[1]
n_stroke = int((df["stroke"] == 1).sum())
ratio = n_stroke / total * 100 if total else 0

st.markdown(
    """
    <style>
    [data-testid="stMetric"] {
        background-color: rgba(64, 120, 192, 0.12);
        border-radius: 0.75rem;
        padding: 1rem 1.25rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("전체 사람 수", f"{total:,}명")
c2.metric("열 개수", f"{n_cols}개")
c3.metric("stroke가 1인 사람 수", f"{n_stroke:,}명")
c4.metric("stroke가 1인 비율", f"{ratio:.1f}%")

# 열 정보 표
st.subheader("열 정보")
st.caption("우리말 뜻 칸은 직접 채워 넣는다. 입력한 내용은 자동으로 저장된다.")

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
st.subheader("데이터 미리보기 (처음 다섯 줄)")
st.dataframe(df.head(5), hide_index=True, width="stretch")

# 데이터 출처
st.subheader("데이터 출처")
source = st.text_area(
    "출처",
    value=record.get("source", ""),
    placeholder="교재에 있는 데이터 출처를 적는다.",
    label_visibility="collapsed",
)

# 변경 사항 저장
new_record = {"meanings": meanings, "source": source}
if new_record != record:
    save_record(new_record)
    st.session_state.record = new_record
