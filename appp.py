import streamlit as st
from groq import Groq
import os
import time
from dotenv import load_dotenv
import streamlit.components.v1 as components

load_dotenv()

st.set_page_config(
    page_title="현생 RPG 상태창",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');

    header {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}

    .stApp {
        background-color: #050510;
        background-image: 
            linear-gradient(rgba(0, 255, 255, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 255, 0.05) 1px, transparent 1px);
        background-size: 50px 50px;
        font-family: 'Orbitron', sans-serif;
        color: #e0e0e0; 
    }

    .stTextInput label, .stTextArea label {
        color: #ffffff !important; 
        font-weight: bold;
        text-shadow: 0 0 5px rgba(0, 243, 255, 0.5); 
        font-size: 14px;
    }

    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #0f0f1a; 
        color: #00f3ff; 
        border: 1px solid #58a6ff;
        border-radius: 5px;
        font-family: 'Orbitron', sans-serif;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #ff00de;
        box-shadow: 0 0 10px #ff00de;
    }

    .stButton>button {
        width: 100%;
        background: black;
        color: #ff00de;
        border: 2px solid #ff00de;
        padding: 15px;
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        font-size: 20px;
        text-transform: uppercase;
        box-shadow: 0 0 10px #ff00de, inset 0 0 10px #ff00de;
        transition: 0.2s;
        border-radius: 0px;
        clip-path: polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px);
    }
    .stButton>button:hover {
        background-color: #ff00de;
        color: white;
        box-shadow: 0 0 30px #ff00de;
    }

    .ad-box {
        background: #111;
        border: 2px dashed #ffd700;
        color: #ffd700;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
        border-radius: 10px;
        animation: blink 1.5s infinite;
    }
    @keyframes blink { 50% { border-color: #555; } }

    .status-window {
        background: rgba(15, 20, 35, 0.95); 
        border: 2px solid #00f3ff;
        padding: 25px;
        margin-top: 20px;
        position: relative;
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.3);
        clip-path: polygon(20px 0, 100% 0, 100% calc(100% - 20px), calc(100% - 20px) 100%, 0 100%, 0 20px);
    }
    .scanline {
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(to bottom, rgba(255,255,255,0), rgba(255,255,255,0) 50%, rgba(0,0,0,0.1) 50%, rgba(0,0,0,0.1)); 
        background-size: 100% 4px;
        pointer-events: none;
        z-index: 10;
        opacity: 0.4;
    }
    .window-header { display: flex; justify-content: space-between; border-bottom: 1px dashed #00f3ff; padding-bottom: 10px; margin-bottom: 20px; font-size: 12px; color: #00f3ff; text-shadow: 0 0 5px #00f3ff; letter-spacing: 2px; }
    .char-container { display: flex; align-items: center; gap: 20px; margin-bottom: 30px; }
    .char-avatar-box { width: 80px; height: 80px; border: 2px solid #ff00de; display: flex; align-items: center; justify-content: center; font-size: 50px; background: rgba(255, 0, 222, 0.1); box-shadow: 0 0 15px #ff00de; }
    .char-details { flex-grow: 1; }
    .char-name { font-size: 28px; font-weight: 900; color: #fff; text-shadow: 2px 2px 0px #ff00de; line-height: 1.2; }
    .char-job { font-size: 16px; color: #f2cc60; text-shadow: 0 0 5px #f2cc60; margin-top: 5px; }
    .stat-row { display: flex; align-items: center; margin-bottom: 15px; font-family: 'Orbitron', sans-serif; }
    .stat-label { width: 50px; font-size: 14px; font-weight: bold; color: #fff; }
    .stat-track { flex-grow: 1; height: 18px; background: #222; border: 1px solid #444; margin: 0 10px; position: relative; transform: skewX(-15deg); }
    .stat-fill { height: 100%; box-shadow: 0 0 10px currentColor; transition: width 1s; }
    .stat-val { width: 40px; text-align: right; font-weight: bold; color: #fff; text-shadow: 0 0 5px #fff; }
    .skill-box { border: 1px solid #00f3ff; background: rgba(0, 243, 255, 0.05); padding: 15px; margin-top: 25px; position: relative; }
    .skill-label { position: absolute; top: -10px; left: 10px; background: #050510; padding: 0 10px; color: #00f3ff; font-size: 12px; font-weight: bold; }
    
    .desc-text { 
        color: #e0e0e0; 
        font-size: 14px; 
        line-height: 1.6; 
        margin-top: 20px; 
        padding: 10px; 
        border-left: 3px solid #ff00de; 
        background: linear-gradient(90deg, rgba(255,0,222,0.1), transparent); 
    }
    
    ::placeholder {
        color: #aaaaaa !important; 
        opacity: 1; 
        font-weight: normal;
    }        

    .footer { margin-top: 20px; text-align: right; font-size: 10px; color: #888; }
</style>
""", unsafe_allow_html=True)

api_key = os.environ.get("GROQ_API_KEY") 
if not api_key:
    st.error("⚠️ .env 파일 설정을 확인해주세요.")
    st.stop()

client = Groq(api_key=api_key)

st.title("현생 RPG 상태창")
st.markdown("<div style='color:#ccc; margin-bottom:20px; text-shadow:0 0 5px #00f3ff;'>SYSTEM: 플레이어 스캔 준비 완료...</div>", unsafe_allow_html=True)

with st.form("game_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("PLAYER ID (닉네임)", placeholder="홍길동")
    with col2:
        mbti = st.text_input("CLASS (MBTI)", placeholder="ENFP")
    
    hobby = st.text_input("QUEST (취미/특기)", placeholder="유튜브 정주행, 롤 하기")
    worry = st.text_area("DEBUFF (현재 고민)", placeholder="돈 부족, 만성 피로...", height=80)
    
    st.write("")
    submitted = st.form_submit_button("INITIALIZE (시작)")

if submitted:
    if not name:
        st.warning("ERROR: 닉네임이 입력되지 않았습니다.")
    else:
        ad_placeholder = st.empty()
        
        kakao_ad_code = """
        <ins class="kakao_ad_area" style="display:none;"
        data-ad-unit =기         data-ad-unit =                 닉네임:{name}, MBTI:{mbti}, 취미:{hobby}, 고민:{worry}

                [출력 형식]
                직업: (웃긴 미래지향적 직업명)
                칭호: (별명)
                체력: (0~100 숫자)
                멘탈: (0~100 숫자)
                행운: (0~100 숫자)
                자금: (0~100 숫자)
                스킬명: (스킬 이름)
                스킬설명: (스킬 효과 한 줄)
                설명: (3줄 요약 팩폭)
                """

                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.1-8b-instant",
                    temperature=0.8,
                )
                
                result = completion.choices[0].message.content
                
                # 데이터 파싱
                def get_val(key):
                    for line in result.split('\n'):
                        if line.strip().startswith(key):
                            return line.split(':', 1)[1].strip().replace('"', '').replace("'", "").replace(",", "")
                    return "UNKNOWN"
                
                def get_num(key):
                    try:
                        import re
                        return int(re.search(r'\d+', get_val(key)).group())
                    except:
                        return 50

                job = get_val("직업")
                title = get_val("칭호")
                skill_name = get_val("스킬명")
                skill_desc = get_val("스킬설명")
                desc = get_val("설명")
                
                hp = get_num("체력")
                mp = get_num("멘탈")
                luck = get_num("행운")
                gold = get_num("자금")

                avatar = "🤖"
                if "E" in mbti.upper(): avatar = "⚡"
                if "F" in mbti.upper(): avatar = "❤️"

                final_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
                    <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
                    <style>
                        body {{ background-color: transparent; margin: 0; padding: 10px; font-family: 'Orbitron', sans-serif; overflow: hidden; }}
                        .status-window {{
                            background: rgba(15, 20, 35, 0.95); 
                            border: 2px solid #00f3ff;
                            padding: 25px;
                            position: relative;
                            box-shadow: 0 0 20px rgba(0, 243, 255, 0.3);
                            color: #e0e0e0;
                            max-width: 400px;
                            margin: 0 auto;
                            clip-path: polygon(20px 0, 100% 0, 100% calc(100% - 20px), calc(100% - 20px) 100%, 0 100%, 0 20px);
                        }}
                        .window-header {{ display: flex; justify-content: space-between; border-bottom: 1px dashed #00f3ff; padding-bottom: 10px; margin-bottom: 20px; font-size: 12px; color: #00f3ff; text-shadow: 0 0 5px #00f3ff; letter-spacing: 2px; }}
                        .char-container {{ display: flex; align-items: center; gap: 20px; margin-bottom: 30px; }}
                        .char-avatar-box {{ width: 80px; height: 80px; border: 2px solid #ff00de; display: flex; align-items: center; justify-content: center; font-size: 40px; background: rgba(255, 0, 222, 0.1); box-shadow: 0 0 15px #ff00de; color: #fff; }}
                        .char-details {{ flex-grow: 1; }}
                        .char-name {{ font-size: 24px; font-weight: 900; color: #fff; text-shadow: 2px 2px 0px #ff00de; line-height: 1.2; margin: 0; }}
                        .char-job {{ font-size: 14px; color: #f2cc60; text-shadow: 0 0 5px #f2cc60; margin-top: 5px; }}
                        .stat-row {{ display: flex; align-items: center; margin-bottom: 12px; }}
                        .stat-label {{ width: 50px; font-size: 12px; font-weight: bold; color: #fff; }}
                        .stat-track {{ flex-grow: 1; height: 15px; background: #222; border: 1px solid #444; margin: 0 10px; transform: skewX(-15deg); }}
                        .stat-fill {{ height: 100%; transition: width 1s; }}
                        .stat-val {{ width: 30px; text-align: right; font-weight: bold; color: #fff; font-size: 12px; }}
                        .skill-box {{ border: 1px solid #00f3ff; background: rgba(0, 243, 255, 0.05); padding: 15px; margin-top: 20px; position: relative; }}
                        .skill-label {{ position: absolute; top: -10px; left: 10px; background: #050510; padding: 0 10px; color: #00f3ff; font-size: 10px; font-weight: bold; }}
                        .desc-text {{ 
                            color: #ddd; font-size: 12px; line-height: 1.5; margin-top: 20px; padding: 10px; 
                            border-left: 3px solid #ff00de; background: linear-gradient(90deg, rgba(255,0,222,0.1), transparent); 
                        }}
                        .footer {{ margin-top: 15px; text-align: right; font-size: 9px; color: #666; }}
                        
                        /* 버튼 스타일 */
                        .btn-group {{ margin-top: 20px; text-align: center; display: flex; gap: 10px; justify-content: center; }}
                        .action-btn {{
                            background: #000; color: #fff; border: 1px solid #fff; padding: 10px 20px;
                            font-family: 'Orbitron', sans-serif; cursor: pointer; font-size: 12px;
                            text-decoration: none; display: inline-block;
                        }}
                        .save-btn {{ border-color: #00f3ff; color: #00f3ff; }}
                        .insta-btn {{ border-color: #ff00de; color: #ff00de; }}
                    </style>
                </head>
                <body>
                    
                    <!-- 캡처 대상 영역 -->
                    <div id="capture_area" class="status-window">
                        <div class="window-header">
                            <span>SYSTEM_STATUS: <span style="color:#0f0;">NORMAL</span></span>
                            <span>v.1.0.3</span>
                        </div>
                        <div class="char-container">
                            <div class="char-avatar-box">{avatar}</div>
                            <div class="char-details">
                                <div class="char-name">{name}</div>
                                <div class="char-job">{job}</div>
                                <div style="font-size:10px; color:#ccc; margin-top:5px;">TITLE: [{title}]</div>
                            </div>
                        </div>
                        
                        <div class="stat-row">
                            <div class="stat-label" style="color:#ff0055;">HP</div>
                            <div class="stat-track"><div class="stat-fill" style="width:{hp}%; background:#ff0055; box-shadow:0 0 10px #ff0055;"></div></div>
                            <div class="stat-val">{hp}</div>
                        </div>
                        <div class="stat-row">
                            <div class="stat-label" style="color:#00f3ff;">MP</div>
                            <div class="stat-track"><div class="stat-fill" style="width:{mp}%; background:#00f3ff; box-shadow:0 0 10px #00f3ff;"></div></div>
                            <div class="stat-val">{mp}</div>
                        </div>
                        <div class="stat-row">
                            <div class="stat-label" style="color:#bd00ff;">LUCK</div>
                            <div class="stat-track"><div class="stat-fill" style="width:{luck}%; background:#bd00ff; box-shadow:0 0 10px #bd00ff;"></div></div>
                            <div class="stat-val">{luck}</div>
                        </div>
                         <div class="stat-row">
                            <div class="stat-label" style="color:#ffd700;">GOLD</div>
                            <div class="stat-track"><div class="stat-fill" style="width:{gold}%; background:#ffd700; box-shadow:0 0 10px #ffd700;"></div></div>
                            <div class="stat-val">{gold}</div>
                        </div>

                        <div class="skill-box">
                            <div class="skill-label">ACTIVE SKILL</div>
                            <div style="color:#fff; font-weight:bold; font-size:14px;">⚡ {skill_name}</div>
                            <div style="font-size:11px; color:#ccc; margin-top:5px;">{skill_desc}</div>
                        </div>
                        
                        <div class="desc-text">{desc}</div>
                        <div class="footer">GENERATED BY ai-rpg.streamlit.app</div>
                    </div>

                    <!-- 버튼 영역 (캡처 안됨) -->
                    <div class="btn-group">
                        <button class="action-btn save-btn" onclick="downloadImage()">💾 이미지 저장</button>
                        <a href="https://www.instagram.com/create/story" target="_blank" class="action-btn insta-btn">📸 인스타 열기</a>
                    </div>

                    <script>
                        function downloadImage() {{
                            const element = document.getElementById("capture_area");
                            html2canvas(element, {{
                                backgroundColor: null,
                                scale: 2 
                            }}).then(canvas => {{
                                const link = document.createElement('a');
                                link.download = 'my_rpg_status.png';
                                link.href = canvas.toDataURL();
                                link.click();
                            }});
                        }}
                    </script>
                </body>
                </html>
                """
                
                components.html(final_html, height=750)
                components.html(kakao_ad_code, height=120)
                st.info("💡 '이미지 저장' 후 '인스타 열기'를 눌러 스토리에 올려보세요!")
                copy_text = f"🕹️ [현생 RPG 상태창]\nID: {name} / 직업: {job}\n스킬: {skill_name}\n\n#현생RPG #AI상태창"
                st.code(copy_text, language=None)

                

            except Exception as e:
                st.error(f"SYSTEM ERROR: {e}")
