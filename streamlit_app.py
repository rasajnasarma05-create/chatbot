import streamlit as st
from google import genai
from google.genai import types
import os
from pypdf import PdfReader

# ==========================================
# 1. ELITE LAW SCHOOL DESIGN THEMING (CSS)
# ==========================================
st.set_page_config(page_title="ClassroomBuddy AI", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    /* Premium Palette: Navy Blue, Sky Blue, Deep White, Amber Orange */
    .stApp { background-color: #F4F7F9; }
    
    /* Global Typography Reset */
    h1, h2, h3, h4, .stSubheader, p, label, .stMarkdown, div[data-baseweb="select"] {
        color: #0A192F !important; /* Deep Navy */
        font-family: 'Helvetica Neue', Arial, sans-serif;
    }
    h1 {
        font-family: 'Georgia', serif;
        font-weight: bold;
        color: #0A192F !important;
        border-bottom: 3px solid #FF9F1C; /* Amber Orange Accent line */
        padding-bottom: 10px;
    }
    
    /* Custom Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0A192F !important;
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }
    
    /* Modern Navigation Tabs */
    button[data-baseweb="tab"] {
        font-weight: 800 !important;
        color: #0A192F !important;
        font-size: 15px !important;
        background-color: #E2E8F0 !important;
        border-radius: 4px 4px 0px 0px;
        margin-right: 4px;
        padding: 10px 15px !important;
    }
    button[aria-selected="true"] {
        background-color: #00B4D8 !important; /* Sky Blue Highlight */
        color: #FFFFFF !important;
        border-bottom: 3px solid #FF9F1C !important;
    }
    
    /* Interactive Cloud & Water Containers */
    .cloud-bubble {
        background-color: #FFFFFF;
        border-left: 5px solid #00B4D8;
        border-radius: 12px;
        padding: 18px;
        margin: 12px 0px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    }
    .water-ripple-panel {
        background-color: #EBF8FF;
        border: 1px solid #BEE3F8;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0px;
    }
    
    /* Caricature Thinker Grid Profile Cards */
    .thinker-card {
        background-color: #FFFFFF;
        border: 2px solid #0A192F;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    }
    .thinker-name {
        font-family: 'Georgia', serif;
        font-weight: bold;
        color: #FF9F1C !important;
        font-size: 16px;
    }
    
    /* Minimalist Minimal Action Arrow Button Line Interface */
    div.stButton > button:first-child {
        background-color: #FF9F1C !important; /* Amber Orange */
        color: #0A192F !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 50% !important;
        width: 45px !important;
        height: 45px !important;
        font-size: 20px !important;
        line-height: 45px !important;
        padding: 0 !important;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    div.stButton > button:first-child:hover {
        transform: scale(1.1);
        background-color: #E08600 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Secure Encryption String Handling for Master Key
try:
    MASTER_API_KEY = str(st.secrets["GEMINI_MASTER_KEY"]).strip().replace('"', '').replace("'", "")
except Exception:
    MASTER_API_KEY = ""

# ==========================================
# 2. GLOBAL REGISTRY (REFRESH-PROOF)
# ==========================================
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

# Gatecheck Verification Interfacing
if st.session_state.active_user is None:
    st.title("🎓 ClassroomBuddy AI")
    st.subheader("Law School Core Authentication Hub")
    auth_tab1, auth_tab2 = st.tabs(["🔒 Student Login", "📝 Dynamic Registration"])
    
    with auth_tab1:
        username_entry = st.text_input("Username / Roll Number").lower().strip()
        password_entry = st.text_input("Password", type="password")
        if st.button("➔", key="login_trigger"):
            if username_entry in st.session_state.master_user_db and st.session_state.master_user_db[username_entry] == password_entry:
                st.session_state.active_user = username_entry
                if username_entry not in st.session_state.chat_history_vault:
                    st.session_state.chat_history_vault[username_entry] = {"General Study Session": []}
                st.rerun()
            else:
                st.error("Invalid institutional credentials.")
                
    with auth_tab2:
        reg_username = st.text_input("Create Username / Enter Roll Number", placeholder="e.g., megha").lower().strip()
        reg_password = st.text_input("Create Secure Password", type="password", placeholder="••••••••")
        if st.button("➔", key="reg_trigger"):
            if not reg_username or not reg_password:
                st.error("Fields cannot remain blank.")
            elif reg_username in st.session_state.master_user_db:
                st.error("Username already logged in standard database entries.")
            else:
                st.session_state.master_user_db[reg_username] = reg_password
                st.success(f"Account registered for '{reg_username}' cleanly! Switch to the Login tab.")
    st.stop()

# Initialize dynamic greeting block elements
if st.session_state.active_user not in st.session_state.chat_history_vault:
    st.session_state.chat_history_vault[st.session_state.active_user] = {"General Study Session": []}

# ==========================================
# 3. CHATGPT STYLE SIDEBAR INTERFACE OVERHAUL
# ==========================================
with st.sidebar:
    st.markdown(f"### 👤 Welcome back, {st.session_state.active_user.upper()}!")
    st.info("🛡️ Server Infrastructure Fully Connected.")
    st.markdown("---")
    
    research_mode_active = st.toggle("Research Mode", value=True)
    st.markdown("---")
    
    st.markdown("### 💬 Chat History")
    user_conversations = st.session_state.chat_history_vault[st.session_state.active_user]
    
    for topic_title in list(user_conversations.keys()):
        if st.button(f"📄 {topic_title[:24]}...", key=f"hist_{topic_title}"):
            st.session_state.selected_history_topic = topic_title
            st.rerun()
            
    st.markdown("---")
    new_chat_topic_name = st.text_input("Start New Chat Topic", placeholder="e.g., Section 13 HMA Problems")
    if st.button("➔", key="add_topic_btn"):
        if new_chat_topic_name and new_chat_topic_name not in user_conversations:
            user_conversations[new_chat_topic_name] = []
            st.session_state.selected_history_topic = new_chat_topic_name
            st.rerun()
            
    st.markdown("---")
    if st.button("🚪 Logout Node"):
        st.session_state.active_user = None
        st.rerun()

# Document RAG text processing chunker functions
def rapid_extract_document_chunks(file_asset):
    if file_asset is None: return ""
    try:
        pdf_reader = PdfReader(file_asset)
        extracted_text_payload = ""
        for page_index, file_page in enumerate(pdf_reader.pages[:30]):
            page_content_text = file_page.extract_text()
            if page_content_text: 
                extracted_text_payload += f"\n[Document Asset Source Material: {file_asset.name} Page: {page_index+1}]\n{page_content_text}\n"
        return extracted_text_payload
    except Exception as e: 
        return f"[Document parsing error: {str(e)}]"

# ==========================================
# 4. MASTER 6-TAB APPLICATION SUITE OVERHAUL
# ==========================================
st.title("🎓 ClassroomBuddy AI")
st.caption(f"Active Workspace Thread Segment Lane: {st.session_state.selected_history_topic}")

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
    st.subheader("Ask Me Anything Legal Workspace")
    audio_query_t1 = st.audio_input("Record audio question via microphone:", key="mic_tab1")
    tab1_file_upload = st.file_uploader("Upload reference files context (PDF):", type=["pdf"], key="uploader_t1")
    
    active_chat_log = st.session_state.chat_history_vault[st.session_state.active_user][st.session_state.selected_history_topic]
    for msg in active_chat_log:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
    text_chat_input = st.chat_input("Query any legal concepts or legal provisions here...")
    if text_chat_input:
        active_chat_log.append({"role": "user", "content": text_chat_input})
        st.rerun()
        
    if active_chat_log and active_chat_log[-1]["role"] == "user":
        unresolved_user_prompt = active_chat_log[-1]["content"]
        if not MASTER_API_KEY: st.warning("Master Key configuration missing from Streamlit secrets panel.")
        else:
            with st.chat_message("assistant"):
                with st.spinner("☁️ Accessing Cloud Network Grounding Processing Pools..."):
                    try:
                        client = genai.Client(api_key=MASTER_API_KEY)
                        file_context_string = rapid_extract_document_chunks(tab1_file_upload)
                        
                        system_instructions = (
                            "You are ClassroomBuddy AI, an elite general legal consultant. "
                            "CRITICAL LEGAL INSTRUCTION:\n"
                            "1. If analyzing Indian criminal law, you are STRICTLY FORBIDDEN from using legacy IPC/CrPC standards as active law. You must prioritize the Bharatiya Nyaya Sanhita (BNS, 2023), BNSS, and BSA provisions first.\n"
                            "2. If an answer is not found in the attached document text, automatically search the web using Research Mode.\n\n"
                            f"--- ATTACHED FILE SYSTEM MEMORY POOL ---\n{file_context_string}"
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
                                    final_response_payload += "\n\n---\n### 🌐 Research Mode Verified Reference Anchors:\n"
                                    for web_chunk in grounding_data.grounding_chunks:
                                        if hasattr(web_chunk, 'web') and web_chunk.web:
                                            final_response_payload += f"- [{web_chunk.web.title}]({web_chunk.web.uri})\n"
                            except Exception: pass
                            
                        st.markdown(f"<div class='cloud-bubble'>{final_response_payload}</div>", unsafe_allow_html=True)
                        active_chat_log.append({"role": "assistant", "content": final_response_payload})
                    except Exception as loop_error: st.error(str(loop_error))

# --- TAB 2: CASE SCENARIO ANALYSER ---
with tab2:
    st.subheader("Case Scenario Fact Brief Compiler")
    audio_query_t2 = st.audio_input("Record case scenario briefing via voice:", key="mic_tab2")
    tab2_file_upload = st.file_uploader("Upload fact sheets context (PDF):", type=["pdf"], key="uploader_t2")
    problem_matrix_text = st.text_area("Legal Problem Statement / Factual Matrix Input Pane", height=120, placeholder="Paste your raw case problem assignment facts straight here...")
    
    if st.button("➔", key="irac_trigger_arrow"):
        if not problem_matrix_text and not tab2_file_upload: st.error("Factual boundary inputs cannot remain completely blank.")
        elif not MASTER_API_KEY: st.error("Master Cloud Secret Key configuration missing.")
        else:
            with st.spinner("☁️ Compiling legal analysis briefs..."):
                try:
                    client = genai.Client(api_key=MASTER_API_KEY)
                    file_context_string = rapid_extract_document_chunks(tab2_file_upload)
                    
                    system_instructions = (
                        "You are ClassroomBuddy AI, an elite legal analyst machine. Break down the query using exactly 4 clear headers:\n"
                        "1. ISSUE: Isolated target legal questions.\n"
                        "2. RULE: Governing statutory laws (Apply new frameworks like BNS first. Old IPC numbers are banned).\n"
                        "3. APPLICATION: Deep evaluation applying facts to the rules framework components line-by-line.\n"
                        "4. CONCLUSION: Final structural summary judgment.\n\n"
                        f"--- ATTACHED CASE FACTS FILE ---\n{file_context_string}"
                    )
                    config = {"system_instruction": system_instructions}
                    if research_mode_active: config["tools"] = [{"google_search": {}}]
                        
                    api_call_response = client.models.generate_content(
                        model='gemini-2.5-flash', contents=problem_matrix_text, config=types.GenerateContentConfig(**config)
                    )
                    st.markdown(f"<div class='cloud-bubble'><h3>⚖️ IRAC Summary Brief Result</h3>{api_call_response.text}</div>", unsafe_allow_html=True)
                except Exception as generic_error: st.error(str(generic_error))

# --- TAB 3: JURISPRUDENCE SCHOLAR MASTERPIECE ---
with tab3:
    st.subheader("🏛️ Socratic Jurisprudence Comedy Court Panel")
    
    # Comedic Caricature Thinkers Profile Panel Grid Layout
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: st.markdown("<div class='thinker-card'><div class='thinker-name'>John Austin</div><p style='font-size:12px; color:#555;'>'Law is the Command of a Sovereign backed by Sanctions!'</p></div>", unsafe_allow_html=True)
    with col2: st.markdown("<div class='thinker-card'><div class='thinker-name'>John Salmond</div><p style='font-size:12px; color:#555;'>'Analytical Realism and the body of principles applied by Courts!'</p></div>", unsafe_allow_html=True)
    with col3: st.markdown("<div class='thinker-card'><div class='thinker-name'>H.L.A. Hart</div><p style='font-size:12px; color:#555;'>'Austin got it wrong. Law is a union of Primary and Secondary Rules!'</p></div>", unsafe_allow_html=True)
    with col4: st.markdown("<div class='thinker-card'><div class='thinker-name'>Hans Kelsen</div><p style='font-size:12px; color:#555;'>'The Pure Theory of Law. Trace everything up to the absolute Grundnorm!'</p></div>", unsafe_allow_html=True)
    with col5: st.markdown("<div class='thinker-card'><div class='thinker-name'>Thomas Aquinas</div><p style='font-size:12px; color:#555;'>'Natural law is an ordinance of divine reason for the common good!'</p></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    audio_query_t3 = st.audio_input("Record philosophy questions via mic:", key="mic_tab3")
    tab3_file_upload = st.file_uploader("Upload legal philosophy textbook materials (PDF):", type=["pdf"], key="uploader_t3")
    philosophy_query_line = st.text_input("Enter philosophy doctrine or analytical inquiry topic...", placeholder="e.g., Explain the Historical School vs Analytical School...")
    
    if st.button("➔", key="scholar_trigger_arrow"):
        if not philosophy_query_line: st.error("Please specify a philosophy query to break down.")
        elif not MASTER_API_KEY: st.error("Master Key configuration missing.")
        else:
            with st.spinner("☁️ Gathering Socratic Arguments and Evolutionary Timeline Parameters..."):
                try:
                    client = genai.Client(api_key=MASTER_API_KEY)
                    uploaded_book_context = rapid_extract_document_chunks(tab3_file_upload)
                    
                    system_instructions = (
                        "You are ClassroomBuddy AI, an elite legal philosopher and Socratic scholar. "
                        "Break up your answer into clear, engaging segments. "
                        "CRITICAL SEARCH FALLBACK RULE:\n"
                        "If the user asks a concept missing from the uploaded book data context pool, automatically switch to Research Mode or baseline intelligence to gather details.\n\n"
                        "REQUIRED LAYOUT:\n"
                        "1. Provide a clear, intuitive 'Evolutionary Timeline Matrix' mapping out how the schools evolved or attacked each other.\n"
                        "2. Output the explanation inside funny, witty, pedagogical paragraphs that summarize the thinkers' core arguments.\n\n"
                        f"--- ATTACHED SCHOLAR BOOK HIGHLIGHTS ---\n{uploaded_book_context}"
                    )
                    config = {"system_instruction": system_instructions}
                    if research_mode_active: config["tools"] = [{"google_search": {}}]
                        
                    api_call_response = client.models.generate_content(
                        model='gemini-2.5-flash', contents=philosophy_query_line, config=types.GenerateContentConfig(**config)
                    )
                    st.markdown(f"<div class='water-ripple-panel'><h2>🏛️ Philosophical Judgment Panel Response</h2>{api_call_response.text}</div>", unsafe_allow_html=True)
                except Exception as generic_error: st.error(str(generic_error))

# --- TAB 4: QUIZ STUDIO (ALL 5 MODES INSTALLED) ---
with tab4:
    st.subheader("🎯 The Open Quiz Studio Node")
    audio_query_t4 = st.audio_input("Record test constraints parameters via mic:", key="mic_tab4")
    tab4_file_upload = st.file_uploader("Upload textbook materials or readings notes (PDF):", type=["pdf"], key="uploader_t4")
    curriculum_domain_label = st.text_input("Enter Target Subject Lane Category:", value="BNS Criminal Law")
    
    chosen_quiz_assessment_mode = st.selectbox("Select Assessment Mode Suite:", [
        "Multiple Choice Questions (MCQs)", 
        "Real-World Scenario Problems",
        "Long Answer Question Sheets", 
        "Short Analytical Questions", 
        "Fill in the Blanks"
    ])
    
    if st.button("➔", key="quiz_trigger_arrow"):
        if not MASTER_API_KEY: st.error("Master Secret Key configuration missing.")
        else:
            with st.spinner("☁️ Compiling custom evaluation questions sheets..."):
                try:
                    client = genai.Client(api_key=MASTER_API_KEY)
                    custom_textbook_quiz_payload = rapid_extract_document_chunks(tab4_file_upload)
                    
                    quiz_generation_prompt_string = (
                        f"Construct an evaluation testing assessment sheet using exactly the '{chosen_quiz_assessment_mode}' format guidelines.\n"
                        f"CRITICAL TESTING INSTRUCTION:\n"
                        f"You are strictly prohibited from generating evaluation questions based on the old IPC. You MUST formulate all questions and scenario answers using the new active laws: Bharatiya Nyaya Sanhita (BNS, 2023), BNSS, and BSA.\n\n"
                        f"TARGET SUBJECT AREA lane: '{curriculum_domain_label}'\n"
                        f"--- READING RESOURCE CONTENT MATRIX FILE ---\n{custom_textbook_quiz_payload}\n\n"
                        "At the absolute end of your test sheet, provide a complete, clear Answer Key & Rationale Guide explicitly detailed to justify matching the statutory legal provisions criteria."
                    )
                    api_call_response = client.models.generate_content(
                        model='gemini-2.5-flash', contents=quiz_generation_prompt_string
                    )
                    st.session_state.quiz_sheet_cache = api_call_response.text
                except Exception as generic_error: st.error(str(generic_error))
                
    if st.session_state.quiz_sheet_cache:
        st.markdown(f"<div class='cloud-bubble'><h3>🎯 Custom Generated Exam Sheet</h3>{st.session_state.quiz_sheet_cache}</div>", unsafe_allow_html=True)

# --- TAB 5: THE COMPREHENSIVE DRAFTING GUIDE ---
with tab5:
    st.subheader("📝 Professional Legal Drafting Framework Assistant")
    audio_query_t5 = st.audio_input("Record instrument drafting specifications:", key="mic_tab5")
    target_draft_instrument = st.text_input("Enter Document Type to Draft", placeholder="e.g., Legal Notice for Breach of Contract, Defamation Complaint Application, RTI Query...")
    factual_elements_draft = st.text_area("Factual Parameters & Client Specifications", height=100, placeholder="Type the specific factual inputs, parties names, and dates to populate inside the legal template draft...")
    
    if st.button("➔", key="draft_trigger_arrow"):
        if not target_draft_instrument: st.error("Please specify an instrument type template to draft.")
        elif not MASTER_API_KEY: st.error("Master Cloud Secret Key configuration missing.")
        else:
            with st.spinner("☁️ Generating structural boilerplate legal drafts..."):
                try:
                    client = genai.Client(api_key=MASTER_API_KEY)
                    drafting_prompt_payload = (
                        f"You are an expert courtroom documentation master draftsman. Draft a highly professional, pristine, student-friendly legal blueprint template for a: '{target_draft_instrument}'.\n\n"
                        f"FACTUAL PARAMETERS FOR POPULATION:\n{factual_elements_draft}\n\n"
                        "CRITICAL PACKAGING RULE:\n"
                        "1. Provide automated structural outlines and step-by-step boilerplate placement sections.\n"
                        "2. Append a specialized 'Vocabulary Guidance Sidebar section' at the bottom containing formal legal phrases and terminology suggestions to elevate the overall legal presentation."
                    )
                    api_call_response = client.models.generate_content(
                        model='gemini-2.5-flash', contents=drafting_prompt_payload
                    )
                    st.markdown(f"<div class='water-ripple-panel'><h3>📝 Courtroom Ready Draft Asset</h3>{api_call_response.text}</div>", unsafe_allow_html=True)
                except Exception as generic_error: st.error(str(generic_error))

# --- TAB 6: COMPETITIVE EXAM HUB (JUDICIARY, JAG, CIVIL SERVICES) ---
with tab6:
    st.subheader("🏛️ Institutional Competitive Services Examination Simulator")
    audio_query_t6 = st.audio_input("Record exam testing specs:", key="mic_tab6")
    past_papers_file_upload = st.file_uploader("Upload past competitive exam question sheets (PDF):", type=["pdf"], key="uploader_t6")
    target_exam_stream = st.selectbox("Select Target Examination Stream Segment:", [
        "Provincial Civil Services - Judicial (PCS-J / Judiciary)",
        "Judge Advocate General Officer Branch (JAG - Indian Army)",
        "Civil Services IAS/IJS Law Optional Track Framework"
    ])
    core_focus_topic_exam = st.text_input("Specific Code Syllabus Weightage Focus Area", value="BNS and Constitutional Law Principles")
    
    if st.button("➔", key="exam_trigger_arrow"):
        if not MASTER_API_KEY: st.error("Master Cloud Secret Key configuration missing from deployment control panel.")
        else:
            with st.spinner("☁️ Analyzing weightage patterns and generating high-fidelity mock blueprints..."):
                try:
                    client = genai.Client(api_key=MASTER_API_KEY)
                    past_paper_text_context = rapid_extract_document_chunks(past_papers_file_upload)
                    
                    exam_prompt_payload = (
                        f"You are an elite institutional supervisor and premier coach for competitive law exams. "
                        f"Analyze the structure, syllabus blueprints, and difficulty matrix for the: '{target_exam_stream}' exam.\n\n"
                        f"SPECIFIC SYLLABUS CORNER FOCUS: {core_focus_topic_exam}\n"
                        f"--- ATTACHED PAST PAPERS RESOURCE FOR CORE WEIGHTAGE BLUEPRINT MATRIX ANALYSIS ---\n{past_paper_text_context}\n\n"
                        "REQUIRED SYSTEM CONFIGURATION OUTPUT:\n"
                        "1. A quick analytical breakdown of past paper subject weightage patterns (e.g., Constitutional Law: 35%, Criminal: 30%).\n"
                        "2. Formulate a highly realistic, challenging, and rigorous Mock Examination Paper that perfectly copies the exact style, tone, and question format of real legal service exams.\n"
                        "3. Append a detailed Answer Key and Evaluators Rationale Guide mapping matching provisions criteria at the very end."
                    )
                    api_call_response = client.models.generate_content(
                        model='gemini-2.5-flash', contents=exam_prompt_payload
                    )
                    st.session_state.exam_sheet_cache = api_call_response.text
                except Exception as generic_error: st.error(str(generic_error))
                
    if st.session_state.exam_sheet_cache:
        st.markdown(f"<div class='cloud-bubble'><h3>🏛️ Competitive Simulation Testing Asset</h3>{st.session_state.exam_sheet_cache}</div>", unsafe_allow_html=True)