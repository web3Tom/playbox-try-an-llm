# RAG Query Demo

## Goal

Demonstrates Retrieval-Augmented Generation (RAG) by grounding LLM responses in retrieved context. Uses `text-embedding-3-large` for semantic similarity and ChromaDB for in-memory vector storage.

## How to Run

```bash
uv run python demos/rag-embeddings/rag_query.py
```

## How It Works

1. **Ingest Documents**: Sample policy documents are embedded using `text-embedding-3-large` and stored in an in-memory ChromaDB collection.
2. **Query**: User query is embedded and compared against stored documents.
3. **Retrieve**: Top-1 most similar document is retrieved.
4. **Answer**: `gpt-5-mini` generates a response using only the retrieved context.

## Vector Store

The document collection is stored **entirely in-memory** — no persistent storage or external database. Data is lost when the script exits.

Sample documents are hardcoded in the script. To use real documents, place them in `data/` and update the ingest logic.

## Environment Variables

- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI deployment endpoint
- `AZURE_OPENAI_API_KEY`: Azure OpenAI API key

## Dependencies

- `chromadb` (vector database)
- `openai` (Azure SDK)
