import streamlit as st
import openai
import json

# ============================================================
# 1. 페이지 설정
# ============================================================
st.set_page_config(
    page_title="지문 3초 퀴즈 메이커 (Final)",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# 2. 안전한 JSON 파싱 함수 (이게 해결사입니다! 🦸‍♂️)
# ============================================================
def safe_parse_quiz(response_text):
    try:
        data = json.loads(response_text)
        
        # Case 1: {"questions": [...]} 형태로 온 경우
        if isinstance(data, dict) and "questions" in data:
            return data["questions"]
        
        # Case 2: [...] 리스트 형태로 온 경우
        if isinstance(data, list):
            return data
            
        # Case 3: 퀴즈가 1개라서 단일 { ... } 객체로 온 경우 -> 리스트로 포장
        if isinstance(data, dict):
            return [data]
            
        return []
    except Exception as e:
        print(f"JSON 파싱 오류: {e}")
        return []

# ============================================================
# 3. 진짜 AI 퀴즈 생성 함수
# ============================================================
def generate_real_quiz(text, difficulty, num_questions, api_key):
    client = openai.OpenAI(api_key=api_key)
    
    prompt = f"""
    너는 선생님을 돕는 AI야. 아래 지문을 읽고 객관식 퀴즈를 만들어줘.
    
    [지문]:
    {text}
    
    [조건]:
    1. 난이도: {difficulty}
    2. 문제 수: {num_questions}개
    3. 결과는 반드시 아래와 같은 'JSON 형식'으로만 출력해. (군더더기 설명 금지)
    
    [JSON 형식 예시]:
    {{
        "questions": [
            {{
                "question": "문제 내용",
                "options": ["보기1", "보기2", "보기3", "보기4"],
                "answer": 0,
                "explanation": "해설 내용"
            }}
        ]
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        # 만능 파서로 안전하게 변환
        return safe_parse_quiz(response.choices[0].message.content)
        
    except Exception as e:
        st.error(f"AI 호출 중 오류 발생: {e}")
        return []

# ============================================================
# 4. 화면 디자인 (CSS)
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
    
    # 사이드바에서 API 키 입력
    with st.sidebar:
        st.header("🔐 설정")
        api_key = st.text_input("OpenAI API 키", type="password", help="sk-로 시작하는 키를 입력하세요")
    
    left_col, right_col = st.columns([1, 1], gap="large")
    
    with left_col:
        st.markdown("### 📄 지문 입력")
        text_input = st.text_area("지문 텍스트를 입력하세요", placeholder="내용을 붙여넣으세요... (최소 10자 이상)", height=300)
        st.markdown("### ⚙️ 퀴즈 설정")
        col1, col2 = st.columns(2)
        with col1: difficulty = st.selectbox("난이도", ["하", "중", "상"], index=1)
        with col2: num_questions = st.selectbox("문항 수", [1, 3, 5], index=1)
        st.markdown("<br>", unsafe_allow_html=True)
        generate_button = st.button("🚀 퀴즈 생성하기", use_container_width=True)
    
    with right_col:
        st.markdown("### 📋 생성된 퀴즈")
        if generate_button:
            if not api_key:
                st.error("🔐 왼쪽 사이드바를 열어 API 키를 먼저 입력해주세요!")
            elif not text_input or len(text_input.strip()) < 10:
                st.warning("⚠️ 지문 텍스트를 좀 더 길게 입력해주세요.")
            else:
                with st.spinner("AI가 지문을 읽고 문제를 출제 중입니다..."):
                    quiz_data = generate_real_quiz(text_input, difficulty, num_questions, api_key)
                    
                    if quiz_data:
                        st.success(f"✅ AI가 {len(quiz_data)}개의 문제를 만들었습니다!")
                        for idx, quiz in enumerate(quiz_data, 1):
                            st.markdown(f"""<div class="quiz-card"><div class="question-number">문제 {idx}</div><div class="question-text">{quiz.get('question', '문제 없음')}</div>""", unsafe_allow_html=True)
                            
                            options = quiz.get('options', [])
                            answer_idx = quiz.get('answer', 0)
                            
                            for opt_idx, option in enumerate(options):
                                if opt_idx == answer_idx:
                                    st.markdown(f"""<div class="option correct-answer">{opt_idx + 1}. {option} ✓</div>""", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"""<div class="option">{opt_idx + 1}. {option}</div>""", unsafe_allow_html=True)
                            
                            st.markdown(f"""<div class="explanation"><strong>💡 해설:</strong> {quiz.get('explanation', '해설 없음')}</div></div>""", unsafe_allow_html=True)
                    else:
                        st.error("AI가 문제를 생성하지 못했습니다. 잠시 후 다시 시도해주세요.")

if __name__ == "__main__":
    main()
