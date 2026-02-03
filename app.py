import streamlit as st
import openai
import json
import time

# ============================================================
# 1. 페이지 설정
# ============================================================
st.set_page_config(
    page_title="지문 3초 퀴즈 메이커 (Full Ver.)",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# 2. 세션 상태 초기화
# ============================================================
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = []
if 'current_idx' not in st.session_state:
    st.session_state.current_idx = 0
if 'class_mode' not in st.session_state:
    st.session_state.class_mode = False
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False

# ============================================================
# 3. 유틸리티 함수 (파싱, AI호출, 다운로드 파일 생성)
# ============================================================
def safe_parse_quiz(response_text):
    try:
        data = json.loads(response_text)
        if isinstance(data, dict) and "questions" in data:
            return data["questions"]
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
        return []
    except Exception as e:
        return []

def generate_real_quiz(text, difficulty, num_questions, api_key):
    client = openai.OpenAI(api_key=api_key)
    prompt = f"""
    너는 선생님을 돕는 AI야. 아래 지문을 읽고 객관식 퀴즈를 만들어줘.
    [지문]: {text}
    [조건]:
    1. 난이도: {difficulty}
    2. 문제 수: {num_questions}개
    3. JSON 형식으로만 출력.
    [형식]: {{"questions": [{{"question": "...", "options": ["..."], "answer": 0, "explanation": "..."}}]}}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return safe_parse_quiz(response.choices[0].message.content)
    except Exception as e:
        st.error(f"오류: {e}")
        return []

# [NEW] 텍스트 파일 생성 함수
def create_text_file(quiz_data, text_input):
    content = "📝 AI가 만든 지문 3초 퀴즈\n"
    content += "=" * 50 + "\n\n"
    content += "[지문 내용]\n"
    content += f"{text_input[:100]}...\n\n" # 지문 앞부분만 살짝
    content += "-" * 50 + "\n\n"
    
    # 문제 부분
    content += "[학습지: 학생용]\n\n"
    for idx, quiz in enumerate(quiz_data, 1):
        content += f"Q{idx}. {quiz['question']}\n"
        for i, opt in enumerate(quiz['options']):
            content += f"  ({i+1}) {opt}\n"
        content += "\n"
    
    content += "=" * 50 + "\n\n"
    
    # 정답 부분
    content += "[정답 및 해설: 교사용]\n\n"
    for idx, quiz in enumerate(quiz_data, 1):
        content += f"{idx}번 정답: {quiz['answer'] + 1}번\n"
        content += f"해설: {quiz['explanation']}\n\n"
        
    return content

# ============================================================
# 4. 화면 디자인 (CSS)
# ============================================================
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .class-card { background: white; border-radius: 20px; padding: 3rem; margin: 2rem auto; box-shadow: 0 10px 25px rgba(0,0,0,0.1); max-width: 900px; border-top: 8px solid #1e3a8a; }
    .class-question { font-size: 2.2rem; font-weight: 800; color: #1e3a8a; margin-bottom: 2rem; line-height: 1.4; }
    .class-option { font-size: 1.5rem; padding: 1.2rem; margin: 1rem 0; background: #f1f5f9; border-radius: 12px; color: #334155; border: 2px solid transparent; transition: all 0.3s; }
    .class-option:hover { border-color: #3b82f6; background: #e0f2fe; }
    .class-answer { background: #dcfce7 !important; border-color: #22c55e !important; color: #14532d !important; font-weight: bold; }
    .class-explanation { background: #eff6ff; padding: 1.5rem; border-radius: 12px; margin-top: 2rem; font-size: 1.2rem; line-height: 1.6; border-left: 5px solid #3b82f6; }
    .quiz-card { background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(30, 58, 138, 0.1); border-left: 4px solid #1e3a8a; }
    .question-text { font-size: 1.1rem; font-weight: 600; }
    .correct-answer { background: #dcfce7; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# 5. 메인 로직
# ============================================================

# [A] 수업 모드 화면
if st.session_state.class_mode:
    quiz_data = st.session_state.quiz_data
    current = st.session_state.current_idx
    total = len(quiz_data)
    quiz = quiz_data[current]
    
    st.progress((current + 1) / total)
    st.markdown(f"<div style='text-align:right; color:#64748b;'>문제 {current + 1} / {total}</div>", unsafe_allow_html=True)

    st.markdown(f"""<div class="class-card"><div class="class-question">Q{current + 1}. {quiz['question']}</div>""", unsafe_allow_html=True)

    for idx, option in enumerate(quiz['options']):
        if st.session_state.show_answer and idx == quiz['answer']:
            st.markdown(f'<div class="class-option class-answer">{idx + 1}. {option} (정답)</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="class-option">{idx + 1}. {option}</div>', unsafe_allow_html=True)

    if st.session_state.show_answer:
        st.markdown(f"""<div class="class-explanation"><strong>🎓 선생님의 해설:</strong><br>{quiz['explanation']}</div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if not st.session_state.show_answer:
            if st.button("👀 정답 및 해설 확인하기", use_container_width=True, type="primary"):
                st.session_state.show_answer = True
                st.rerun()
        else:
            if current < total - 1:
                if st.button("다음 문제로 넘어가기 👉", use_container_width=True):
                    st.session_state.current_idx += 1
                    st.session_state.show_answer = False
                    st.rerun()
            else:
                if st.button("🎉 수업 종료하기 (첫 화면으로)", use_container_width=True, type="primary"):
                    st.session_state.class_mode = False
                    st.session_state.current_idx = 0
                    st.session_state.show_answer = False
                    st.rerun()
    
    with st.sidebar:
        if st.button("❌ 수업 강제 종료"):
            st.session_state.class_mode = False
            st.rerun()

# [B] 입력 및 생성 화면
else:
    st.markdown('<h1 style="text-align:center; color:#1e3a8a;">🎓 지문 3초 퀴즈 메이커</h1>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("🔐 설정")
        api_key = st.text_input("OpenAI API 키", type="password")

    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.markdown("### 📄 지문 입력")
        text_input = st.text_area("내용 입력", height=300)
        c1, c2 = st.columns(2)
        with c1: difficulty = st.selectbox("난이도", ["하", "중", "상"], index=1)
        with c2: num_questions = st.selectbox("문항 수", [3, 5], index=0)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button
