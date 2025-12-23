import streamlit as st
from groq import Groq
import os
from datetime import datetime
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="🔮 AI 팩폭 점집",
    page_icon="🔮",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS 스타일 (게임 HP바 디자인 포함) ---
st.markdown("""
<style>
    /* 배경: 은은한 파스텔 움직임 */
    .stApp {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* 버튼 스타일 */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #FDBB2D 0%, #22C1C3 100%);
        border: none;
        color: white;
        padding: 15px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 30px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .stButton>button:hover {
        transform: scale(1.02);
    }

    /* 📸 결과 카드 스타일 */
    .result-card {
        background-color: white;
        border: 3px solid #333;
        border-radius: 20px;
        padding: 25px;
        margin-top: 20px;
        box-shadow: 10px 10px 0px rgba(0,0,0,0.15);
    }

    .card-header {
        font-size: 20px;
        font-weight: 800;
        color: #333;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* 🎮 HP 게이지 바 (디자인 요소) */
    .hp-container {
        width: 100%;
        background-color: #eee;
        border-radius: 10px;
        height: 20px;
        border: 2px solid #333;
        margin-bottom: 5px;
        overflow: hidden;
    }
    
    .hp-fill {
        height: 100%;
        transition: width 1s ease-in-out;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding-right: 5px;
        color: white;
        font-size: 11px;
        font-weight: bold;
    }

    /* 점수별 색상 */
    .hp-danger { background: #ff4757; } /* 빨강 */
    .hp-warning { background: #ffa502; } /* 주황 */
    .hp-good { background: #2ed573; }   /* 초록 */
    .hp-super { background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%); } /* 무지개 */

    .hp-text {
        text-align: right;
        font-size: 12px;
        font-weight: bold;
        color: #555;
        margin-bottom: 20px;
    }

    .card-body {
        font-size: 17px;
        line-height: 1.6;
        color: #444;
        font-weight: 500;
        white-space: pre-line;
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #eee;
    }

    .card-footer {
        margin-top: 15px;
        text-align: center;
        font-size: 12px;
        color: #888;
        font-weight: bold;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. API 설정 ---
api_key = os.environ.get("GROQ_API_KEY") 
if not api_key:
    st.error("⚠️ .env 파일에 GROQ_API_KEY가 없습니다.")
    st.stop()

client = Groq(api_key=api_key)

# --- 4. 메인 화면 ---
st.title("🔮 AI 팩폭 점집")
st.caption("내 운세 체력(HP)은 얼마일까?")

with st.form("fortune_form"):
    name = st.text_input("이름", placeholder="예: 김코딩")
    
    col1, col2 = st.columns(2)
    with col1:
        birth = st.date_input("생년월일", value=datetime(2000, 1, 1), min_value=datetime(1900, 1, 1))
    with col2:
        category = st.selectbox("고민 분야", ["💘 연애운", "💰 금전운", "🎓 학업/취업", "💣 인간관계"])
    
    worry = st.text_area("고민 (선택)", placeholder="요즘 너무 피곤해요...", height=80)
    
    st.write("")
    submitted = st.form_submit_button("⚡ 점괘 확인하기")

# --- 5. 결과 처리 ---
if submitted:
    if not name:
        st.warning("이름을 입력해주세요!")
    else:
        with st.spinner("🔮 신령님이 점괘를 뽑는 중..."):
            try:
                # 프롬프트 수정: 게임 용어 금지, 점수와 텍스트만 요구
                prompt = f"""
                너는 시니컬하고 직설적인 AI 점술가야.
                사용자의 고민을 듣고 운세 점수(0~100)와 조언을 줘.

                [규칙]
                1. 맨 첫 줄에는 무조건 '숫자'만 적어. (예: 75)
                2. 두 번째 줄부터 조언을 적어.
                3. 말투는 반말(친구처럼).
                4. 게임 용어(NPC, 퀘스트 등)는 절대 쓰지 마. 일상적인 말로 해.
                5. 팩트폭력으로 뼈를 때리지만, 마지막엔 현실적인 조언이나 행운템을 추천해줘.
                6. 길이는 3~4문장.
                7. 나이는 언급하지 말것
                8. 점수는 고민의 심각도에 따라 엄격하게 매겨.

                정보: 이름({name}), 생일({birth}), 주제({category}), 고민({worry})
                """

                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.1-8b-instant",
                    temperature=0.7,
                )
                
                full_text = completion.choices[0].message.content
                
                # --- 점수와 텍스트 분리 ---
                lines = full_text.strip().split('\n')
                try:
                    # 첫 줄에서 숫자만 추출
                    score = int(''.join(filter(str.isdigit, lines[0])))
                    # 나머지는 텍스트 (줄바꿈 다시 합치기)
                    result_text = "\n".join(lines[1:]).strip()
                except:
                    score = 50
                    result_text = full_text

                # 점수별 디자인 설정
                if score >= 90:
                    hp_class = "hp-super"
                    status_msg = "컨디션 최상! 🌈"
                elif score >= 70:
                    hp_class = "hp-good"
                    status_msg = "안전해요 💚"
                elif score >= 40:
                    hp_class = "hp-warning"
                    status_msg = "주의 필요 🧡"
                else:
                    hp_class = "hp-danger"
                    status_msg = "위험해요 🩸"

                # --- 결과 카드 생성 (HTML 문자열 조립) ---
                # 주의: f-string 안에서는 중괄호를 {{ }}로 써야 CSS등과 안 겹칩니다.
                html_card = f"""
                <div class="result-card">
                    <div class="card-header">
                        <span>👤 {name}</span>
                        <span>{category} 운세</span>
                    </div>
                    
                    <!-- 시각적 HP 바 -->
                    <div class="hp-container">
                        <div class="hp-fill {hp_class}" style="width: {score}%;">
                            {score}%
                        </div>
                    </div>
                    <div class="hp-text">
                        현재 상태: {status_msg}
                    </div>

                    <!-- 점괘 내용 -->
                    <div class="card-body">{result_text}</div>
                    
                    <div class="card-footer">
                         🔮 AI-FORTUNE.COM
                    </div>
                </div>
                """
                
                # 화면에 HTML 렌더링
                st.markdown(html_card, unsafe_allow_html=True)
                
                # 텍스트 복사 및 공유 버튼
                st.write("")
                col1, col2 = st.columns(2)
                with col1:
                    # 복사용 텍스트 제공
                    copy_text = f"[{name}님의 운세 HP: {score}%]\n{status_msg}\n\n{result_text}"
                    st.code(copy_text, language=None)
                with col2:
                    st.link_button("📸 인스타 올리기", "https://instagram.com")
                
                st.caption("👆 위 카드를 캡처해서 스토리에 올려보세요!")

            except Exception as e:
                st.error(f"에러 발생: {e}")