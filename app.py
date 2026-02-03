"""
지문 3초 퀴즈 메이커
선생님들을 위한 AI 기반 객관식 퀴즈 자동 생성 서비스

개발: Streamlit + Python
"""

import streamlit as st
import random

# ============================================================
# 페이지 설정 (반드시 최상단에 위치해야 함)
# ============================================================
st.set_page_config(
    page_title="지문 3초 퀴즈 메이커",
    page_icon="📝",
    layout="wide",  # 화면을 넓게 사용
    initial_sidebar_state="collapsed"  # 사이드바 숨김
)

# ============================================================
# 커스텀 CSS - 딥 블루 & 화이트 디자인
# ============================================================
st.markdown("""
    <style>
    /* 전체 배경 */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* 메인 타이틀 스타일 */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    /* 서브 타이틀 스타일 */
    .sub-title {
        font-size: 1.1rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* 퀴즈 카드 스타일 */
    .quiz-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(30, 58, 138, 0.1);
        border-left: 4px solid #1e3a8a;
    }
    
    /* 문제 번호 */
    .question-number {
        color: #1e3a8a;
        font-weight: 700;
        font-size: 1.3rem;
        margin-bottom: 0.5rem;
    }
    
    /* 문제 내용 */
    .question-text {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 1rem;
        line-height: 1.6;
    }
    
    /* 보기 스타일 */
    .option {
        background: #f1f5f9;
        padding: 0.7rem 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        font-size: 1rem;
        color: #334155;
    }
    
    /* 정답 표시 */
    .correct-answer {
        background: #dcfce7;
        border-left: 3px solid #22c55e;
        font-weight: 600;
    }
    
    /* 해설 박스 */
    .explanation {
        background: #eff6ff;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
        border-left: 3px solid #3b82f6;
    }
    
    /* 버튼 스타일 개선 */
    .stButton>button {
        width: 100%;
        background-color: #1e3a8a;
        color: white;
        font-size: 1.1rem;
        font-weight: 600;
        padding: 0.7rem 1.5rem;
        border-radius: 8px;
        border: none;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #1e40af;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.3);
    }
    
    /* 텍스트 영역 스타일 */
    .stTextArea>div>div>textarea {
        font-size: 1rem;
        border-radius: 8px;
        border: 2px solid #e2e8f0;
    }
    
    /* 선택 박스 스타일 */
    .stSelectbox>div>div>div {
        font-size: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# 더미 데이터 생성 함수
# (나중에 실제 AI API로 교체될 부분)
# ============================================================
def generate_dummy_quiz(text, difficulty, num_questions):
    """
    가상의 퀴즈 데이터를 생성하는 함수
    
    Args:
        text: 입력된 지문 텍스트
        difficulty: 난이도 (상/중/하)
        num_questions: 생성할 문제 개수
    
    Returns:
        list: 퀴즈 데이터 리스트
    """
    
    # 더미 퀴즈 템플릿 (실제로는 AI가 생성)
    dummy_questions = [
        {
            "question": "광합성 과정에서 식물이 흡수하는 기체는 무엇인가요?",
            "options": ["산소", "이산화탄소", "질소", "수소"],
            "answer": 1,  # 인덱스 (0부터 시작)
            "explanation": "식물은 광합성 과정에서 이산화탄소를 흡수하고 산소를 방출합니다."
        },
        {
            "question": "다음 중 재생 에너지가 아닌 것은?",
            "options": ["태양광", "풍력", "석탄", "조력"],
            "answer": 2,
            "explanation": "석탄은 화석 연료로, 재생이 불가능한 에너지원입니다."
        },
        {
            "question": "물의 끓는점은 섭씨 몇 도인가요?",
            "options": ["0도", "50도", "100도", "150도"],
            "answer": 2,
            "explanation": "표준 대기압에서 물은 섭씨 100도에서 끓습니다."
        },
        {
            "question": "지구에서 가장 큰 대륙은 어디인가요?",
            "options": ["아프리카", "아시아", "유럽", "북아메리카"],
            "answer": 1,
            "explanation": "아시아는 면적과 인구 모두 세계에서 가장 큰 대륙입니다."
        },
        {
            "question": "빛의 삼원색이 아닌 것은?",
            "options": ["빨강", "초록", "파랑", "노랑"],
            "answer": 3,
            "explanation": "빛의 삼원색은 빨강(Red), 초록(Green), 파랑(Blue)입니다."
        }
    ]
    
    # 요청한 문제 개수만큼 랜덤 선택
    selected_questions = random.sample(dummy_questions, min(num_questions, len(dummy_questions)))
    
    return selected_questions

# ============================================================
# 퀴즈 렌더링 함수
# ============================================================
def display_quiz(quiz_data):
    """
    생성된 퀴즈를 카드 형태로 깔끔하게 표시하는 함수
    
    Args:
        quiz_data: 퀴즈 데이터 리스트
    """
    for idx, quiz in enumerate(quiz_data, 1):
        # 퀴즈 카드 시작
        st.markdown(f"""
        <div class="quiz-card">
            <div class="question-number">문제 {idx}</div>
            <div class="question-text">{quiz['question']}</div>
        """, unsafe_allow_html=True)
        
        # 보기 표시
        for opt_idx, option in enumerate(quiz['options']):
            # 정답인 경우 하이라이트
            if opt_idx == quiz['answer']:
                st.markdown(f"""
                <div class="option correct-answer">
                    {opt_idx + 1}. {option} ✓
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="option">
                    {opt_idx + 1}. {option}
                </div>
                """, unsafe_allow_html=True)
        
        # 해설 표시
        st.markdown(f"""
            <div class="explanation">
                <strong>💡 해설:</strong> {quiz['explanation']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# 메인 애플리케이션
# ============================================================
def main():
    # 헤더
    st.markdown('<h1 class="main-title">📝 지문 3초 퀴즈 메이커</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">지문을 입력하면 AI가 자동으로 퀴즈를 만들어드립니다</p>', unsafe_allow_html=True)
    
    # 구분선
    st.markdown("---")
    
    # 좌/우 2개 컬럼으로 화면 분할
    left_col, right_col = st.columns([1, 1], gap="large")
    
    # ============================================================
    # 왼쪽 컬럼: 입력 영역
    # ============================================================
    with left_col:
        st.markdown("### 📄 지문 입력")
        
        # 텍스트 입력 영역
        text_input = st.text_area(
            label="지문 텍스트를 입력하세요",
            placeholder="교과서 내용, 뉴스 기사, 설명문 등 어떤 텍스트든 붙여넣으세요...",
            height=300,
            help="입력한 지문을 바탕으로 퀴즈가 생성됩니다."
        )
        
        st.markdown("### ⚙️ 퀴즈 설정")
        
        # 옵션 선택을 위한 2개 컬럼
        opt_col1, opt_col2 = st.columns(2)
        
        with opt_col1:
            difficulty = st.selectbox(
                "난이도 선택",
                options=["하", "중", "상"],
                index=1,  # 기본값: 중
                help="퀴즈의 난이도를 선택하세요"
            )
        
        with opt_col2:
            num_questions = st.selectbox(
                "문항 수",
                options=[3, 5],
                index=0,  # 기본값: 3문제
                help="생성할 퀴즈 문항 수를 선택하세요"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 퀴즈 생성 버튼
        generate_button = st.button("🚀 퀴즈 생성하기", use_container_width=True)
    
    # ============================================================
    # 오른쪽 컬럼: 결과 영역
    # ============================================================
    with right_col:
        st.markdown("### 📋 생성된 퀴즈")
        
        # 버튼 클릭 시 퀴즈 생성
        if generate_button:
            # 입력 검증
            if not text_input or len(text_input.strip()) < 10:
                st.warning("⚠️ 지문 텍스트를 최소 10자 이상 입력해주세요.")
            else:
                # 로딩 스피너 표시
                with st.spinner("퀴즈를 생성하는 중입니다... 잠시만 기다려주세요!"):
                    # 퀴즈 생성 (현재는 더미 데이터)
                    quiz_data = generate_dummy_quiz(text_input, difficulty, num_questions)
                
                # 성공 메시지
                st.success(f"✅ {num_questions}개의 퀴즈가 생성되었습니다!")
                
                # 퀴즈 표시
                display_quiz(quiz_data)
                
                # 다운로드 버튼 (추가 기능)
                st.markdown("<br>", unsafe_allow_html=True)
                st.info("💾 향후 업데이트: 퀴즈를 PDF나 워드 파일로 다운로드할 수 있는 기능이 추가될 예정입니다.")
        
        else:
            # 초기 안내 메시지
            st.info("👈 왼쪽에서 지문을 입력하고 '퀴즈 생성하기' 버튼을 눌러주세요.")
    
    # ============================================================
    # 하단 푸터
    # ============================================================
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #64748b; font-size: 0.9rem;">
        💙 선생님들의 수업을 위한 <strong>지문 3초 퀴즈 메이커</strong> | 
        개발: Streamlit + Python (AI 연동 예정)
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# 애플리케이션 실행
# ============================================================
if __name__ == "__main__":
    main()
