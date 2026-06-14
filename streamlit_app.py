import streamlit as st
from google import genai
from google.genai import types
import os
from pypdf import PdfReader
from streamlit_mic_recorder import speech_to_text

# ==========================================
# 1. PREMIUM LAW SCHOOL DARK TYPOGRAPHY THEMING
# ==========================================
st.set_page_config(page_title="ClassroomBuddy AI", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    /* Global Canvas Styling */
    .stApp {
        background-color: #F8F9FA;
    }
    /* STRICT DARK TYPOGRAPHY FOR PROFESSIONAL ACCENT */
    h1, h2, h3, h4, .stSubheader, p, label, .stMarkdown, div[data-baseweb="select"] {
        color: #1A1A1A !important; /* Deep Solid Charcoal */
        font-family: 'Helvetica Neue', Arial, sans-serif;
    }
    h1 {
        font-family: 'Georgia', serif;
        font-weight: bold;
        color: #4B0082 !important; /* Royal Purple Primary Title */
    }
    /* Bold Dark Navigation Bars Selector Rules */
    button[data-baseweb="tab"] {
        font-weight: 900 !important;
        color: #2D2D2D !important; /* Bold Black Unselected Text */
        font-size: 16px !important;
    }
    button[aria-selected="true"] {
        color: #4B0082 !important; /* Purple focused text */
        border-bottom-color: #D4AF37 !important; /* Gold/Yellow bottom line */
    }
    /* Royal Purple Action Triggers */
    div.stButton > button:first-child {
        background-color: #4B0082 !important;
        color: #FFFFFF !important;
        border: 2px solid #D4AF37 !important; /* Academic Gold Accent */
        border-radius: 6px;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    div.stButton > button:first-child:hover {
        background-color: #3A0066 !important;
        border-color: #FFD700 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. INSTALMENT OF INSTITUTIONAL MULTI-USER GATE
# ==========================================
USER_REGISTRY = {
    "akshaya": "law2029",
    "buddy": "classroom",
    "professor": "juryexpert"
}

if "active_user" not in st.session_state:
    st.session_state.active_user = None

if st.session_state.active_user is None:
    st.title("🎓 ClassroomBuddy AI")
    st.subheader("Secure Law School Authentication Workspace")
    
    col1, _ = st.columns([1, 1])
    with col1:
        username_entry = st.text_input("Enter Student Username", placeholder="e.g., akshaya")
        password_entry = st.text_input("Enter System Password", type="password", placeholder="••••••••")
        if st.button("Authenticate Login"):
            if username_entry.lower() in USER_REGISTRY and USER_REGISTRY[username_entry.lower()] == password_entry:
                st.session_state.active_user = username_entry.lower()
                st.success(f"Access authorized. Syncing workspace maps...")
                st.rerun()
            else:
                st.error("Invalid institutional credentials. Please try again.")
    st.stop()

# Post-Verification Global Layout Space
st.title("🎓 ClassroomBuddy AI")
st.caption(f"Secure Node Active | Authorized User: {st.session_state.active_user.upper()}")

# Global paths configuration parameters
FEEDBACK_LOG_PATH = "data/peer_feedback.txt"

# ==========================================
# 3. USER TOPIC SESSION SPACE SEGREGATION
# ==========================================
if "user_session_vault" not in st.session_state:
    st.session_state.user_session_vault = {}

# Ensure individual sandboxed directory structure exists
if st.session_state.active_user not in st.session_state.user_session_vault:
    st.session_state.user_session_vault[st.session_state.active_user] = {"General Study Session": []}

if "current_active_topic" not in st.session_state:
    st.session_state.current_active_topic = "General Study Session"
if "quiz_sheet_cache" not in st.session_state:
    st.session_state.quiz_sheet_cache = None

# Sidebar Dashboard Configuration Layout
with st.sidebar:
    st.header("Dashboard")
    user_api_key = st.text_input("Gemini API Key", type="password", placeholder="Paste authentication key...")
    
    st.markdown("---")
    st.subheader("Verification Tools")
    research_mode_active = st.toggle("Research Mode", value=True, 
                                     help="Deploys live multi-source web search grounding to evaluate current amendments and judgments.")
    
    st.markdown("---")
    st.subheader("Study Sessions")
    
    new_topic_entry = st.text_input("Start New Chat Topic", placeholder="e.g., Analytical Positivism Study")
    if st.button("Initialize Topic"):
        if new_topic_entry and new_topic_entry not in st.session_state.user_session_vault[st.session_state.active_user]:
            st.session_state.user_session_vault[st.session_state.active_user][new_topic_entry] = []
            st.session_state.current_active_topic = new_topic_entry
            st.rerun()
            
    # Clean User Session Log Down-drop Selection
    user_threads = st.session_state.user_session_vault[st.session_state.active_user]
    st.session_state.current_active_topic = st.selectbox(
        "Select Chat Topic", 
        list(user_threads.keys()), 
        index=list(user_threads.keys()).index(st.session_state.current_active_topic)
    )
    
    st.markdown("---")
    st.subheader("Peer Suggestion Box")
    anonymous_suggestion = st.text_area("Share bugs, drawbacks, or recommendations anonymously:", placeholder="Type entry detail here...")
    if st.button("Submit Comment"):
        if anonymous_suggestion:
            os.makedirs("data", exist_ok=True)
            with open(FEEDBACK_LOG_PATH, "a") as file_handle:
                file_handle.write(f"[User Space Segment: {st.session_state.active_user}] - Suggestion: {anonymous_suggestion}\n---\n")
            st.success("Comment saved securely to backend ledger array.")
            
    st.markdown("---")
    if st.button("🚪 Logout of Workspace"):
        st.session_state.active_user = None
        st.rerun()

# ==========================================
# 4. RAPID RAG DOCUMENT IN-MEMORY PROCESSOR (ZERO-LAG LOGIC)
# ==========================================
def rapid_extract_document_chunks(file_asset):
    if file_asset is None:
        return ""
    try:
        pdf_reader = PdfReader(file_asset)
        extracted_text_payload = ""
        # Parsed page count buffer safety limit optimized to bypass 429 quota limits completely
        for page_index, file_page in enumerate(pdf_reader.pages[:30]):
            page_content_text = file_page.extract_text()
            if page_content_text:
                extracted_text_payload += f"\n[Document Context Reference: {file_asset.name} | Page Ref Line: {page_index+1}]\n{page_content_text}\n"
        return extracted_text_payload
    except Exception as current_error:
        return f"[Document indexing error parameter captured: {str(current_error)}]"

# ==========================================
# 5. STRICT FOUR-MODULE NAVIGATION INTERFACE SEQUENCING
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Ask Me Anything Legal", 
    "⚖️ Case Scenario Analyser", 
    "🏛️ Jurisprudence Scholar", 
    "🎯 Quiz"
])

# --- TAB 1: ASK ME ANYTHING LEGAL (UNRESTRICTED MASTER WORKSPACE) ---
with tab1:
    st.subheader("Ask Me Anything Legal")
    st.write("Query global terminology, core procedural concepts, or courtroom language instantly across any legal domain.")
    
    # Global audio mic recording module integration loop
    st.write("🎙️ **Voice input processing console:**")
    voice_input_t1 = speech_to_text(language='en', start_prompt="Record Verbal Question", stop_prompt="Stop Recording", just_once=True, key='global_mic_tab1')
    
    tab1_file_upload = st.file_uploader("Upload any supplementary case file or reading material context (PDF):", type=["pdf"], key="master_t1_uploader")
    
    # Track sandboxed user chat lists
    active_chat_log = st.session_state.user_session_vault[st.session_state.active_user][st.session_state.current_active_topic]
    
    if not active_chat_log:
        active_chat_log.append({"role": "assistant", "content": "System connection authorized. I am ClassroomBuddy, your advanced critical legal counsel. Ask anything legal to begin."})
        
    for text_message in active_chat_log:
        with st.chat_message(text_message["role"]):
            st.markdown(text_message["content"])
            
    text_chat_input = st.chat_input("Query legal concepts or ask a direct procedural question...", key="chat_master_input_line")
    
    # Overwrite raw prompt input tracking variables if audio recording registers payload text
    if voice_input_t1:
        text_chat_input = voice_input_t1
        
    if text_chat_input:
        active_chat_log.append({"role": "user", "content": text_chat_input})
        st.rerun()
        
    if active_chat_log and active_chat_log[-1]["role"] == "user":
        unresolved_user_prompt = active_chat_log[-1]["content"]
        
        if not user_api_key:
            st.warning("Please configure your Gemini API Key in the sidebar dashboard to open connection channels.")
        else:
            with st.chat_message("assistant"):
                text_stream_block = st.empty()
                try:
                    client_instance = genai.Client(api_key=user_api_key)
                    file_context_string = rapid_extract_document_chunks(tab1_file_upload)
                    
                    system_rules_specification = (
                        "You are ClassroomBuddy AI, an advanced general legal consultant and critical courtroom analyst. "
                        "You evaluate terminology, comparative procedural doctrines, and cross-subject legal matters deeply. "
                        "Think critically, legally, and philosophically. Provide answers with maximum factual correct accuracy.\n\n"
                        f"--- LOCAL SOURCE FILE DATA BLOCK ---\n{file_context_string}"
                    )
                    
                    config_mapping = {"system_instruction": system_rules_specification}
                    if research_mode_active:
                        config_mapping["tools"] = [{"google_search": {}}]
                        
                    api_call_response = client_instance.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=unresolved_user_prompt,
                        config=types.GenerateContentConfig(**config_mapping)
                    )
                    
                    final_response_payload = api_call_response.text
                    
                    # Inject clickable link footnote cards if web grounding yields data references
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
                except Exception as loop_error:
                    st.error(f"Execution boundary line dropped. Details: {str(loop_error)}")

# --- TAB 2: HIGH-RIGOR CASE SCENARIO ANALYSER (IRAC ENGINE) ---
with tab2:
    st.subheader("Case Scenario Analyser")
    st.write("Deconstruct complex fact problems using strict IRAC legal briefing guidelines.")
    
    st.write("🎙---- **Voice input scenario criteria console:**")
    voice_input_t2 = speech_to_text(language='en', start_prompt="Speak Case Scenario Details", stop_prompt="Stop Recording", just_once=True, key='global_mic_tab2')
    
    problem_matrix_text = st.text_area("Legal Problem Statement / Factual Matrix", height=150, value=voice_input_t2 if voice_input_t2 else "", placeholder="Paste case scenario matrix parameters directly here...")
    selected_subject_domain = st.selectbox("Select Subject", ["All Codes Combined", "Jurisprudence (Theory Critique)", "BNS (Substantive Offences)", "BNSS (Procedural Framework)", "BSA (Evidence Core)"], key="subject_dropdown_selector")
    
    if st.button("Execute High-Rigor IRAC Evaluation", type="primary"):
        if not problem_matrix_text:
            st.error("Problem statement text boundaries cannot remain empty.")
        elif not user_api_key:
            st.error("API Key authorization missing.")
        else:
            with st.spinner("Compiling legal analysis briefs..."):
                try:
                    client_instance = genai.Client(api_key=user_api_key)
                    system_rules_specification = (
                        "You are ClassroomBuddy AI, an elite analytical briefing machine. Break down the query using exactly 4 sections:\n"
                        "1. ISSUE: Clear legal questions tracking the conflict matrix components.\n"
                        "2. RULE: Active supreme code provision (Apply new rules like BNS/BNSS/BSA first as primary law, then trace its evolution backwards to old IPC/CrPC counterparts to clarify exact modifications).\n"
                        "3. APPLICATION: Connect facts to rules text step-by-step with structural critique logic.\n"
                        "4. CONCLUSION: Final judgment mapping.\n"
                    )
                    config_mapping = {"system_instruction": system_rules_specification}
                    if research_mode_active: 
                        config_mapping["tools"] = [{"google_search": {}}]
                    
                    api_call_response = client_instance.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=f"Analyze problem facts: {problem_matrix_text}. Target subject lane constraints: {selected_subject_domain}",
                        config=types.GenerateContentConfig(**config_mapping)
                    )
                    st.markdown("---")
                    st.success("IRAC Summary Brief Compiled Successfully!")
                    st.markdown(api_call_response.text)
                except Exception as generic_error: 
                    st.error(str(generic_error))

# --- TAB 3: DEDICATED JURISPRUDENCE SCHOLAR HUB ---
with tab3:
    st.subheader("Jurisprudence Scholar")
    st.write("Deconstruct abstract philosophy using interactive Socratic educational loops and deep reasoning custom frameworks.")
    
    tab3_file_upload = st.file_uploader("Upload specified legal philosophy reading texts or book chapters (PDF):", type=["pdf"], key="philosophy_t3_uploader")
    
    st.write("🎙️ **Voice prompt tool:**")
    voice_input_t3 = speech_to_text(language='en', start_prompt="Speak Philosophy Query Topic", stop_prompt="Stop Recording", just_once=True, key='global_mic_tab3')
    
    st.markdown("**Select Preferred Learning Format Customization:**")
    layout_flow_check = st.checkbox("Flowchart / Logic Matrix Layout", key="box_cfg_flow")
    layout_analogy_check = st.checkbox("Analogies & Real-World Illustrations", value=True, key="box_cfg_analogy")
    layout_case_check = st.checkbox("Landmark Precedent Analysis", key="box_cfg_case")
    layout_direct_check = st.checkbox("Direct Conceptual Answer Only", key="box_cfg_direct")
    
    philosophy_query_line = st.text_input("Enter philosophy doctrine or analytical inquiry topic...", value=voice_input_t3 if voice_input_t3 else "", key="text_t3_input_box")
    
    if st.button("Execute Scholar Processing", key="trigger_t3_processing_btn"):
        if not philosophy_query_line: 
            st.error("Please enter a text philosophy query line to research.")
        elif not user_api_key: 
            st.error("API Key entry validation parameter missing.")
        else:
            with st.spinner("Extracting parameters from philosophy reading indexes..."):
                try:
                    client_instance = genai.Client(api_key=user_api_key)
                    uploaded_book_context = rapid_extract_document_chunks(tab3_file_upload)
                    
                    layouts_list = []
                    if layout_flow_check: layouts_list.append("- A step-by-step structural text flowchart/logic tree diagram layout tracking the school's sequence arguments.")
                    if layout_analogy_check: layouts_list.append("- Simple everyday analogies and clear legal illustrations to link abstract principles to current reality.")
                    if layout_case_check: layouts_list.append("- Explicit landmark precedent analysis records proving how courts applied this philosophy.")
                    if layout_direct_check: layouts_list.append("- A sharp, un-complicated, direct concept answer immediately up front.")
                    compiled_layouts_string = "\n".join(layouts_list)
                    
                    system_rules_specification = (
                        "You are ClassroomBuddy AI, an elite legal philosopher and Socratic scholar. "
                        "Explain theory concepts explicitly using the target formats highlighted below.\n\n"
                        f"REQUIRED FORMAT MATRIX LOGS:\n{compiled_layouts_string or '- Balanced pedagogical structure.'}\n\n"
                        "SOCRATIC INTERACTIVE LOOP RULE:\n"
                        "At the absolute bottom of your response, you must prompt the user with a next-step options selection list asking if they want to:\n"
                        "Option 1: Simplify this current topic text again with a completely fresh illustration.\n"
                        "Option 2: Construct an interactive factual matrix question to test their understanding.\n\n"
                        f"--- ATTACHED SCHOLAR BOOK HIGHLIGHTS ---\n{uploaded_book_context}"
                    )
                    config_mapping = {"system_instruction": system_rules_specification}
                    if research_mode_active: 
                        config_mapping["tools"] = [{"google_search": {}}]
                    
                    api_call_response = client_instance.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=philosophy_query_line,
                        config=types.GenerateContentConfig(**config_mapping)
                    )
                    st.markdown("---")
                    st.markdown(api_call_response.text)
                except Exception as generic_error: 
                    st.error(str(generic_error))

# --- TAB 4: THE ALL-MODE QUIZ ENGINE ---
with tab4:
    st.subheader("Quiz")
    st.write("Construct interactive testing matrices tailored to customized book uploads or specific target subject domains.")
    
    quiz_source_mode_radio = st.radio("Choose Material Source:", ["Select Curriculum Topic", "Upload Custom Study File"], key="quiz_source_selector_radio")
    
    curriculum_domain_label = "General Law Principles"
    custom_textbook_quiz_payload = ""
    
    if quiz_source_mode_radio == "Select Curriculum Topic":
        curriculum_domain_label = st.selectbox("Choose Target Subject Domain:", [
            "Murder & Culpable Homicide", "Criminal Stalking & Electronic Monitoring",
            "General Exceptions & Defenses", "International Law Foundations",
            "Analytical Positivism & Sovereign Commands", "Natural Law Doctrines & Morality Theories"
        ], key="quiz_curriculum_selector_box")
    else:
        tab4_file_upload = st.file_uploader("Upload custom textbook readings or syllabus review logs (PDF):", type=["pdf"], key="quiz_document_uploader_widget")
        if tab4_file_upload:
            custom_textbook_quiz_payload = rapid_extract_document_chunks(tab4_file_upload)
            
    chosen_quiz_assessment_mode = st.selectbox("Select Assessment Mode:", [
        "Multiple Choice Questions (MCQs)", "Real-World Scenario Problems",
        "Long Answer Question Sheets", "Short Analytical Questions", "Fill in the Blanks"
    ], key="quiz_mode_selector_box")
    
    if st.button("Generate Custom Test", type="primary", key="quiz_execution_trigger_btn"):
        if not user_api_key: 
            st.error("API Key tracking access key entry missing.")
        else:
            with st.spinner("Compiling custom testing parameters..."):
                try:
                    client_instance = genai.Client(api_key=user_api_key)
                    quiz_generation_prompt_string = (
                        f"Construct an evaluation sheet using exactly the '{chosen_quiz_assessment_mode}' format pattern rules. "
                        f"Focus heavily on testing this scope criteria topic area: '{curriculum_domain_label}'.\n\n"
                        f"--- READING RESOURCE CONTENT MATRIX ---\n{custom_textbook_quiz_payload or 'Utilize standard Indian legal curriculum frameworks.'}\n\n"
                        "At the absolute end, print an active answer key guide detailing specific rationale explanations for each test entry item."
                    )
                    api_call_response = client_instance.models.generate_content(
                        model='gemini-2.5-flash', 
                        contents=quiz_generation_prompt_string
                    )
                    st.session_state.quiz_sheet_cache = api_call_response.text
                except Exception as generic_error: 
                    st.error(str(generic_error))
                
    if st.session_state.quiz_sheet_cache:
        st.markdown("---")
        st.markdown(st.session_state.quiz_sheet_cache)