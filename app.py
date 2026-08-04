import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv(override=True)

DB_NAME = Path(__file__).parent / "vector_db"

st.set_page_config(page_title="Insurellm Expert Assistant", page_icon="🏢", layout="wide")


@st.cache_resource(show_spinner="Building the knowledge base, this runs only once...")
def build_knowledge_base(_api_key):
    """
    Index the knowledge base on first use. The key is underscored so it stays out of the
    cache key: the store is built once per deployment, whoever happens to arrive first.
    """
    if not DB_NAME.exists():
        from ingest import create_chunks, create_embeddings, fetch_documents

        create_embeddings(create_chunks(fetch_documents()), api_key=_api_key)
    return True


with st.sidebar:
    st.header("Insurellm Expert Assistant")
    st.write("A retrieval-augmented chat assistant over the Insurellm knowledge base.")

    st.subheader("🔑 Your OpenAI API key")
    api_key = st.text_input(
        "OpenAI API key",
        type="password",
        placeholder="sk-...",
        label_visibility="collapsed",
        help="Used only for your own requests and never stored.",
    ).strip()
    st.caption(
        "Get one at [platform.openai.com/api-keys]"
        "(https://platform.openai.com/api-keys). "
        "It lives in your browser session only and is gone when you close the tab."
    )

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.context = []
        st.rerun()

api_key = api_key or os.getenv("OPENAI_API_KEY", "")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "context" not in st.session_state:
    st.session_state.context = []

st.title("🏢 Insurellm Expert Assistant")
st.caption("Ask me anything about Insurellm!")

if not api_key:
    st.info("👈 Enter your OpenAI API key in the sidebar to start chatting.")
    st.stop()

build_knowledge_base(api_key)

chat_column, context_column = st.columns(2)

with chat_column:
    st.subheader("💬 Conversation")
    transcript = st.container(height=600)
    for message in st.session_state.messages:
        transcript.chat_message(message["role"]).markdown(message["content"])

question = st.chat_input("Ask anything about Insurellm...")

if question:
    from answer import answer_question

    history = list(st.session_state.messages)
    st.session_state.messages.append({"role": "user", "content": question})
    transcript.chat_message("user").markdown(question)

    with transcript.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                answer, context = answer_question(question, history, api_key=api_key)
        except Exception as error:
            st.session_state.messages.pop()
            st.error(f"Request failed — check that your API key is valid and has credit.\n\n{error}")
            st.stop()
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.context = context

with context_column:
    st.subheader("📚 Retrieved Context")
    panel = st.container(height=600)
    if st.session_state.context:
        for doc in st.session_state.context:
            panel.markdown(f":orange[**Source:** {doc.metadata.get('source', 'unknown')}]")
            panel.markdown(doc.page_content)
            panel.divider()
    else:
        panel.markdown("*Retrieved context will appear here*")
