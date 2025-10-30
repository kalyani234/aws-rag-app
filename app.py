import streamlit as st
import time
from modules.models import create_llama3_model
from modules.vectorstore import load_vector_store
from modules.qa_chain import get_response_with_prompt


# --------------------------------------------------------------
# PAGE CONFIG + STYLING
# --------------------------------------------------------------
st.set_page_config(page_title="Document Q&A with Llama 3", layout="wide", page_icon="🦙")

st.markdown("""
<style>
.main { background-color: #0d1117; color: #e6edf3; font-family: "Inter", sans-serif; padding: 1rem 2rem; }
.stChatMessage { border-radius: 18px; margin: 10px 0; padding: 1.2rem; box-shadow: 0 4px 12px rgba(0,0,0,0.2); transition: all 0.3s ease-in-out; }
.stChatMessage:hover { transform: scale(1.01); }
.stChatMessage[data-testid="stChatMessage-user"] { background: linear-gradient(135deg, #111827, #1e293b); border: 1px solid #00b4d8; }
.stChatMessage[data-testid="stChatMessage-assistant"] { background: linear-gradient(135deg, #1e1e1e, #232323); border: 1px solid #3a3f44; }
.stTextInput > div > div > input { background-color: #161b22 !important; color: #e6edf3 !important; border: 1px solid #00b4d8 !important; border-radius: 10px; padding: 0.6rem; }
.stButton > button { background: linear-gradient(90deg, #00b4d8, #0096c7); color: white !important; border-radius: 10px; font-weight: 600; padding: 0.6rem 1.2rem; border: none; transition: background 0.3s ease-in-out; }
.stButton > button:hover { background: linear-gradient(90deg, #0096c7, #0077b6); }
h1, h2, h3, h4, h5, h6 { color: #00b4d8; font-weight: 700; }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------------------
# HEADER + SIDEBAR
# --------------------------------------------------------------
st.header("🦙 Document Q&A with Llama 3")

with st.sidebar:
    st.markdown("### ⚙️ Model Configuration")
    max_tokens = st.slider("Max tokens (response length):", 256, 2048, 1024, step=128)
    temperature = st.slider("Temperature (creativity):", 0.0, 1.0, 0.5, step=0.1)
    st.markdown("---")
    st.info(f"**Model:** Meta Llama 3 8B Instruct\n**Tokens:** {max_tokens}\n**Temperature:** {temperature}")
    st.markdown("### 📄 Source")
    st.caption("AWS Guidance PDF — 7,253 chunks indexed in PostgreSQL via PGVector.")
    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.experimental_rerun()


# --------------------------------------------------------------
# LOAD VECTOR STORE
# --------------------------------------------------------------
vector_store = load_vector_store()

if "messages" not in st.session_state:
    st.session_state.messages = []


# --------------------------------------------------------------
# DISPLAY CHAT HISTORY
# --------------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🤖"):
        st.markdown(msg["content"])


# --------------------------------------------------------------
# TYPING ANIMATION
# --------------------------------------------------------------
def stream_text(text: str):
    container = st.empty()
    typed = ""
    for char in text:
        typed += char
        container.markdown(typed)
        time.sleep(0.008)  # typing speed


# --------------------------------------------------------------
# HANDLE USER INPUT
# --------------------------------------------------------------
if user_question := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_question)

    with st.spinner("🤖 Llama 3 is generating a detailed answer..."):
        try:
            llm = create_llama3_model(max_tokens=max_tokens, temperature=temperature)
            answer = get_response_with_prompt(llm, vector_store, user_question)
        except Exception as e:
            answer = f"**Error:** {e}"

    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant", avatar="🤖"):
        stream_text(answer)


# --------------------------------------------------------------
# FOOTER
# --------------------------------------------------------------
st.markdown("""
<hr style="border: 0.5px solid #2f3338;">
<p style="text-align:center; color:gray;">
Built with ❤️ by <b>Navya Kalyani</b> · Powered by <b>Llama 3</b> on <b>AWS Bedrock</b>
</p>
""", unsafe_allow_html=True)
