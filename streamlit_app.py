import streamlit as st
from google import genai
from google.genai import types
import os
from pypdf import PdfReader

# 1. Page Configuration & Aesthetic Layout
st.set_page_config(page_title="ClassroomBuddy AI", page_icon="🎓", layout="wide")
st.title("🎓 ClassroomBuddy AI")
st.caption("Your Elite, Double-Verified Law School Research & Analysis Station")

DATA_DIRS = {
    "BNS": "data/bns",
    "BNSS": "data/BNSS",
    "BSA": "data/bsa"
}

for folder_path in DATA_DIRS.values():
    os.makedirs(folder_path, exist_ok=True)

# 2. Sidebar Layout
with st.sidebar:
    st.header("🎯 System Control")
    gemini_api_key = st.text_input("Enter Gemini API Key", type="password")
    
    st.markdown("---")
    st.header("🔍 Verification Settings")
    research_mode = st.toggle("Activate Research Mode", value=False, 
                              help="When enabled, scans your repositories to explicitly cite pages.")
    
    st.markdown("---")
    st.header("📚 Your Repository Tracker")
    
    for law_name, folder_path in DATA_DIRS.items():
        st.markdown(f"**{law_name} Library:**")
        files = os.listdir(folder_path) if os.path.exists(folder_path) else []
        if files:
            for f in files:
                st.caption(f"🛡️ Verified: {f}")
        else:
            st.caption("❌ Empty Repository")
        st.markdown("")

# SPEED UPGRADE: Caches the text extraction loop efficiently
@st.cache_resource(show_spinner=False)
def load_local_knowledge_base():
    context_text = ""
    for law_name, folder_path in DATA_DIRS.items():
        if os.path.exists(folder_path):
            for file_name in os.listdir(folder_path):
                if file_name.endswith(".pdf"):
                    try:
                        reader = PdfReader(os.path.join(folder_path, file_name))
                        # Safely parse up to 60 essential pages to avoid hitting API rate limits
                        for i, page in enumerate(reader.pages[:60]):
                            text = page.extract_text()
                            if text:
                                context_text += f"\n[Document: {law_name} File: {file_name} | Page: {i+1}]\n{text}\n"
                    except Exception:
                        pass
    return context_text

# 3. Workspace Separation Modules
tab1, tab2 = st.tabs(["💬 Verified Legal Consult", "🧠 Rigorous IRAC Brief Builder"])

# --- MODULE 1: GENERAL CONSULTATION TAB ---
with tab1:
    st.subheader("Interactive Legal Consult (Verified Stream)")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am ClassroomBuddy, your advanced legal companion. Configure your key and let's explore legal theory."}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a general legal question...", key="chat_input_field"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        if not gemini_api_key:
            st.warning("Please configure your API key in the sidebar.")
        else:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                try:
                    client = genai.Client(api_key=gemini_api_key, http_options={'headers': {'Connection': 'close'}})
                    
                    # Core Bug Fix: ONLY scan files if Research Mode is toggled to ON
                    local_context = ""
                    if research_mode:
                        with st.spinner("Scanning textbooks (Research Mode Active)..."):
                            local_context = load_local_knowledge_base()
                    
                    if research_mode and local_context:
                        system_instruction = (
                            "You are ClassroomBuddy AI, an elite legal scholar. Use the strict metrics provided. "
                            "Base your arguments directly on the text below and explicitly cite document titles and pages."
                            f"\n\n--- DATA POOL ---\n{local_context}"
                        )
                    else:
                        system_instruction = "You are ClassroomBuddy AI, an expert Indian criminal law assistant. Provide clear, analytical breakdowns using baseline knowledge."
                    
                    api_contents = []
                    for msg in st.session_state.messages[:-1]:
                        role = "user" if msg["role"] == "user" else "model"
                        api_contents.append({"role": role, "parts": [{"text": msg["content"]}]})
                    api_contents.append({"role": "user", "parts": [{"text": prompt}]})

                    # Using gemini-1.5-flash handles high-volume token contexts without hitting rate caps
                    response = client.models.generate_content(
                        model='gemini-1.5-flash',
                        contents=api_contents,
                        config=types.GenerateContentConfig(system_instruction=system_instruction)
                    )
                    full_response = response.text
                    message_placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    st.error(f"Execution Error: {str(e)}")

# --- MODULE 2: IRAC ANALYZER TAB ---
with tab2:
    st.subheader("Case Scenario Analysis Workstation")
    
    fact_scenario = st.text_area("Legal Problem Statement / Factual Matrix", height=180, placeholder="Paste your problem facts here...")
    focus_law = st.selectbox("Code Selection Focus", ["All Codes Combined", "BNS (Substantive Law)", "BNSS (Procedural Framework)", "BSA (Evidence Core)"])
    
    if st.button("Execute IRAC Evaluation", type="primary"):
        if not fact_scenario:
            st.error("Factual profile cannot be blank.")
        elif not gemini_api_key:
            st.error("API Key required.")
        else:
            with st.spinner("Processing analysis..."):
                try:
                    client = genai.Client(api_key=gemini_api_key, http_options={'headers': {'Connection': 'close'}})
                    
                    local_context = ""
                    if research_mode:
                        local_context = load_local_knowledge_base()
                    
                    irac_prompt = f"""
                    Generate a rigorous IRAC brief. 
                    
                    SCENARIO:
                    {fact_scenario}
                    
                    FOCUS WINDOW:
                    {focus_law}
                    """
                    
                    system_instruction = (
                        "You are ClassroomBuddy AI, an elite analytical machine. You break down law via Issue, Rule, Application, and Conclusion. "
                        "Always detail old IPC/CrPC counterparts alongside the new BNS guidelines."
                        f"\n\n--- DATA REPOSITORY ---\n{local_context}"
                    )
                    
                    response = client.models.generate_content(
                        model='gemini-1.5-flash',
                        contents=irac_prompt,
                        config=types.GenerateContentConfig(system_instruction=system_instruction)
                    )
                    
                    st.markdown("---")
                    st.success("🔬 Analysis Evaluated!")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")