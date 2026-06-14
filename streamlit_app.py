import streamlit as st
from google import genai
from google.genai import types
import os
from pypdf import PdfReader

# ==========================================
# 1. PREMIUM LAW SCHOOL VISUAL THEMING
# ==========================================
st.set_page_config(page_title="ClassroomBuddy AI", page_icon="🎓", layout="wide")

# Custom injection for professional Purple, Academic Yellow, and Silver accents
st.markdown("""
    <style>
    /* Global Background Adjustments */
    .stApp {
        background-color: #F8F9FA;
    }
    /* Main Headers Styling */
    h1 {
        color: #4B0082 !important; /* Royal Purple */
        font-family: 'Georgia', serif;
        font-weight: bold;
    }
    /* Primary buttons custom styling */
    div.stButton > button:first-child {
        background-color: #4B0082 !important;
        color: #FFFFFF !important;
        border: 2px solid #D4AF37 !important; /* Academic Gold/Yellow */
        border-radius: 6px;
        font-weight: bold;
        padding: 0.5rem 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    div.stButton > button:first-child:hover {
        background-color: #3A0066 !important;
        border-color: #FFD700 !important;
        color: #F0F0F0 !important;
    }
    /* Tab headers active accents */
    button[data-baseweb="tab"] {
        font-weight: bold !important;
        color: #6C757D !important;
    }
    button[aria-selected="true"] {
        color: #4B0082 !important;
        border-bottom-color: #D4AF37 !important;
    }
    /* Clean Cards for data storage displays */
    .metric-card {
        background-color: #FFFFFF;
        border-left: 5px solid #4B0082;
        padding: 15px;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True) # Fixed the exact keyword initialization typo here

st.title("🎓 ClassroomBuddy AI")
st.caption("Your Elite, Double-Verified Jurisprudence & Criminal Law Learning Matrix")

# Directory configurations
DATA_DIRS = {"BNS": "data/bns", "BNSS": "data/BNSS", "BSA": "data/bsa"}
FEEDBACK_FILE = "data/peer_feedback.txt"
for folder_path in DATA_DIRS.values():
    os.makedirs(folder_path, exist_ok=True)

# ==========================================
# 2. USER FRIENDLY PERSISTENT DASHBOARD STATE
# ==========================================
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {"General Study Session": []}
if "active_topic" not in st.session_state:
    st.session_state.active_topic = "General Study Session"
if "generated_quiz" not in st.session_state:
    st.session_state.generated_quiz = None

# Re-engineered Clean Sidebar Dashboard
with st.sidebar:
    st.header("Dashboard")
    user_api_key = st.text_input("Gemini API Key", type="password", placeholder="Paste authorization key...")
    
    st.markdown("---")
    st.subheader("Verification Tools")
    live_search_active = st.toggle("Live Google Verification", value=True, 
                                   help="Enables multi-source cross-referencing against real-time academic legal indices.")
    
    st.markdown("---")
    st.subheader("Study Sessions")
    
    # Simple topic session initializer
    topic_input = st.text_input("Start New Chat Topic", placeholder="e.g., Analytical Positivism Study")
    if st.button("Initialize Topic"):
        if topic_input and topic_input not in st.session_state.chat_sessions:
            st.session_state.chat_sessions[topic_input] = []
            st.session_state.active_topic = topic_input
            st.rerun()
            
    # Clean workspace selector dropdown mapping past records
    session_options = list(st.session_state.chat_sessions.keys())
    st.session_state.active_topic = st.selectbox("Select Chat Topic", session_options, index=session_options.index(st.session_state.active_topic))
    
    st.markdown("---")
    st.subheader("Peer Suggestion Box")
    peer_review = st.text_area("Anonymously share errors, suggestions, or drawbacks here:", placeholder="Type feedback details...")
    if st.button("Submit Comment"):
        if peer_review:
            with open(FEEDBACK_FILE, "a") as f:
                f.write(peer_review + "\n---\n")
            st.success("Feedback recorded anonymously. Thank you!")

# ==========================================
# 3. GLOBAL MEMORY CACHING ENGINE
# ==========================================
@st.cache_resource(show_spinner=False)
def extract_global_repository_context():
    parsed_context = ""
    for subject_label, folder_path in DATA_DIRS.items():
        if os.path.exists(folder_path):
            for file_name in os.listdir(folder_path):
                if file_name.endswith(".pdf"):
                    try:
                        reader = PdfReader(os.path.join(folder_path, file_name))
                        for idx, page in enumerate(reader.pages[:40]): # Processing buffer optimized for speed performance
                            page_text = page.extract_text()
                            if page_text:
                                parsed_context += f"\n[Repository: {subject_label} File: {file_name} Page Reference: {idx+1}]\n{page_text}\n"
                    except Exception:
                        pass
    return parsed_context

# Pre-load shared document indices cleanly
shared_context = extract_global_repository_context()

# ==========================================
# 4. MODULARIZED STUDENT LEARNING WORKSPACES
# ==========================================
tab1, tab2, tab3 = st.tabs(["🏛️ Jurisprudence Scholar", "⚖️ Case Scenario Analyzer", "📝 Quiz Studio"])

# --- TAB 1: DEDICATED SOCRATIC JURISPRUDENCE SCHOLAR MODULE ---
with tab1:
    st.subheader("Jurisprudence Scholar Engine")
    st.write("Deconstruct philosophy frameworks safely. Upload readings to extract logic structures.")
    
    # Local contextual file processing widget
    juris_file = st.file_uploader("Upload local reading materials or assignment notes (PDF):", type=["pdf"], key="juris_pdf_uploader")
    
    # Custom format selection control panel parameters
    st.markdown("**Select Preferred Learning Format:**")
    col1, col2, col3, col4 = st.columns(4)
    with col1: format_flow = st.checkbox("Flowchart / Logic Matrix Layout")
    with col2: format_analogies = st.checkbox("Analogies & Real-World Illustrations", value=True)
    with col3: format_precedents = st.checkbox("Landmark Precedent Analysis")
    with col4: format_direct = st.checkbox("Direct Conceptual Answer Only")
    
    # Map thread tracking session lists
    active_chat_stream = st.session_state.chat_sessions[st.session_state.active_topic]
    
    if not active_chat_stream:
        active_chat_stream.append({"role": "assistant", "content": "Hello! I am your Socratic Jurisprudence guide. Paste legal philosophical topics, and select formats to begin."})
        
    for entry in active_chat_stream:
        with st.chat_message(entry["role"]):
            st.markdown(entry["content"])
            
    # Multi-modal media pipeline upload capability
    captured_screenshot = st.file_uploader("📸 Upload legal flowcharts, handwritten notes, or textbook images:", type=["jpg", "jpeg", "png"], key="chat_img_uploader")
    
    if chat_prompt := st.chat_input("Query a philosophy concept or ask a direct question..."):
        active_chat_stream.append({"role": "user", "content": chat_prompt})
        with st.chat_message("user"):
            st.markdown(chat_prompt)
            
        if not user_api_key:
            st.warning("Please configure your Gemini API Key in the sidebar.")
        else:
            with st.chat_message("assistant"):
                response_frame = st.empty()
                try:
                    client = genai.Client(api_key=user_api_key)
                    
                    # Extract local PDF text if present
                    uploaded_juris_text = ""
                    if juris_file:
                        with st.spinner("Analyzing uploaded documentation context..."):
                            reader = PdfReader(juris_file)
                            for page in reader.pages[:30]:
                                text_chunk = page.extract_text()
                                if text_chunk: uploaded_juris_text += text_chunk + "\n"

                    # Assemble explicit formatting string rules based on checkbox status
                    requested_layouts = []
                    if format_flow: requested_layouts.append("- A text-based logic mapping or chronological structural flowchart layout tracing line arguments.")
                    if format_analogies: requested_layouts.append("- Relatable everyday student analogies, explicit illustrations, and plain-language examples.")
                    if format_precedents: requested_layouts.append("- Authoritative Supreme Court decisions or case laws evaluating this doctrine.")
                    if format_direct: requested_layouts.append("- A highly direct, un-complicated, sharp conceptual breakdown immediately up front.")
                    format_rules_string = "\n".join(requested_layouts)

                    system_instruction = (
                        "You are ClassroomBuddy AI, an expert law scholar and Socratic Jurisprudence professor. "
                        "Your mission is to guide students through dense legal theory securely. "
                        "You must cross-examine all data and remain 100% authentic. Do not invent fake precedents.\n\n"
                        "REQUIRED LAYOUT CONSTRAINTS:\n"
                        f"Tailor your response to integrate the following selected frameworks explicitly:\n{format_rules_string or '- Balanced pedagogical layout.'}\n\n"
                        "INTERACTIVE SOCRATIC CLOSURE LOOP:\n"
                        "At the absolute end of your response, you must display an 'Interactive Step Options Menu'. "
                        "Ask the student clearly if they would prefer you to:\n"
                        "1. Simplify this current explanation further with a completely fresh analogy.\n"
                        "2. Generate an interactive hypothetical case scenario question to verify if they truly understood the principles.\n\n"
                        f"--- UPLOADED BOOK READING CONTEXT ---\n{uploaded_juris_text}\n"
                        f"--- SHARED DATA REPOSITORY CONTEXT ---\n{shared_context}"
                    )
                    
                    execution_config = {"system_instruction": system_instruction}
                    if live_search_active:
                        execution_config["tools"] = [{"google_search": {}}]
                        
                    payload = []
                    if captured_screenshot:
                        import PIL.Image
                        loaded_image = PIL.Image.open(captured_screenshot)
                        payload.append(loaded_image)
                        payload.append(f"[Media processing pass enabled]. User inquiry: {chat_prompt}")
                    else:
                        for history_msg in active_chat_stream[:-1]:
                            msg_role = "user" if history_msg["role"] == "user" else "model"
                            payload.append({"role": msg_role, "parts": [{"text": history_msg["content"]}]})
                        payload.append({"role": "user", "parts": [{"text": chat_prompt}]})
                        
                    model_response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=payload,
                        config=types.GenerateContentConfig(**execution_config)
                    )
                    
                    final_output_text = model_response.text
                    
                    # Attach clickable web footnotes if search grounding returns hits
                    if live_search_active and hasattr(model_response, 'candidates') and model_response.candidates:
                        try:
                            metadata = model_response.candidates[0].grounding_metadata
                            if metadata and hasattr(metadata, 'grounding_chunks'):
                                final_output_text += "\n\n----- ---\n### Verified Research References:\n"
                                for link_chunk in metadata.grounding_chunks:
                                    if hasattr(link_chunk, 'web') and link_chunk.web:
                                        final_output_text += f"- [{link_chunk.web.title}]({link_chunk.web.uri})\n"
                        except Exception:
                            pass
                            
                    response_frame.markdown(final_output_text)
                    active_chat_stream.append({"role": "assistant", "content": final_output_text})
                except Exception as e:
                    st.error(f"Network processing checkpoint initialized. Details: {str(e)}")

# --- TAB 2: RIGOROUS CASE SCENARIO MATRIX ANALYZER ENGINE ---
with tab2:
    st.subheader("Case Scenario Analysis Workstation")
    st.write("Deconstruct real-world messy facts using strict legal analytical briefing parameters.")
    
    factual_matrix = st.text_area("Factual Scenario / Problem Statement", height=180, placeholder="Paste the complete case problem details here...")
    target_subject = st.selectbox("Select Subject", ["All Codes Combined", "Jurisprudence (Theory Critique)", "BNS (Substantive Offences)", "BNSS (Procedural Framework)", "BSA (Evidence Core)"])
    
    if st.button("Execute High-Rigor IRAC Evaluation", type="primary"):
        if not factual_matrix:
            st.error("Please enter a fact matrix problem.")
        elif not user_api_key:
            st.error("API Key required.")
        else:
            with st.spinner("Assembling structural legal verification matrices..."):
                try:
                    client = genai.Client(api_key=user_api_key)
                    
                    irac_evaluation_query = f"Analyze problem: {factual_matrix}. Primary target focus context: {target_subject}"
                    
                    system_instruction_rules = (
                        "You are ClassroomBuddy AI, an elite legal analyst. Evaluate the fact profile using strict IRAC structuring:\n"
                        "- **I. ISSUE**: Isolate the core legal contentions and questions clearly.\n"
                        "- **II. RULE**: State the active governing legal standard. If evaluating criminal law, ALWAYS state the new code rules (BNS, BNSS, BSA) as the primary supreme rules first. Immediately follow it with an exact evolution transition log tracing it back to the historic old IPC/CrPC counterparts, explaining why the text philosophy shifted.\n"
                        "- **III. APPLICATION/ANALYSIS**: Connect the case scenario facts directly to each component element of the provisions cited.\n"
                        "- **IV. CONCLUSION**: Provide a definitive final outcome summary statement.\n\n"
                        f"--- DATABASE RESOURCES ---\n{shared_context}"
                    )
                    
                    eval_config = {"system_instruction": system_instruction_rules}
                    if live_search_active:
                        eval_config["tools"] = [{"google_search": {}}]
                        
                    brief_response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=irac_evaluation_query,
                        config=types.GenerateContentConfig(**eval_config)
                    )
                    
                    st.markdown("---")
                    st.success("Analysis Successfully Compiled!")
                    st.markdown(brief_response.text)
                except Exception as e:
                    st.error(f"Evaluation loop conflict: {str(e)}")

# --- TAB 3: THE ALL-MODE QUIZ MATRIX STUDIO ---
with tab3:
    st.subheader("Quiz Studio")
    st.write("Generate customized interactive test sheets based on topics or uploaded reading documents.")
    
    # Core input selectors
    quiz_input_mode = st.radio("Choose Material Source:", ["Select Curriculum Topic", "Upload Custom Study File"])
    
    targeted_topic = "General legal principles"
    custom_quiz_text = ""
    
    if quiz_input_mode == "Select Curriculum Topic":
        targeted_topic = st.selectbox("Choose Target Subject Domain:", [
            "Murder & Culpable Homicide", 
            "Criminal Stalking & Electronic Monitoring",
            "General Exceptions & Defenses",
            "International Law Foundations",
            "Analytical Positivism & Sovereign Commands",
            "Natural Law Doctrines & Morality Theories"
        ])
    else:
        quiz_file_upload = st.file_uploader("Upload custom textbook chapter or notes (PDF):", type=["pdf"], key="quiz_uploader_widget")
        if quiz_file_upload:
            with st.spinner("Scanning file text indices..."):
                quiz_reader = PdfReader(quiz_file_upload)
                for q_page in quiz_reader.pages[:25]:
                    text_line = q_page.extract_text()
                    if text_line: custom_quiz_text += text_line + "\n"
                    
    # Evaluation structural configuration modes
    selected_mode = st.selectbox("Select Assessment Mode:", [
        "Multiple Choice Questions (MCQs)",
        "Real-World Scenario Problems",
        "Long Answer Question Sheets",
        "Short Analytical Questions",
        "Fill in the Blanks"
    ])
    
    if st.button("Generate Custom Test", type="primary"):
        if not user_api_key:
            st.error("API Key required.")
        else:
            with st.spinner("Assembling examination items..."):
                try:
                    client = genai.Client(api_key=user_api_key)
                    
                    quiz_construction_prompt = (
                        f"Construct a complete exam paper utilizing the '{selected_mode}' architecture. "
                        f"Focus heavily on the selected subject scope: '{targeted_topic}'.\n\n"
                        f"CONTEXT SPECS:\n"
                        f"If custom text is provided here, extract parameters directly from it: {custom_quiz_text or 'Rely on standard Indian legal curriculum guidelines.'}\n\n"
                        "OUTPUT CONSTRAINT:\n"
                        "Provide questions clearly. At the end, include a comprehensive 'Answer Key & Analytical Verification Guide' breaking down exactly why each correct answer matches the law."
                    )
                    
                    quiz_response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=quiz_construction_prompt
                    )
                    st.session_state.generated_quiz = quiz_response.text
                except Exception as e:
                    st.error(f"Quiz compilation aborted: {str(e)}")
                    
    if st.session_state.generated_quiz:
        st.markdown("---")
        st.markdown("### Active Assessment Sheet")
        st.markdown(st.session_state.generated_quiz)
        st.info("Write down your logic, test your parameters, and consult Tab 1 if you need any concept simplified further!")