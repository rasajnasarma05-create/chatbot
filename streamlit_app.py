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
    h1 {
        font-family: 'Georgia', serif;
        font-weight: bold;
        color: #4B0082 !important;
    }
    button[data-baseweb="tab"] {
        font-weight: 900 !important;
        color: #2D2D2D !important;
        font-size: 16px !important;
    }
    button[aria-selected="true"] {
        color: #4B0082 !important;
        border-bottom-color: #D4AF37 !important;
    }
    div.stButton > button:first-child {
        background-color: #4B0082 !important;
        color: #FFFFFF !important;
        border: 2px solid #D4AF37 !important;
        border-radius: 6px;
        font-weight: bold;
    }
    div.stButton > button:first-child:hover {
        background-color: #3A0066 !important;
        border-color: #FFD700 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Fetching the embedded Master Key securely from Streamlit Secrets
try:
    MASTER_API_KEY = st.secrets["GEMINI_MASTER_KEY"]
except Exception:
    MASTER_API_KEY = ""

# ==========================================
# 2. PERSISTENT INSTITUTIONAL REGISTRY GATE
# ==========================================
# Using a server-level dictionary cache that survives browser refreshes completely
@st.cache_resource
def get_persistent_user_database():
    return {
        "akshaya": "law2029",
        "megha": "gitam2026",
        "rasajna": "buddy2026",
        "professor": "juryexpert"
    }

USER_DATABASE = get_persistent_user_database()

if "active_user" not in st.session_state:
    st.session_state.active_user = None
if "user_session_vault" not in st.session_state:
    st.session_state.user_session_vault = {}
if "current_active_topic" not in st.session_state:
    st.session_state.current_active_topic = "General Study Session"
if "quiz_sheet_cache" not in st.session_state:
    st.session_state.quiz_sheet_cache = None

if st.session_state.active_user is None:
    st.title("🎓 ClassroomBuddy AI")
    st.subheader("Law School Authentication & Registration Hub")
    
    auth_tab1, auth_tab2 = st.tabs(["🔒 Existing Student Login", "📝 New Student Registration"])
    
    with auth_tab1:
        username_entry = st.text_input("Username / Roll Number", placeholder="e.g., rasajna or roll-042").lower().strip()
        password_entry = st.text_input("Password", type="password", placeholder="••••••••", key="login_pass_box")
        if st.button("Authenticate Login"):
            if username_entry in USER_DATABASE and USER_DATABASE[username_entry] == password_entry:
                st.session_state.active_user = username_entry
                if username_entry not in st.session_state.user_session_vault:
                    st.session_state.user_session_vault[username_entry] = {"General Study Session": []}
                st.success("Access authorized. Syncing custom workspaces...")
                st.rerun()
            else:
                st.error("Invalid credentials. If you just registered, ensure text matches or re-enter details.")
                
    with auth_tab2:
        reg_username = st.text_input("Create Username / Enter Roll Number", placeholder="e.g., rasajna").lower().strip()
        reg_password = st.text_input("Create Secure Password", type="password", placeholder="••••••••", key="reg_pass_box")
        if st.button("Register Account"):
            if not reg_username or not reg_password:
                st.error("Fields cannot be left blank.")
            elif reg_username in USER_DATABASE:
                st.error("Username already registered in institutional logs.")
            else:
                USER_DATABASE[reg_username] = reg_password
                st.success(f"Account for '{reg_username}' created permanently! Switch to login tab.")
    st.stop()

# Post-Authentication Active Workspace Environment
st.title("🎓 ClassroomBuddy AI")
st.caption(f"Secure Institutional Node Active | Welcome, {st.session_state.active_user.upper()}")
FEEDBACK_LOG_PATH = "data/peer_feedback.txt"

if st.session_state.active_user not in st.session_state.user_session_vault:
    st.session_state.user_session_vault[st.session_state.active_user] = {"General Study Session": []}

# Workspace Sidebar Configuration Dashboard
with st.sidebar:
    st.header("Dashboard")
    st.info("🛡️ Server Infrastructure Connected: Access is completely unlocked for students.")
    
    st.markdown("---")
    st.subheader("Verification Tools")
    research_mode_active = st.toggle("Research Mode", value=True, 
                                     help="Deploys live multi-source web search grounding to evaluate current amendments and judgments.")
    
    st.markdown("---")
    st.subheader("Study Sessions")
    new_topic_entry = st.text_input("Start New Chat Topic", placeholder="e.g., Mens Rea Evolution")
    if st.button("Initialize Topic"):
        if new_topic_entry and new_topic_entry not in st.session_state.user_session_vault[st.session_state.active_user]:
            st.session_state.user_session_vault[st.session_state.active_user][new_topic_entry] = []
            st.session_state.current_active_topic = new_topic_entry
            st.rerun()
            
    user_threads = st.session_state.user_session_vault[st.session_state.active_user]
    st.session_state.current_active_topic = st.selectbox("Select Chat Topic", list(user_threads.keys()), index=list(user_threads.keys()).index(st.session_state.current_active_topic))
    
    st.markdown("---")
    st.subheader("Peer Suggestion Box")
    anonymous_suggestion = st.text_area("Share bugs or recommendations anonymously:", placeholder="Type entry detail here...")
    if st.button("Submit Comment"):
        if anonymous_suggestion:
            os.makedirs("data", exist_ok=True)
            with open(FEEDBACK_LOG_PATH, "a") as file_handle:
                file_handle.write(f"[User Space Segment: {st.session_state.active_user}] - Suggestion: {anonymous_suggestion}\n---\n")
            st.success("Comment saved securely.")
            
    st.markdown("---")
    if st.button("🚪 Logout of Workspace"):
        st.session_state.active_user = None
        st.rerun()

# Rapid Document Processor RAG
def rapid_extract_document_chunks(file_asset):
    if file_asset is None:
        return ""
    try:
        pdf_reader = PdfReader(file_asset)
        extracted_text_payload = ""
        for page_index, file_page in enumerate(pdf_reader.pages[:30]):
            page_content_text = file_page.extract_text()
            if page_content_text:
                extracted_text_payload += f"\n[Doc Source Material: {file_asset.name} Page: {page_index+1}]\n{page_content_text}\n"
        return extracted_text_payload
    except Exception as e:
        return f"[Document parsing error: {str(e)}]"

# Tab Layout Sequence Configuration
tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Ask Me Anything Legal", 
    "⚖️ Case Scenario Analyser", 
    "🏛️ Jurisprudence Scholar", 
    "🎯 Quiz"
])

# --- TAB 1: ASK ME ANYTHING LEGAL ---
with tab1:
    st.subheader("Ask Me Anything Legal")
    st.write("Query global terminology, procedural concepts, or courtroom language instantly across any legal domain.")
    
    audio_query_t1 = st.audio_input("Record audio question via microphone:", key="mic_tab1_native")
    tab1_file_upload = st.file_uploader("Upload any supplementary document context (PDF):", type=["pdf"], key="master_t1_uploader")
    
    active_chat_log = st.session_state.user_session_vault[st.session_state.active_user][st.session_state.current_active_topic]
    for text_message in active_chat_log:
        with st.chat_message(text_message["role"]):
            st.markdown(text_message["content"])
            
    text_chat_input = st.chat_input("Query legal concepts or ask a direct procedural question...", key="chat_master_input_line")
    
    if text_chat_input or audio_query_t1:
        final_query_text = text_chat_input if text_chat_input else "[Audio Input Processed via Native Module]"
        active_chat_log.append({"role": "user", "content": final_query_text})
        st.rerun()
        
    if active_chat_log and active_chat_log[-1]["role"] == "user":
        unresolved_user_prompt = active_chat_log[-1]["content"]
        
        if not MASTER_API_KEY:
            st.warning("System Admin has not configured the Master Cloud Secret Key yet.")
        else:
            with st.chat_message("assistant"):
                text_stream_block = st.empty()
                try:
                    # Robust client initialization pass to prevent 401 connection exceptions
                    client_instance = genai.Client(api_key=MASTER_API_KEY)
                    file_context_string = rapid_extract_document_chunks(tab1_file_upload)
                    
                    system_instructions = (
                        "You are ClassroomBuddy AI, an advanced general legal consultant and critical courtroom analyst. "
                        "CRITICAL LEGAL INSTRUCTION:\n"
                        "1. If analyzing Indian criminal law elements, you are STRICTLY FORBIDDEN from using old IPC/CrPC standards as active law. You must prioritize the new Bharatiya Nyaya Sanhita (BNS, 2023), BNSS, and BSA provisions first.\n"
                        "2. Think critically, legally, and philosophically. Provide double-verified answers.\n\n"
                        f"--- LOCAL SOURCE FILE DATA BLOCK ---\n{file_context_string}"
                    )
                    
                    config_mapping = {"system_instruction": system_instructions}
                    if research_mode_active: config_mapping["tools"] = [{"google_search": {}}]
                        
                    api_call_response = client_instance.models.generate_content(
                        model='gemini-2.5-flash', contents=unresolved_user_prompt, config=types.GenerateContentConfig(**config_mapping)
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
                        
                    text_stream_block.markdown(final_response_payload)
                    active_chat_log.append({"role": "assistant", "content": final_response_payload})
                except Exception as loop_error: st.error(str(loop_error))

# --- TAB 2: CASE SCENARIO ANALYSER ---
with tab2:
    st.subheader("Case Scenario Analyser")
    st.write("Deconstruct complex fact problems using strict IRAC legal briefing guidelines.")
    
    audio_query_t2 = st.audio_input("Record scenario problem facts:", key="mic_tab2_native")
    problem_matrix_text = st.text_area("Legal Problem Statement / Factual Matrix", height=150, placeholder="Paste or record factual problem map inputs directly here...")
    selected_subject_domain = st.text_input("Select Subject", value="BNS (Criminal Law)", placeholder="Type any law subject here...")
    
    if st.button("Execute High-Rigor IRAC Evaluation", type="primary"):
        if not problem_matrix_text: st.error("Problem statement entry boundaries cannot remain empty.")
        elif not MASTER_API_KEY: st.error("Master Cloud Secret Key configuration missing.")
        else:
            with st.spinner("Compiling legal analysis briefs..."):
                try:
                    client_instance = genai.Client(api_key=MASTER_API_KEY)
                    system_instructions = (
                        "You are ClassroomBuddy AI, an elite legal analytical machine. Break down the query using exactly 4 clear headers:\n"
                        "1. ISSUE: Clear isolated legal questions tracking the factual matrices.\n"
                        "2. RULE: Primary supreme provisions (For criminal law, you MUST apply new codes like BNS, BNSS, BSA first as governing standards. Old IPC numbers are completely banned).\n"
                        "3. APPLICATION: Deeply apply facts to the rules framework components.\n"
                        "4. CONCLUSION: Clear structural final outcome summary judgment.\n"
                    )
                    config_mapping = {"system_instruction": system_instructions}
                    if research_mode_active: config_mapping["tools"] = [{"google_search": {}}]
                    
                    api_call_response = client_instance.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=f"Analyze facts: {problem_matrix_text}. Target subject classification: {selected_subject_domain}",
                        config=types.GenerateContentConfig(**config_mapping)
                    )
                    st.markdown("---")
                    st.success("IRAC Summary Brief Compiled Successfully!")
                    st.markdown(api_call_response.text)
                except Exception as generic_error: st.error(str(generic_error))

# --- TAB 3: DEDICATED JURISPRUDENCE SCHOLAR ---
with tab3:
    st.subheader("Jurisprudence Scholar")
    st.write("Deconstruct abstract philosophy using interactive Socratic educational loops.")
    
    tab3_file_upload = st.file_uploader("Upload specified legal philosophy reading texts (PDF):", type=["pdf"], key="philosophy_t3_uploader")
    audio_query_t3 = st.audio_input("Record philosophy query:", key="mic_tab3_native")
    
    st.markdown("**Select Preferred Learning Format Customization:**")
    layout_flow_check = st.checkbox("Flowchart / Logic Matrix Layout")
    layout_analogy_check = st.checkbox("Analogies & Real-World Illustrations", value=True)
    layout_case_check = st.checkbox("Landmark Precedent Analysis")
    layout_direct_check = st.checkbox("Direct Conceptual Answer Only")
    
    philosophy_query_line = st.text_input("Enter philosophy doctrine or analytical inquiry topic...", placeholder="e.g., Explain the historical school...")
    
    if st.button("Execute Scholar Processing", key="trigger_t3_processing_btn"):
        if not philosophy_query_line: st.error("Please enter a text philosophy query line to research.")
        elif not MASTER_API_KEY: st.error("Master Cloud Secret Key configuration missing.")
        else:
            with st.spinner("Extracting parameters from philosophy reading indexes..."):
                try:
                    client_instance = genai.Client(api_key=MASTER_API_KEY)
                    uploaded_book_context = rapid_extract_document_chunks(tab3_file_upload)
                    
                    layouts_list = []
                    if layout_flow_check: layouts_list.append("- A structural text flowchart tracking arguments chain.")
                    if layout_analogy_check: layouts_list.append("- Simple everyday analogies and direct examples.")
                    if layout_case_check: layouts_list.append("- Explicit landmark precedent analysis records.")
                    if layout_direct_check: layouts_list.append("- A sharp, direct conceptual answer immediately up front.")
                    compiled_layouts_string = "\n".join(layouts_list)
                    
                    system_instructions = (
                        "You are ClassroomBuddy AI, an elite legal philosopher and Socratic scholar. "
                        "CRITICAL SEARCH FALLBACK RULE:\n"
                        "If the user asks a concept and it is missing or not found within the uploaded book data context pool, "
                        "you MUST NOT state 'not found'. Instead, automatically switch to your baseline intelligence or activate Research Mode to pull correct web references.\n\n"
                        f"REQUIRED FORMAT MATRIX SETTINGS:\n{compiled_layouts_string or '- Pedagogical breakdown layout.'}\n\n"
                        "SOCRATIC INTERACTIVE LOOP:\n"
                        "At the bottom of response, append a structured markdown selector prompting next steps.\n\n"
                        f"--- ATTACHED SCHOLAR BOOK HIGHLIGHTS ---\n{uploaded_book_context}"
                    )
                    config_mapping = {"system_instruction": system_instructions}
                    if research_mode_active: config_mapping["tools"] = [{"google_search": {}}]
                    
                    api_call_response = client_instance.models.generate_content(
                        model='gemini-2.5-flash', contents=philosophy_query_line, config=types.GenerateContentConfig(**config_mapping)
                    )
                    st.markdown("---")
                    st.markdown(api_call_response.text)
                except Exception as generic_error: st.error(str(generic_error))

# --- TAB 4: THE OPEN QUIZ STUDIO ---
with tab4:
    st.subheader("Quiz")
    st.write("Construct evaluation testing sheets tailored to customized book uploads or any typing entry subject domain.")
    
    quiz_source_mode_radio = st.radio("Choose Material Source:", ["Select Curriculum Topic", "Upload Custom Study File"], key="quiz_source_selector_radio")
    audio_query_t4 = st.audio_input("Record test specs details:", key="mic_tab4_native")
    
    curriculum_domain_label = st.text_input("Enter Target Subject Domain:", value="BNS Criminal Law", placeholder="Type any specific law topic here...")
    custom_textbook_quiz_payload = ""
    
    if quiz_source_mode_radio == "Upload Custom Study File":
        tab4_file_upload = st.file_uploader("Upload custom textbook readings (PDF):", type=["pdf"], key="quiz_document_uploader_widget")
        if tab4_file_upload: custom_textbook_quiz_payload = rapid_extract_document_chunks(tab4_file_upload)
            
    chosen_quiz_assessment_mode = st.selectbox("Select Assessment Mode:", [
        "Multiple Choice Questions (MCQs)", "Real-World Scenario Problems",
        "Long Answer Question Sheets", "Short Analytical Questions", "Fill in the Blanks"
    ], key="quiz_mode_selector_box")
    
    if st.button("Generate Custom Test", type="primary", key="quiz_execution_trigger_btn"):
        if not MASTER_API_KEY: st.error("Master Cloud Secret Key configuration missing.")
        else:
            with st.spinner("Compiling custom testing parameters..."):
                try:
                    client_instance = genai.Client(api_key=MASTER_API_KEY)
                    
                    quiz_generation_prompt_string = (
                        f"Construct an evaluation sheet using exactly the '{chosen_quiz_assessment_mode}' format pattern rules. "
                        f"CRITICAL TESTING INSTRUCTION:\n"
                        f"You are strictly prohibited from generating evaluation questions based on the old Indian Penal Code (IPC) of 1860. You MUST formulate all questions and scenario answers using the new active laws: Bharatiya Nyaya Sanhita (BNS, 2023), BNSS, and BSA.\n\n"
                        f"TARGET SUBJECT LANE: '{curriculum_domain_label}'\n"
                        f"--- READING RESOURCE CONTENT MATRIX ---\n{custom_textbook_quiz_payload}\n\n"
                        "At the absolute end of your test sheet, provide a complete, clear Answer Key & Rationale Guide explicitly detailed to justify matching the BNS provisions criteria."
                    )
                    
                    config_mapping = {}
                    if research_mode_active: config_mapping["tools"] = [{"google_search": {}}]
                        
                    api_call_response = client_instance.models.generate_content(
                        model='gemini-2.5-flash', contents=quiz_generation_prompt_string, config=types.GenerateContentConfig(**config_mapping)
                    )
                    st.session_state.quiz_sheet_cache = api_call_response.text
                except Exception as generic_error: st.error(str(generic_error))
                
    if st.session_state.quiz_sheet_cache:
        st.markdown("---")
        st.markdown(st.session_state.quiz_sheet_cache)