# Simple RAG Model

A retrieval-augmented chat assistant that answers questions about Insurellm from a local markdown knowledge base.

**Live demo:** _add your Streamlit Cloud link here_ — bring your own OpenAI API key.

## Stack

- Streamlit — chat UI
- LangChain + Chroma — retrieval
- OpenAI `gpt-4.1-nano` (chat) and `text-embedding-3-large` (embeddings)

## Setup

```bash
pip install -r requirements.txt
```

The app asks for an OpenAI API key in the sidebar. For local runs you can skip that prompt by putting the key in a `.env` file in the project root:

```
OPENAI_API_KEY=sk-...
```

## Run

```bash
streamlit run app.py
```

On the first run the app builds the vector store from `knowledge-base/` into `vector_db/`. Later runs reuse it. To rebuild manually:

```bash
python ingest.py
```

## Deploy to Streamlit Cloud

1. Push the repo to GitHub.
2. Create a new app at [share.streamlit.io](https://share.streamlit.io) pointing at `app.py`.

No secrets to configure — each visitor supplies their own OpenAI API key in the sidebar, so they pay for their own usage. The key is held in that visitor's session only and is never written to disk.

The knowledge base is committed, so the app builds its vector store on first boot.

## Files

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit chat interface |
| `answer.py` | Retrieval and answer generation |
| `ingest.py` | Loads `knowledge-base/`, chunks it, writes embeddings to `vector_db/` |
| `knowledge-base/` | Source markdown documents |
