import streamlit as st
import openai
import json

# ============================================================
# 1. 페이지 설정
# ============================================================
st.set_page_config(
    page_title="지문 3초 퀴즈 메이커 (AI Ver.)",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# 2. API 키 입력 받기 (사이드바)
# ============================================================
with st.sidebar:
    st.header("🔐 설정")
    api_key = st.text_input("OpenAI API 키를 입력하세요", type="password")
    st.info("발급받은 sk-... 로 시작하는 키를 입력해주세요.")

# ============================================================
# 3. 진짜 AI 퀴즈 생성 함수 (ChatGPT 연결)
# ============================================================
def generate_real_quiz(text, difficulty, num_questions, api_key):
    client = openai.OpenAI(api_key=api_key)
    
    # AI에게 보낼 명령서 (프롬프트)
    prompt = f"""
    너는 현직 교사야. 아래 지문을 읽고 학생들을 위한 객관식 퀴즈를 만들어줘.
    
    [지문 내용]:
    {text}
    
    [조건]:
    1. 난이도: {difficulty}
    2. 문제 수: {num_questions}문제
    3. 결과는 반드시 JSON 형식으로만 출력해. 다른 말은 하지 마.
    
    [JSON 형식 예시]:
    [
        {{
            "question": "문제 내용",
            "options": ["보기1", "보기2", "보기3", "보기4"],
            "answer": 0, (정답 인덱스 0~3)
            "explanation": "해설 내용"
        }}
    ]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # 가성비 좋은 최신 모델
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"} # JSON 모드 강제
        )
        return json.loads(response.choices[0].message.content)['questions'] # 구조에 따라 조정 필요할 수 있음
    except Exception as e:
        # JSON 파싱 실패 시 예외 처리 (간단하게)
        try:
             return json.loads(response.choices[0].message.content)
        except:
             st.error(f"AI가 응답을 생성하지 못했습니다: {e}")
             return []

# ============================================================
# 4. 화면 디자인 (기존 CSS 유지)
# ============================================================
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .main-title { font-size: 2.5rem; font-weight: 700; color: #1e3a8a; text-align: center; margin-bottom: 0.5rem; }
    .sub-title { font-size: 1.1rem; color: #64748b; text-align: center; margin-bottom: 2rem; }
    .quiz-card { background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(30, 58, 138, 0.1); border-left: 4px solid #1e3a8a; }
    .question-number { color: #1e3a8a; font-weight: 700; font-size: 1.3rem; margin-bottom: 0.5rem; }
    .question-text { font-size: 1.1rem; font-weight: 600; color: #1e293b; margin-bottom: 1rem; line-height: 1.6; }
    .option { background: #f1f5f9; padding: 0.7rem 1rem; margin: 0.5rem 0; border-radius: 8px; font-size: 1rem; color: #334155; }
    .correct-answer { background: #dcfce7; border-left: 3px solid #22c55e; font-weight: 600; }
    .explanation { background: #eff6ff; padding: 1rem; border-radius: 8px; margin-top: 1rem; border-left: 3px solid #3b82f6; }
    .stButton>button { width: 100%; background-color: #1e3a8a; color: white; font-size: 1.1rem; font-weight: 600; padding: 0.7rem 1.5rem; border-radius: 8px; border: none; transition: all 0.3s; }
    .stButton>button:hover { background-color: #1e40af; box-shadow: 0 4px 12px rgba(30, 58, 138, 0.3); }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# 5. 메인 로직
# ============================================================
def main():
    st.markdown('<h1 class="main-title">📝 지문 3초 퀴즈 메이커 (AI Ver.)</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">지문을 입력하면 AI가 내용을 분석해 진짜 퀴즈를 만듭니다</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    left_col, right_col = st.columns([1, 1], gap="large")
    
    with left_col:
        st.markdown("### 📄 지문 입력")
        text_input = st.text_area("지문 텍스트를 입력하세요", placeholder="내용을 붙여넣으세요...", height=300)
        st.markdown("### ⚙️ 퀴즈 설정")
        col1, col2 = st.columns(2)
        with col1: difficulty = st.selectbox("난이도", ["하", "중", "상"], index=1)
        with col2: num_questions = st.selectbox("문항 수", [3, 5], index=0)
        st.markdown("<br>", unsafe_allow_html=True)
        generate_button = st.button("🚀 퀴즈 생성하기", use_container_width=True)
    
    with right_col:
        st.markdown("### 📋 생성된 퀴즈")
        if generate_button:
            if not api_key:
                st.error("🔐 왼쪽 사이드바(화살표)를 열어 API 키를 먼저 입력해주세요!")
            elif not text_input or len(text_input.strip()) < 10:
                st.warning("⚠️ 지문 텍스트를 최소 10자 이상 입력해주세요.")
            else:
                with st.spinner("AI가 지문을 읽고 문제를 출제 중입니다..."):
                    # 실제 AI 호출
                    try:
                        quiz_data = generate_real_quiz(text_input, difficulty, num_questions, api_key)
                        if quiz_data:
                            st.success(f"✅ AI가 {len(quiz_data)}개의 문제를 만들었습니다!")
                            # 퀴즈 표시 로직 (기존과 동일)
                            for idx, quiz in enumerate(quiz_data, 1):
                                st.markdown(f"""<div class="quiz-card"><div class="question-number">문제 {idx}</div><div class="question-text">{quiz['question']}</div>""", unsafe_allow_html=True)
                                for opt_idx, option in enumerate(quiz['options']):
                                    if opt_idx == quiz['answer']:
                                        st.markdown(f"""<div class="option correct-answer">{opt_idx + 1}. {option} ✓</div>""", unsafe_allow_html=True)
                                    else:
                                        st.markdown(f"""<div class="option">{opt_idx + 1}. {option}</div>""", unsafe_allow_html=True)
                                st.markdown(f"""<div class="explanation"><strong>💡 해설:</strong> {quiz['explanation']}</div></div>""", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()
