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
if 'timer_started' not in st.session_state:
    st.session_state.timer_started = False
if 'timer_finished' not in st.session_state:
    st.session_state.timer_finished = False

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

def create_text_file(quiz_data, text_input):
    content = "📝 AI가 만든 지문 3초 퀴즈\n"
    content += "=" * 50 + "\n\n"
    content += "[지문 내용]\n"
    content += f"{text_input[:100]}...\n\n"
    content += "-" * 50 + "\n\n"
    
    content += "[학습지: 학생용]\n\n"
    for idx, quiz in enumerate(quiz_data, 1):
        content += f"Q{idx}. {quiz['question']}\n"
        for i, opt in enumerate(quiz['options']):
            content += f"  ({i+1}) {opt}\n"
        content += "\n"
    
    content += "=" * 50 + "\n\n"
    
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
    .class-card { background: white; border-radius: 20px; padding: 3rem; margin: 2rem auto; box-shadow: 0 10px 25px rgba(0,0,0,0.1); max-width: 1200px; border-top: 8px solid #1e3a8a; }
    .class-question { font-size: 2.2rem; font-weight: 800; color: #1e3a8a; margin-bottom: 2rem; line-height: 1.4; }
    .class-option { font-size: 1.5rem; padding: 1.2rem; margin: 1rem 0; background: #f1f5f9; border-radius: 12px; color: #334155; border: 2px solid transparent; transition: all 0.3s; }
    .class-option:hover { border-color: #3b82f6; background: #e0f2fe; }
    .class-answer { background: #dcfce7 !important; border-color: #22c55e !important; color: #14532d !important; font-weight: bold; }
    .class-explanation { background: #eff6ff; padding: 1.5rem; border-radius: 12px; margin-top: 2rem; font-size: 1.2rem; line-height: 1.6; border-left: 5px solid #3b82f6; }
    .quiz-card { background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(30, 58, 138, 0.1); border-left: 4px solid #1e3a8a; }
    .question-text { font-size: 1.1rem; font-weight: 600; }
    .correct-answer { background: #dcfce7; font-weight: 600; }
    .timer-box { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 15px; text-align: center; box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4); height: 100%; display: flex; flex-direction: column; justify-content: center; }
    .timer-text { font-size: 4rem; font-weight: bold; font-family: 'Courier New', monospace; }
    .timer-label { font-size: 1.2rem; margin-bottom: 1rem; opacity: 0.9; }
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

    st.markdown(f"""<div class="class-card">""", unsafe_allow_html=True)
    
    # === 문제와 타이머를 좌우로 배치 ===
    question_col, timer_col = st.columns([2, 1])
    
    with question_col:
        st.markdown(f"""<div class="class-question">Q{current + 1}. {quiz['question']}</div>""", unsafe_allow_html=True)
        
        # 선택지 표시 (타이머와 상관없이 항상 표시)
        for idx, option in enumerate(quiz['options']):
            if st.session_state.show_answer and idx == quiz['answer']:
                st.markdown(f'<div class="class-option class-answer">{idx + 1}. {option} (정답)</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="class-option">{idx + 1}. {option}</div>', unsafe_allow_html=True)

        if st.session_state.show_answer:
            st.markdown(f"""<div class="class-explanation"><strong>🎓 선생님의 해설:</strong><br>{quiz['explanation']}</div>""", unsafe_allow_html=True)
    
    with timer_col:
        # === 타이머 기능 (오른쪽 컬럼에 배치) ===
        if not st.session_state.timer_started and not st.session_state.show_answer:
            st.markdown("### ⏱️ 타이머 설정")
            timer_duration = st.selectbox("생각할 시간", [10, 20, 30, 45, 60], index=2, key=f"timer_{current}")
            if st.button("🚀 타이머 시작!", use_container_width=True, type="primary"):
                st.session_state[f"timer_duration_{current}"] = timer_duration
                st.session_state.timer_started = True
                st.rerun()
        
        # 타이머 진행 중
        elif st.session_state.timer_started and not st.session_state.timer_finished:
            timer_duration = st.session_state.get(f"timer_duration_{current}", 30)
            
            timer_placeholder = st.empty()
            progress_placeholder = st.empty()
            
            for remaining in range(timer_duration, 0, -1):
                timer_placeholder.markdown(f"""
                    <div class="timer-box">
                        <div class="timer-label">남은 시간</div>
                        <div class="timer-text">{remaining}</div>
                        <div style="font-size: 1rem; margin-top: 0.5rem;">초</div>
                    </div>
                """, unsafe_allow_html=True)
                progress_placeholder.progress((timer_duration - remaining) / timer_duration)
                time.sleep(1)
            
            # 타이머 종료
            timer_placeholder.markdown("""
                <div class="timer-box">
                    <div class="timer-text">⏰</div>
                    <div style="font-size: 1.5rem; margin-top: 1rem;">시간 종료!</div>
                </div>
            """, unsafe_allow_html=True)
            progress_placeholder.progress(1.0)
            st.session_state.timer_finished = True
            time.sleep(2)
            st.rerun()
        
        # 타이머 종료 후 표시
        elif st.session_state.timer_finished:
            st.markdown("""
                <div class="timer-box">
                    <div class="timer-text">✅</div>
                    <div style="font-size: 1.2rem; margin-top: 1rem;">타이머 완료</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

    # 버튼 영역
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
                    st.session_state.timer_started = False
                    st.session_state.timer_finished = False
                    st.rerun()
            else:
                if st.button("🎉 수업 종료하기 (첫 화면으로)", use_container_width=True, type="primary"):
                    st.session_state.class_mode = False
                    st.session_state.current_idx = 0
                    st.session_state.show_answer = False
                    st.session_state.timer_started = False
                    st.session_state.timer_finished = False
                    st.rerun()
    
    with st.sidebar:
        st.markdown("### ⚙️ 수업 설정")
        if st.button("⏭️ 타이머 건너뛰기"):
            st.session_state.timer_finished = True
            st.rerun()
        if st.button("🔄 타이머 초기화"):
            st.session_state.timer_started = False
            st.session_state.timer_finished = False
            st.rerun()
        if st.button("❌ 수업 강제 종료"):
            st.session_state.class_mode = False
            st.session_state.timer_started = False
            st.session_state.timer_finished = False
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
                        st.session_state.class_mode = False
                        st.success(f"{len(quiz_data)}문제 생성 완료!")
                        st.rerun()

    with right_col:
        st.markdown("### 📋 생성 결과 확인")
        
        if st.session_state.quiz_data:
            b1, b2 = st.columns(2)
            with b1:
                if st.button("👨‍🏫 수업 모드 시작", use_container_width=True, type="secondary"):
                    st.session_state.class_mode = True
                    st.session_state.current_idx = 0
                    st.session_state.show_answer = False
                    st.session_state.timer_started = False
                    st.session_state.timer_finished = False
                    st.rerun()
            with b2:
                txt_data = create_text_file(st.session_state.quiz_data, text_input)
                st.download_button(
                    label="💾 퀴즈 다운로드 (.txt)",
                    data=txt_data,
                    file_name="my_quiz.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            st.divider()
            
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
            st.info("�← 왼쪽에서 지문을 입력하고 생성 버튼을 눌러주세요.")
