import streamlit as st
from google import genai
from google.genai import types
import os
from pypdf import PdfReader

# ==========================================
# 1. PREMIUM PRESENTATION DESIGN THEMING (CSS)
# ==========================================
st.set_page_config(page_title="ClassroomBuddy AI", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    /* Premium Color Identity Palette */
    .stApp { background-color: #F4F7F9; }
    
    h1, h2, h3, h4, .stSubheader, p, label, .stMarkdown {
        color: #0A192F !important;
        font-family: 'Helvetica Neue', Arial, sans-serif;
    }
    
    /* Interactive Tarot Flip Cards Animation System */
    .tarot-container {
        display: flex;
        justify-content: space-between;
        gap: 10px;
        margin-bottom: 20px;
    }
    .tarot-card {
        background: #FFFFFF;
        border: 2px solid #00B4D8;
        border-radius: 10px;
        width: 19%;
        padding: 15px;
        text-align: center;
        box-shadow: 0px 4px 8px rgba(0,0,0,0.05);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .tarot-card:hover {
        transform: translateY(-5px);
        border-color: #FF9F1C;
        background-color: #F0FDFA;
    }
    .tarot-title {
        font-family: 'Georgia', serif;
        font-weight: bold;
        color: #0A192F;
        font-size: 16px;
        border-bottom: 2px solid #FF9F1C;
        padding-bottom: 5px;
        margin-bottom: 8px;
    }
    .tarot-theory {
        font-size: 12px;
        color: #4A5568;
        font-style: italic;
    }
    
    /* Input Container Bar Modifications */
    .chat-wrapper {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Global Tab Buttons UI Adjustments */
    button[data-baseweb="tab"] {
        font-weight: 800 !important;
        color: #0A192F !important;
        background-color: #E2E8F0 !important;
        border-radius: 6px 6px 0px 0px;
        padding: 10px 16px !important;
    }
    button[aria-selected="true"] {
        background-color: #00B4D8 !important;
        color: #FFFFFF !important;
    }
    
    /* Minimalist Action Arrow Elements */
    div.stButton > button:first-child {
        background-color: #FF9F1C !important;
        color: #0A192F !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 50% !important;
        width: 42px !important;
        height: 42px !important;
        font-size: 18px !important;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Secure direct master key stripping sequence configuration
try:
    MASTER_API_KEY = str(st.secrets["GEMINI_MASTER_KEY"]).strip().replace('"', '').replace("'", "")
except Exception:
    MASTER_API_KEY = ""

# Global Registry File Setup Cache
if "master_user_db" not in st.session_state:
    st.session_state.master_user_db = {
        "rasajna": "buddy2026",
        "megha": "gitam2026",
        "akshaya": "law2029"
    }

if "active_user" not in st.session_state: st.session_state.active_user = None
if "chat_history_vault" not in st.session_state: st.session_state.chat_history_vault = {}
if "selected_history_topic" not in st.session_state: st.session_state.selected_history_topic = "General Study Session"
if "quiz_sheet_cache" not in st.session_state: st.session_state.quiz_sheet_cache = None
if "exam_sheet_cache" not in st.session_state: st.session_state.exam_sheet_cache = None

if st.session_state.active_user is None:
    st.title("🎓 ClassroomBuddy AI")
    auth_tab1, auth_tab2 = st.tabs(["🔒 Student Login", "📝 Dynamic Registration"])
    with auth_tab1:
        u_in = st.text_input("Username").lower().strip()
        p_in = st.text_input("Password", type="password")
        if st.button("➔", key="login_btn"):
            if u_in in st.session_state.master_user_db and st.session_state.master_user_db[u_in] == p_in:
                st.session_state.active_user = u_in
                if u_in not in st.session_state.chat_history_vault:
                    st.session_state.chat_history_vault[u_in] = {"General Study Session": []}
                st.rerun()
            else: st.error("Access denied.")
    st.stop()

# ChatGPT Style Left Panel Thread History Rails
with st.sidebar:
    st.markdown(f"### 👤 Welcome back, {st.session_state.active_user.upper()}!")
    research_mode_active = st.toggle("Research Mode", value=True)
    st.markdown("---")
    st.markdown("### 💬 Chat History")
    user_conversations = st.session_state.chat_history_vault[st.session_state.active_user]
    for topic_title in list(user_conversations.keys()):
        if st.button(f"📄 {topic_title[:20]}...", key=f"side_{topic_title}"):
            st.session_state.selected_history_topic = topic_title
            st.rerun()
    st.markdown("---")
    new_topic_field = st.text_input("New Chat Topic", placeholder="e.g., Bail Codes Matrix")
    if st.button("➔", key="add_topic_side"):
        if new_topic_field and new_topic_field not in user_conversations:
            user_conversations[new_topic_field] = []
            st.session_state.selected_history_topic = new_topic_field
            st.rerun()

def rapid_extract_document_chunks(file_asset):
    if file_asset is None: return ""
    try:
        pdf_reader = PdfReader(file_asset)
        text_data = ""
        for page in pdf_reader.pages[:30]:
            chunk = page.extract_text()
            if chunk: text_data += chunk + "\n"
        return text_data
    except Exception as e: return f"[Parsing Exception: {str(e)}]"

# Tab Setup Sequence Mapping Layout
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "💬 Ask Me Anything Legal", 
    "⚖️ Case Scenario Analyser", 
    "🏛️ Jurisprudence Scholar", 
    "🎯 Quiz Studio",
    "📝 Drafting Guide",
    "🏛️ Competitive Exam Hub"
])

# --- TAB 1: ASK ME ANYTHING LEGAL ---
with tab1:
    st.subheader("Ask Me Anything Legal")
    t1_upload = st.file_uploader("Upload reference files context (PDF):", type=["pdf"], key="t1_pdf")
    
    active_chat_log = st.session_state.chat_history_vault[st.session_state.active_user][st.session_state.selected_history_topic]
    for msg in active_chat_log:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
    col_prompt, col_mic = st.columns([0.85, 0.15])
    with col_prompt: t1_prompt = st.chat_input("Query any legal concepts or legal provisions here...", key="t1_prompt_input")
    with col_mic: t1_audio = st.audio_input("Voice Input Line", key="t1_mic_input", label_visibility="collapsed")
    
    if t1_prompt:
        active_chat_log.append({"role": "user", "content": t1_prompt})
        st.rerun()
        
    if active_chat_log and active_chat_log[-1]["role"] == "user":
        with st.chat_message("assistant"):
            with st.spinner("☁️ Accessing Grounding Engine..."):
                try:
                    client = genai.Client(api_key=MASTER_API_KEY)
                    file_context = rapid_extract_document_chunks(t1_upload)
                    system_instructions = f"You are ClassroomBuddy AI. Prioritize active criminal codes (BNS, 2023) first. Old IPC numbers are completely banned. Fall back to live google search if answers are missing from context.\n\nContext:\n{file_context}"
                    config = {"system_instruction": system_instructions}
                    if research_mode_active: config["tools"] = [{"google_search": {}}]
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash', contents=active_chat_log[-1]["content"], config=types.GenerateContentConfig(**config)
                    )
                    st.markdown(response.text)
                    active_chat_log.append({"role": "assistant", "content": response.text})
                except Exception as e: st.error(f"Engine connection exception: {str(e)}")

# --- TAB 2: CASE SCENARIO ANALYSER ---
with tab2:
    st.subheader("hey i am your case analysist , !")
    t2_upload = st.file_uploader("Upload fact sheets context (PDF):", type=["pdf"], key="t2_pdf")
    
    col_p, col_m = st.columns([0.85, 0.15])
    with col_p: t2_text = st.text_area("Legal Problem Statement / Factual Matrix Input Pane", height=100, key="t2_input_box", label_visibility="collapsed")
    with col_m: t2_audio = st.audio_input("Voice Input", key="t2_mic_input", label_visibility="collapsed")
    
    if st.button("➔", key="t2_trigger"):
        if t2_text or t2_upload:
            with st.spinner("☁:// Compiling IRAC Briefs..."):
                try:
                    client = genai.Client(api_key=MASTER_API_KEY)
                    file_context = rapid_extract_document_chunks(t2_upload)
                    system_instructions = f"Analyze facts using exactly 4 clear headers: ISSUE, RULE, APPLICATION, CONCLUSION. Apply active codes like BNS, BNSS first.\n\nContext:\n{file_context}"
                    config = {"system_instruction": system_instructions}
                    if research_mode_active: config["tools"] = [{"google_search": {}}]
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=t2_text, config=types.GenerateContentConfig(**config))
                    st.markdown(response.text)
                except Exception as e: st.error(str(e))

# --- TAB 3: JURISPRUDENCE SCHOLAR ---
with tab3:
    st.subheader("jurisprudence painkiller")
    
    # Elegant Custom Tarot Grid Layout
    st.markdown("""
    <div class='tarot-container'>
        <div class='tarot-card'><div class='tarot-title'>John Austin</div><div class='tarot-theory'>Command of the Sovereign backed by hard punitive sanctions.</div></div>
        <div class='tarot-card'><div class='tarot-title'>John Salmond</div><div class='tarot-theory'>Analytical Realism: principles implemented strictly by courts.</div></div>
        <div class='tarot-card'><div class='tarot-title'>H.L.A. Hart</div><div class='tarot-theory'>Law is an organic union of Primary and Secondary rules.</div></div>
        <div class='tarot-card'><div class='tarot-title'>Hans Kelsen</div><div class='tarot-theory'>The Pure Theory: every rule traces back to the master Grundnorm.</div></div>
        <div class='tarot-card'><div class='tarot-title'>Thomas Aquinas</div><div class='tarot-theory'>Natural Law: an ordinance of divine reason for the common good.</div></div>
    </div>
    """, unsafe_allow_html=True)
    
    t3_upload = st.file_uploader("Upload textbook metrics reading texts (PDF):", type=["pdf"], key="t3_pdf")
    col_p, col_m = st.columns([0.85, 0.15])
    with col_p: t3_text = st.text_input("Enter philosophy doctrine or analytical inquiry topic...", key="t3_input_box", label_visibility="collapsed")
    with col_m: t3_audio = st.audio_input("Voice Input", key="t3_mic_input", label_visibility="collapsed")
    
    if st.button("➔", key="t3_trigger"):
        if t3_text:
            with st.spinner("☁:// Compiling Socratic Evolutionary Matrix Loops..."):
                try:
                    client = genai.Client(api_key=MASTER_API_KEY)
                    file_context = rapid_extract_document_chunks(t3_upload)
                    system_instructions = f"You are an elite Socratic philosopher. Construct a clear evolutionary matrix or comparison timeline. Fall back to search if answers are missing.\n\nContext:\n{file_context}"
                    config = {"system_instruction": system_instructions}
                    if research_mode_active: config["tools"] = [{"google_search": {}}]
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=t3_text, config=types.GenerateContentConfig(**config))
                    st.markdown(response.text)
                except Exception as e: st.error(str(e))

# --- TAB 4: QUIZ STUDIO ---
with tab4:
    st.subheader("🎯 Quiz Studio")
    t4_upload = st.file_uploader("Upload syllabus reading guidelines notes (PDF):", type=["pdf"], key="t4_pdf")
    curriculum_domain = st.text_input("Target Subject Lane Category Focus Area:", value="BNS Criminal Law")
    quiz_mode = st.selectbox("Select Assessment Mode Suite Options:", ["Multiple Choice Questions (MCQs)", "Real-World Scenario Problems", "Long Answer Question Sheets", "Short Analytical Questions", "Fill in the Blanks"])
    
    if st.button("➔", key="t4_trigger"):
        with st.spinner("☁:// Generating customized sheets..."):
            try:
                client = genai.Client(api_key=MASTER_API_KEY)
                file_context = rapid_extract_document_chunks(t4_upload)
                prompt = f"Construct an evaluation testing assessment sheet using the '{quiz_mode}' format guidelines targeting '{curriculum_domain}'. Prioritize BNS provisions over legacy IPC numbers completely. Provide an explicit Answer Key at the end.\n\nContext:\n{file_context}"
                response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                st.session_state.quiz_sheet_cache = response.text
            except Exception as e: st.error(str(e))
    if st.session_state.quiz_sheet_cache: st.markdown(st.session_state.quiz_sheet_cache)

# --- TAB 5: DRAFTING GUIDE ---
with tab5:
    st.markdown("### **hello i am your drafting buddy**")
    t5_upload = st.file_uploader("Upload sample document template framework (PDF):", type=["pdf"], key="t5_pdf")
    target_instrument = st.text_input("Enter Document Type to Draft Template Framework Blueprint:")
    factual_specs = st.text_area("Factual Parameters & Client Specifications Guidelines")
    
    if st.button("➔", key="t5_trigger"):
        with st.spinner("☁:// Generating courtroom boilerplate drafts..."):
            try:
                client = genai.Client(api_key=MASTER_API_KEY)
                file_context = rapid_extract_document_chunks(t5_upload)
                prompt = f"Draft a professional legal document blueprint for a '{target_instrument}' using these specifications: {factual_specs}. Provide step-by-step placement sections and append a formal Vocabulary Guidance Sidebar section at the bottom.\n\nSample Document Base Context:\n{file_context}"
                response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                st.markdown(response.text)
            except Exception as e: st.error(str(e))

# --- TAB 6: COMPETITIVE EXAM HUB ---
with tab6:
    st.subheader("Exam Hub")
    t6_upload = st.file_uploader("Upload past competitive exam sheets (PDF):", type=["pdf"], key="t6_pdf")
    target_stream = st.selectbox("Select Target Stream:", ["Judiciary (PCS-J)", "JAG (Indian Army Officer Branch)", "Civil Services Law Optional Track"])
    focus_area = st.text_input("Syllabus Weightage Focus Area Concept Lane:", value="BNS and Constitutional Law Principles")
    
    if st.button("➔", key="t6_trigger"):
        with st.spinner("☁:// Analyzing blueprint weightage lines..."):
            try:
                client = genai.Client(api_key=MASTER_API_KEY)
                file_context = rapid_extract_document_chunks(t6_upload)
                prompt = f"Analyze structural syllabus patterns for '{target_stream}' focusing on '{focus_area}'. Output past paper weightage trends and formulate a realistic mock exam sheet matching real difficulty standards with an explicit answer key.\n\nContext:\n{file_context}"
                response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                st.session_state.exam_sheet_cache = response.text
            except Exception as e: st.error(str(e))
    if st.session_state.exam_sheet_cache: st.markdown(st.session_state.exam_sheet_cache)