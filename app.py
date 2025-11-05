import time
import streamlit as st
from modules.models import create_llama3_model, create_nova_model
from modules.vectorstore import load_vector_store
from modules.qa_chain import get_response_with_prompt
from modules.ui import inject_global_styles, render_header, render_footer, sidebar_controls
from modules.ui_texts import TEXTS

st.set_page_config(page_title=TEXTS["app_title"], page_icon=TEXTS["page_icon"], layout="wide")

inject_global_styles()
render_header()

# Sidebar config
max_tokens, temperature, cleared_chat = sidebar_controls()

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_model" not in st.session_state:
    st.session_state.selected_model = None

if cleared_chat:
    st.session_state.messages = []
    st.rerun()

# Vector store
vector_store = load_vector_store()

# Model picker
st.markdown(f"### {TEXTS['choose_model']}")
col_a, col_b = st.columns(2)
with col_a:
    if st.button(TEXTS["model_llama"]):
        st.session_state.selected_model = "llama3"
with col_b:
    if st.button(TEXTS["model_nova"]):
        st.session_state.selected_model = "nova"

selected_model = st.session_state.selected_model
if selected_model:
    model_name = TEXTS["active_llama"] if selected_model == "llama3" else TEXTS["active_nova"]
    st.success(f"✅ Active model: {model_name}")
else:
    st.info(TEXTS["select_model_tip"])

# Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👩🏻‍💻" if msg["role"] == "user" else "🟧"):
        st.markdown(msg["content"])

def stream_text(text: str):
    container = st.empty()
    typed = ""
    for ch in text:
        typed += ch
        container.markdown(typed)
        time.sleep(0.006)

# Chat box
prompt = st.chat_input(TEXTS["chat_placeholder"])

if prompt and selected_model:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👩🏻‍💻"):
        st.markdown(prompt)

    with st.spinner(f"🟧 {model_name} {TEXTS['processing_text']}"):
        try:
            llm = (
                create_llama3_model(max_tokens=max_tokens, temperature=temperature)
                if selected_model == "llama3"
                else create_nova_model(max_tokens=max_tokens, temperature=temperature)
            )
            result = get_response_with_prompt(llm, vector_store, prompt)
            answer = result.get("answer", TEXTS["no_response"])
            sources = result.get("sources", [])
        except Exception as e:
            answer = f"{TEXTS['error_prefix']} {e}"
            sources = []

    reply = answer
    if sources:
        reply += "\n\n---\n" + TEXTS["sources_heading"] + "\n" + "\n".join([f"- {s}" for s in sources])

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant", avatar="🟧"):
        stream_text(reply)

render_footer()
