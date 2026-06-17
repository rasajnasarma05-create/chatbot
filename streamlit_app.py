import streamlit as st
from google import genai
from google.genai import types
import os
from pypdf import PdfReader

# ==========================================
# 1. PREMIUM LAW SCHOOL VISUAL THEMING
# ==========================================
st.set_page_config(page_title="ClassroomBuddy AI", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    h1, h2, h3, h4, .stSubheader, p, label, .stMarkdown, div[data-baseweb="select"] {
        color: #1A1A1A !important;
        font-family: 'Helvetica Neue', Arial, sans-serif;
    }
    h1 { font-family: 'Georgia', serif; font-weight: bold; color: #4B0082 !important; }
    button[data-baseweb="tab"] { font-weight: 900 !important; color: #2D2D2D !important; font-size: 16px !important; }
    button[aria-selected="true"] { color: #4B0082 !important; border-bottom-color: #D4AF37 !important; }
    div.stButton > button:first-child { background-color: #4B0082 !important; color: #FFFFFF !important; border: 2px solid #D4AF37 !important; border-radius: 6px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Secure Master Key Extraction
try:
    MASTER_API_KEY = str(st.secrets["GEMINI_MASTER_KEY"]).strip().replace('"', '').replace("'", "")
except Exception:
    MASTER_API_KEY = ""

# ==========================================
# 2. PERSISTENT INSTITUTIONAL REGISTRY GATE
# ==========================================
@st.cache_resource
def get_persistent_user_database():
    return {
        "akshaya": "law2029",
        "megha": "gitam2026",
        "rasajna": "buddy2026"
    }

USER_DATABASE = get_persistent_user_database()

if "active_user" not in st.session_state: st.session_state.active_user = None
if "user_session_vault" not in st.session_state: st.session_state.user_session_vault = {}
if "current_active_topic" not in st.session_state: st.session_state.current_active_topic = "General Study Session"
if "quiz_sheet_cache" not in st.session_state: st.session_state.quiz_sheet_cache = None

if st.session_state.active_user is None:
    st.title("🎓 ClassroomBuddy AI")
    st.subheader("Law School Authentication Hub")
    auth_tab1, auth_tab2 = st.tabs(["🔒 Student Login", "📝 Registration"])
    
    with auth_tab1:
        username_entry = st.text_input("Username / Roll Number").lower().strip()
        password_entry = st.text_input("Password", type="password")
        if st.button("Authenticate Login"):
            if username_entry in USER_DATABASE and USER_DATABASE[username_entry] == password_entry:
                st.session_state.active_user = username_entry
                if username_entry not in st.session_state.user_session_vault:
                    st.session_state.user_session_vault[username_entry] = {"General Study Session": []}
                st.rerun()
            else: st.error("Invalid credentials.")
    st.stop()

st.title("🎓 ClassroomBuddy AI")
st.caption(f"Secure Institutional Workspace Node | Session Account: {st.session_state.active_user.upper()}")

if st.session_state.active_user not in st.session_state.user_session_vault:
    st.session_state.user_session_vault[st.session_state.active_user] = {"General Study Session": []}

with st.sidebar:
    st.header("Control Panel")
    st.info("🛡️ Server Infrastructure Fully Operational.")
    research_mode_active = st.toggle("Research Mode (Live Google Search Grounding)", value=True)
    
    user_threads = st.session_state.user_session_vault[st.session_state.active_user]
    st.session_state.current_active_topic = st.selectbox("Select Chat Topic", list(user_threads.keys()))

tab1, tab2, tab3, tab4 = st.tabs(["💬 Ask Me Anything Legal", "⚖️ Case Scenario Analyser", "🏛️ Jurisprudence Scholar", "🎯 Quiz"])

# --- TAB 1: ASK ME ANYTHING LEGAL ---
with tab1:
    st.subheader("Ask Me Anything Legal")
    tab1_file_upload = st.file_uploader("Upload reference documents context (PDF):", type=["pdf"])
    
    active_chat_log = st.session_state.user_session_vault[st.session_state.active_user][st.session_state.current_active_topic]
    for msg in active_chat_log:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
    text_chat_input = st.chat_input("Query legal concepts or codes...")
    if text_chat_input:
        active_chat_log.append({"role": "user", "content": text_chat_input})
        st.rerun()
        
    if active_chat_log and active_chat_log[-1]["role"] == "user":
        unresolved_user_prompt = active_chat_log[-1]["content"]
        if not MASTER_API_KEY: st.warning("Master Key configuration missing from deployment dashboard.")
        else:
            with st.chat_message("assistant"):
                text_stream_block = st.empty()
                try:
                    client = genai.Client(api_key=MASTER_API_KEY)
                    
                    system_instructions = (
                        "You are ClassroomBuddy AI, an advanced general legal consultant. "
                        "When analyzing Indian criminal law, you are STRICTLY FORBIDDEN from using legacy IPC/CrPC sections. "
                        "You must prioritize the Bharatiya Nyaya Sanhita (BNS, 2023), BNSS, and BSA provisions first. Provide double-verified answers."
                    )
                    
                    config = {"system_instruction": system_instructions}
                    if research_mode_active: config["tools"] = [{"google_search": {}}]
                        
                    api_call_response = client.models.generate_content(
                        model='gemini-2.5-flash', contents=unresolved_user_prompt, config=types.GenerateContentConfig(**config)
                    )
                    final_response_payload = api_call_response.text
                    
                    if research_mode_active and hasattr(api_call_response, 'candidates') and api_call_response.candidates:
                        try:
                            grounding_data = api_call_response.candidates[0].grounding_metadata
                            if grounding_data and hasattr(grounding_data, 'grounding_chunks'):
                                final_response_payload += "\n\n---\n### 🌐 Live Verification Research Reference Anchors:\n"
                                for web_chunk in grounding_data.grounding_chunks:
                                    if hasattr(web_chunk, 'web') and web_chunk.web:
                                        final_response_payload += f"- [{web_chunk.web.title}]({web_chunk.web.uri})\n"
                        except Exception: pass
                        
                    text_stream_block.markdown(final_response_payload)
                    active_chat_log.append({"role": "assistant", "content": final_response_payload})
                except Exception as loop_error: st.error(f"Engine connection exception: {str(loop_error)}")