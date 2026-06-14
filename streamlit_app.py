import streamlit as st
from google import genai
from google.genai import types
import os
import json
from pypdf import PdfReader

# ==========================================
# 1. PREMIUM CUSTOM CSS THEMING (PURPLE & GOLD)
# ==========================================
st.set_page_config(page_title="ClassroomBuddy AI", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    /* Main App Background & Colors */
    :root {
        --primary-color: #4B0082; /* Royal Purple */
        --secondary-color: #D4AF37; /* Academic Gold */
    }
    .stApp {
        background-color: #FAFAFA;
    }
    /* Buttons and Highlights */
    div.stButton > button:first-child {
        background-color: #4B0082;
        color: white;
        border-radius: 8px;
        border: 2px solid #D4AF37;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #6A0DAD;
        border-color: #FFD700;
        transform: scale(1.02);
    }
    /* Chat bubbles custom style */
    .chat-card {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_with_html=True)

st.title("🎓 ClassroomBuddy AI")
st.caption("The Invincible, Double-Verified Jurisprudence & Criminal Law Learning Matrix")

# Directory setups
DATA_DIRS = {"BNS": "data/bns", "BNSS": "data/BNSS", "BSA": "data/bsa"}
FEEDBACK_FILE = "data/peer_feedback.txt"
for folder_path in DATA_DIRS.values():
    os.makedirs(folder_path, exist_ok=True)

# ==========================================
# 2. STATE PERSISTENCE & HISTORY MANAGEMENT
# ==========================================
if "sessions" not in st.session_state:
    st.session_state.sessions = {"Default Session": []}
if "current_session" not in st.session_state:
    st.session_state.current_session = "Default Session"
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = None

# Sidebar History Dashboard
with st.sidebar:
    st.header("🎯 System Control")
    gemini_api_key = st.text_input("Enter Gemini API Key", type="password")
    
    st.markdown("---")
    st.header("🔍 Verification Settings")
    research_mode = st.toggle("Activate Live Google Research", value=True, 
                              help="Connects the AI engine to live Google search data for real-time statutory updates.")
    
    st.markdown("---")
    st.header("💬 Gemini History Bar")
    
    # New session activation button
    new_session_name = st.text_input("New Session Topic", placeholder="e.g., Mens Rea Evolution")
    if st.button("➕ Create New Session"):
        if new_session_name and new_session_name not in st.session_state.sessions:
            st.session_state.sessions[new_session_name] = []
            st.session_state.current_session = new_session_name
            st.rerun()
            
    # List active persistent sessions
    session_list = list(st.session_state.sessions.keys())
    st.session_state.current_session = st.selectbox("Switch Active Thread", session_list, index=session_list.index(st.session_state.current_session))
    
    st.markdown("---")
    st.header("📚 Repository Tracker")
    for law_name, folder_path in DATA_DIRS.items():
        files = os.listdir(folder_path) if os.path.exists(folder_path) else []
        if files:
            st.caption(f"**{law_name} Library ({len(files)} files):**")
            for f in files:
                st.caption(f"🛡️ Verified: {f}")
        else:
            st.caption(f"❌ {law_name} Empty")

    st.markdown("---")
    st.header("💬 Peer Suggestion Box")
    feedback_text = st.text_area("Found an error or drawback? Let us know anonymously:", placeholder="Type suggestion here...")
    if st.button("Submit Anonymous Feedback"):
        if feedback_text:
            with open(FEEDBACK_FILE, "a") as f:
                f.write(feedback_text + "\n---\n")
            st.success("Thank you! Feedback saved anonymously.")

# ==========================================
# 3. BACKGROUND REPOSITORY TEXT SCANNER ENGINE
# ==========================================
@st.cache_resource(show_spinner=False)
def load_local_knowledge_base():
    context_text = ""
    for law_name, folder_path in DATA_DIRS.items():
        if os.path.exists(folder_path):
            for file_name in os.listdir(folder_path):
                if file_name.endswith(".pdf"):
                    try:
                        reader = PdfReader(os.path.join(folder_path, file_name))
                        for i, page in enumerate(reader.pages[:40]): # Limits parsing depth for processing speed optimization
                            text = page.extract_text()
                            if text:
                                context_text += f"\n[Source File: {file_name} | Page Ref: {i+1}]\n{text}\n"
                    except Exception:
                        pass
    return context_text

# ==========================================
# 4. APP INTERFACE MODULE NAVIGATION TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(["💬 Jurisprudence & Consult Chat", "🧠 Rigorous IRAC Matrix Analyzer", "🎯 Repository Quiz Engine"])

# --- MODULE 1: INTERACTIVE SOCRATIC CONSULT CHAT ---
with tab1:
    st.subheader("Socratic Jurisprudence Hub & Conceptual Consult")
    
    # Active session reference mapping
    active_chat = st.session_state.sessions[st.session_state.current_session]
    
    if not active_chat:
        active_chat.append({"role": "assistant", "content": "Welcome to ClassroomBuddy. I am your specialized Jurisprudence and Criminal Law scholar. Set your key, toggle live research settings, and let's explore legal frameworks deeply."})

    for msg in active_chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Multi-modal media input pipeline interface
    uploaded_image = st.file_uploader("📸 Upload legal flowcharts, mind maps, or problem screenshots for parsing:", type=["jpg", "jpeg", "png"])

    if prompt := st.chat_input("Enter your jurisprudential query or legal question..."):
        active_chat.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        if not gemini_api_key:
            st.warning("Please configure your Gemini API Key in the sidebar control panel.")
        else:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                try:
                    client = genai.Client(api_key=gemini_api_key)
                    
                    with st.spinner("Analyzing uploaded text repositories..."):
                        local_context = load_local_knowledge_base()

                    # Systemic prompting enforcing priority order rules, Socratic execution, and task loops
                    system_instruction = (
                        "You are ClassroomBuddy AI, an elite legal scholar, expert legal philosopher, and Socratic Jurisprudence professor. "
                        "CRITICAL LEGAL PRIORITY ORDER:\n"
                        "1. When analyzing criminal law, ALWAYS state and apply the new criminal code provisions (BNS, BNSS, BSA) as the primary governing law first.\n"
                        "2. Treat any uploaded or referenced IPC/CrPC text strictly as historical evolution markers. Explain HOW the criminal philosophy transitioned from colonial deterrence to modern justice structures.\n\n"
                        "SOCRATIC INTERACTIVE INSTRUCTION:\n"
                        "- Break down dense concepts using clear analogies, foundational examples, explicit legal illustrations, and analytical case law precedents.\n"
                        "- At the absolute end of every response, you must append a structured 'Interactive Next Step Options Menu' using markdown. Give the user clear choices: "
                        "1. Ask you to simplify/explain the text again with a fresh analogy. "
                        "2. Provide an interactive scenario problem task to test if they truly understood the framework.\n\n"
                        f"--- LOCAL STUDENT TEXTBOOK POOL ---\n{local_context}"
                    )

                    # Dynamic structural configuration based on Google Search Grounding selection settings
                    config_args = {"system_instruction": system_instruction}
                    if research_mode:
                        config_args["tools"] = [{"google_search": {}}]

                    # Compile multi-modal inputs if a screenshot or image file is present
                    contents_payload = []
                    if uploaded_image:
                        import PIL.Image
                        img_data = PIL.Image.open(uploaded_image)
                        contents_payload.append(img_data)
                        contents_payload.append(f"[User uploaded an image file for analytical processing]. Additional query details: {prompt}")
                    else:
                        for item in active_chat[:-1]:
                            role = "user" if item["role"] == "user" else "model"
                            contents_payload.append({"role": role, "parts": [{"text": item["content"]}]})
                        contents_payload.append({"role": "user", "parts": [{"text": prompt}]})

                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=contents_payload,
                        config=types.GenerateContentConfig(**config_args)
                    )
                    
                    full_response = response.text
                    
                    # Append grounding metadata footnotes if search tool tracking is triggered
                    if research_mode and hasattr(response, 'candidates') and response.candidates:
                        try:
                            grounding_metadata = response.candidates[0].grounding_metadata
                            if grounding_metadata and hasattr(grounding_metadata, 'grounding_chunks'):
                                full_response += "\n\n---\n### 🌐 Live Research Verified References:\n"
                                for chunk in grounding_metadata.grounding_chunks:
                                    if hasattr(chunk, 'web') and chunk.web:
                                        full_response += f"- [{chunk.web.title}]({chunk.web.uri})\n"
                        except Exception:
                            pass

                    message_placeholder.markdown(full_response)
                    active_chat.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    st.error(f"Network processing cycle completed. Error text: {str(e)}")

# --- MODULE 2: RE-ENGINEERED IRAC MATRIX ANALYZER ENGINE ---
with tab2:
    st.subheader("Case Scenario Factual Matrix Evaluation Station")
    
    fact_scenario = st.text_area("Legal Problem Statement / Factual Matrix Input", height=180, placeholder="Paste your analytical case file details here...")
    focus_law = st.selectbox("Code Selection Focus", ["All Codes Combined", "BNS (Substantive Law)", "BNSS (Procedural Framework)", "BSA (Evidence Core)"])
    
    if st.button("Execute High-Rigor IRAC Evaluation", type="primary"):
        if not fact_scenario:
            st.error("Factual profile entries cannot be empty.")
        elif not gemini_api_key:
            st.error("API Authorization Key missing.")
        else:
            with st.spinner("Compiling cross-verification legal parameters..."):
                try:
                    client = genai.Client(api_key=gemini_api_key)
                    local_context = load_local_knowledge_base()
                    
                    irac_prompt = f"Analyze this problem: {fact_scenario}. Focus area targeted: {focus_law}."
                    
                    system_instruction = (
                        "You are ClassroomBuddy AI, an elite legal researcher. Generate a meticulous IRAC brief.\n"
                        "CRITICAL STRUCTURAL ORDER RULES:\n"
                        "1. Frame the core legal questions cleanly inside the ISSUE module.\n"
                        "2. Under the RULE section, cite the active statutory provisions of the new criminal laws (BNS/BNSS/BSA) as the primary supreme rules. Immediately follow it with a comprehensive transition note tracing it back to the historic old IPC/CrPC counterparts, detailing why the legislature adjusted the criminal philosophy wording.\n"
                        "3. In the ANALYSIS matrix, apply the case facts rigorously to each sub-element of the rule.\n"
                        "4. Deliver a concise final judgment inside the CONCLUSION.\n\n"
                        f"--- VERIFIED REFERENCE MATERIALS ---\n{local_context}"
                    )
                    
                    config_args = {"system_instruction": system_instruction}
                    if research_mode:
                        config_args["tools"] = [{"google_search": {}}]

                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=irac_prompt,
                        config=types.GenerateContentConfig(**config_args)
                    )
                    
                    st.markdown("---")
                    st.success("🔬 Analysis Successfully Verified and Compiled!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Assembly cycle halted. Technical feedback: {str(e)}")

# --- MODULE 3: AUTOMATED REPOSITORY QUIZ ENGINE ---
with tab3:
    st.subheader("🎯 Active Repository Interactive Quiz Mode")
    st.write("Generate a dynamic law quiz based directly on the textbooks and materials currently uploaded in your repository folders.")
    
    if st.button("Generate 3 High-Yield Scenario Questions", key="gen_quiz_btn"):
        if not gemini_api_key:
            st.error("API Key required to construct questions.")
        else:
            with st.spinner("Parsing repositories to build scenario examination modules..."):
                try:
                    client = genai.Client(api_key=gemini_api_key)
                    local_context = load_local_knowledge_base()
                    
                    quiz_prompt = (
                        "Generate 3 distinct multiple-choice question sets based directly on the criminal law mechanics or jurisprudence "
                        "found within the uploaded text data below. Each question must present a brief fact scenario problem, "
                        "provide 4 clear selectable options (A, B, C, D), and state the exact correct answer line alongside an explanation citing BNS standards.\n\n"
                        f"--- TEXT REPOSITORY ---\n{local_context or 'Use baseline criminal jurisprudence principles.'}"
                    )
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=quiz_prompt
                    )
                    st.session_state.quiz_questions = response.text
                except Exception as e:
                    st.error(f"Quiz construction loop interrupted: {str(e)}")
                    
    if st.session_state.quiz_questions:
        st.markdown("### 📝 Your Dynamic Evaluation Sheet")
        st.markdown(st.session_state.quiz_questions)
        st.info("Evaluate your options above, note your logic, and query ClassroomBuddy inside Tab 1 to verify your answer sheets instantly!")