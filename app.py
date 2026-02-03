import streamlit as st
import openai
import json

# ============================================================
# 1. 페이지 설정
# ============================================================
st.set_page_config(
    page_title="지문 3초 퀴즈 메이커 (수업 모드)",
    page_icon="👨‍🏫",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# 2. 세션 상태 초기화 (수업 모드를 위해 필수!)
# ============================================================
# 퀴즈 데이터 저장소
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = []
# 현재 몇 번 문제인지 (0번부터 시작)
if 'current_idx' not in st.session_state:
    st.session_state.current_idx = 0
# 수업 모드인지 아닌지 (False: 입력화면, True: 수업화면)
if 'class_mode' not in st.session_state:
    st.session_state.class_mode = False
# 정답을 보여줄지 말지
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False

# ============================================================
# 3. 유틸리티 함수 (JSON 파싱 & AI 호출)
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

# ============================================================
# 4. 화면 디자인 (CSS)
# ============================================================
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    /* 수업 모드 카드 */
    .class-card { background: white; border-radius: 20px; padding: 3rem; margin: 2rem auto; box-shadow: 0 10px 25px rgba(0,0,0,0.1); max-width: 900px; border-top: 8px solid #1e3a8a; }
    .class-question { font-size: 2.2rem; font-weight: 800; color: #1e3a8a; margin-bottom: 2rem; line-height: 1.4; }
    .class-option { font-size: 1.5rem; padding: 1.2rem; margin: 1rem 0; background: #f1f5f9; border-radius: 12px; color: #334155; border: 2px solid transparent; transition: all 0.3s; }
    .class-option:hover { border-color: #3b82f6; background: #e0f2fe; }
    .class-answer { background: #dcfce7 !important; border-color: #22c55e !important; color: #14532d !important; font-weight: bold; }
    .class-explanation { background: #eff6ff; padding: 1.5rem; border-radius: 12px; margin-top: 2rem; font-size: 1.2rem; line-height: 1.6; border-left: 5px solid #3b82f6; }
    
    /* 일반 모드 카드 */
    .quiz-card { background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(30, 58, 138, 0.1); border-left: 4px solid #1e3a8a; }
    .question-text { font-size: 1.1rem; font-weight: 600; }
    .correct-answer { background: #dcfce7; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# 5. 화면 구성 로직 (입력 모드 vs 수업 모드)
# ============================================================

# [A] 수업 모드 화면 (Presentation Mode)
if st.session_state.class_mode:
    # 상단 진행바
    quiz_data = st.session_state.quiz_data
    current = st.session_state.current_idx
    total = len(quiz_data)
    quiz = quiz_data[current]
    
    # 진행률 표시
    st.progress((current + 1) / total)
    st.markdown(f"<div style='text-align:right; color:#64748b;'>문제 {current + 1} / {total}</div>", unsafe_allow_html=True)

    # 문제 카드 표시
    st.markdown(f"""
    <div class="class-card">
        <div class="class-question">Q{current + 1}. {quiz['question']}</div>
    """, unsafe_allow_html=True)

    # 보기 표시
    for idx, option in enumerate(quiz['options']):
        # 정답 공개 상태이고, 이 보기가 정답이라면 스타일 적용
        if st.session_state.show_answer and idx == quiz['answer']:
            st.markdown(f'<div class="class-option class-answer">{idx + 1}. {option} (정답)</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="class-option">{idx + 1}. {option}</div>', unsafe_allow_html=True)

    # 정답 공개 상태라면 해설 표시
    if st.session_state.show_answer:
        st.markdown(f"""
        <div class="class-explanation">
            <strong>🎓 선생님의 해설:</strong><br>
            {quiz['explanation']}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True) # 카드 닫기

    # 하단 컨트롤 버튼 (3단 컬럼)
    c1, c2, c3 = st.columns([1, 2, 1])
    
    with c2:
        # 1. 아직 정답을 안 보여줬다면 -> [정답 확인] 버튼
        if not st.session_state.show_answer:
            if st.button("👀 정답 및 해설 확인하기", use_container_width=True, type="primary"):
                st.session_state.show_answer = True
                st.rerun()
        
        # 2. 정답을 보여줬다면 -> [다음 문제] 또는 [종료] 버튼
        else:
            if current < total - 1: # 다음 문제가 남음
                if st.button("다음 문제로 넘어가기 👉", use_container_width=True):
                    st.session_state.current_idx += 1
                    st.session_state.show_answer = False # 다음 문제는 정답 가리기
                    st.rerun()
            else: # 마지막 문제임
                if st.button("🎉 수업 종료하기 (첫 화면으로)", use_container_width=True, type="primary"):
                    st.session_state.class_mode = False
                    st.session_state.current_idx = 0
                    st.session_state.show_answer = False
                    st.rerun()

    # (비상구) 강제 종료 버튼
    with st.sidebar:
        if st.button("❌ 수업 강제 종료"):
            st.session_state.class_mode = False
            st.rerun()

# [B] 입력 및 생성 화면 (Setup Mode)
else:
    st.markdown('<h1 style="text-align:center; color:#1e3a8a;">📝 지문 3초 퀴즈 메이커</h1>', unsafe_allow_html=True)
    
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
        if st.button("🚀 퀴즈 생성하기", use_container_width=True, type="primary"):
            if not api_key:
                st.error("API 키를 입력해주세요.")
            elif len(text_input) < 10:
                st.warning("지문을 더 길게 입력해주세요.")
            else:
                with st.spinner("AI 선생님이 문제를 출제중입니다..."):
                    quiz_data = generate_real_quiz(text_input, difficulty, num_questions, api_key)
                    if quiz_data:
                        st.session_state.quiz_data = quiz_data
                        st.session_state.class_mode = False # 생성 직후엔 리스트 보여주기
                        st.success(f"{len(quiz_data)}문제 생성 완료!")
                        st.rerun()

    with right_col:
        st.markdown("### 📋 생성 결과 확인")
        
        # 퀴즈 데이터가 있으면 표시
        if st.session_state.quiz_data:
            # === [핵심] 수업 모드 진입 버튼 ===
            st.info("👇 수업 시간에 학생들에게 보여주려면 아래 버튼을 누르세요.")
            if st.button("👨‍🏫 수업 모드 시작하기 (큰 화면)", use_container_width=True, type="secondary"):
                st.session_state.class_mode = True
                st.session_state.current_idx = 0
                st.session_state.show_answer = False
                st.rerun()
            
            st.divider()
            
            # 기존 리스트 뷰 (선생님 확인용)
            for idx, quiz in enumerate(st.session_state.quiz_data, 1):
                with st.expander(f"문제 {idx}. {quiz['question'][:20]}..."):
                    st.write(f"**Q. {quiz['question']}**")
                    for i, opt in enumerate(quiz['options']):
                        if i == quiz['answer']:
                            st.write(f"- :green[{opt} (정답)]")
                        else:
                            st.write(f"- {opt}")
                    st.info(f"해설: {quiz['explanation']}")
        else:
            st.info("왼쪽에서 지문을 입력하고 생성 버튼을 눌러주세요.")
