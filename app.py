import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv(override=True)

DB_NAME = Path(__file__).parent / "vector_db"

st.set_page_config(page_title="Insurellm Expert Assistant", page_icon="🏢", layout="wide")


def load_api_key():
    """Streamlit Cloud provides the key through secrets; locally it comes from .env."""
    try:
        if "OPENAI_API_KEY" in st.secrets:
            os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    except FileNotFoundError:
        pass


@st.cache_resource(show_spinner="Preparing the knowledge base...")
def load_answerer():
    """Build the vector store on first run, then hand back the RAG entry point."""
    if not DB_NAME.exists():
        from ingest import create_chunks, create_embeddings, fetch_documents

        create_embeddings(create_chunks(fetch_documents()))

    from answer import answer_question

    return answer_question


load_api_key()
answer_question = load_answerer()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "context" not in st.session_state:
    st.session_state.context = []

st.title("🏢 Insurellm Expert Assistant")
st.caption("Ask me anything about Insurellm!")

chat_column, context_column = st.columns(2)

with chat_column:
    st.subheader("💬 Conversation")
    transcript = st.container(height=600)
    for message in st.session_state.messages:
        transcript.chat_message(message["role"]).markdown(message["content"])

question = st.chat_input("Ask anything about Insurellm...")

if question:
    history = list(st.session_state.messages)
    st.session_state.messages.append({"role": "user", "content": question})
    transcript.chat_message("user").markdown(question)

    with transcript.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer, context = answer_question(question, history)
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

with st.sidebar:
    st.header("Insurellm Expert Assistant")
    st.write("A retrieval-augmented chat assistant over the Insurellm knowledge base.")
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.context = []
        st.rerun()
