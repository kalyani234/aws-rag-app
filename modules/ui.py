import streamlit as st
from .ui_markdown import GLOBAL_CSS, HEADER_HTML, FOOTER_HTML
from .ui_texts import TEXTS

def inject_global_styles():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

def render_header():
    st.markdown(HEADER_HTML, unsafe_allow_html=True)

def render_footer():
    st.markdown(FOOTER_HTML, unsafe_allow_html=True)

def sidebar_controls():
    with st.sidebar:
        st.markdown(f"<div class='aws-side-title'>{TEXTS['sidebar_model_settings']}</div>", unsafe_allow_html=True)
        max_tokens = st.slider("Max tokens:", 256, 2048, 1024, step=128)
        temperature = st.slider("Temperature:", 0.0, 1.0, 0.5, step=0.1)

        st.markdown(f"<div class='aws-side-title'>{TEXTS['sidebar_chat_controls']}</div>", unsafe_allow_html=True)
        cleared_chat = st.button(TEXTS["sidebar_clear"])

    return max_tokens, temperature, cleared_chat
