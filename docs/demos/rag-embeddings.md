# Demo: RAG with Embeddings

Build a **Retrieval-Augmented Generation** system: store documents in a vector database, retrieve relevant context, and use an LLM to answer questions grounded in your documents.

## What It Does

This demo:
1. Loads documents (PDFs, Markdown, plain text) from a directory
2. Splits them into chunks and generates embeddings using ChromaDB (in-memory)
3. Stores chunks + embeddings in the vector database
4. Takes a user query and retrieves the top-K most relevant chunks
5. Passes retrieved context to gpt-5.2 for synthesis

### Example

**Documents in `demos/rag-embeddings/docs/`:**
- `architecture.md` — system design overview
- `api-reference.md` — endpoint documentation
- `troubleshooting.md` — common issues and fixes

**User Query:** "How do I fix a timeout error?"

**System:**
1. Embeds the query: "How do I fix a timeout error?"
2. Searches the vector store: Returns chunks from `troubleshooting.md` and `architecture.md`
3. Passes to gpt-5.2: "Answer this based on the context: [chunks]. Question: How do I fix a timeout error?"
4. **Output:** "Timeouts usually occur when... (synthesized answer grounded in your docs)"

## Goal

Learn:
- How embeddings enable semantic search (not keyword matching)
- Building a RAG pipeline (load → split → embed → retrieve → synthesize)
- Why RAG is critical for grounding LLM responses in your knowledge base
- Cost-effective use of models: embeddings are cheap, synthesis is medium-cost

## How to Run

```bash
uv run python demos/rag-embeddings/main.py
```

Interactive mode:
```bash
$ uv run python demos/rag-embeddings/main.py --interactive

Loading documents from docs/...
✓ Loaded 3 files
✓ Split into 42 chunks
✓ Generated embeddings

Enter a question (or 'quit' to exit):
> How do I fix a timeout error?

Top 3 relevant chunks:
1. [troubleshooting.md:15] "Timeouts occur when requests exceed..."
2. [architecture.md:22] "The default timeout is configured..."
3. [api-reference.md:8] "See Timeout Handling section..."

Generating answer with gpt-5.2...

Answer: Timeout errors typically occur when... (full synthesis)
```

Batch mode (preloaded questions):
```bash
uv run python demos/rag-embeddings/main.py --batch demos/rag-embeddings/sample_queries.txt
```

## Code Structure

```
demos/rag-embeddings/
├── main.py                  # Entry point (interactive + batch)
├── document_loader.py       # Load PDFs, Markdown, text files
├── chunker.py               # Split documents into overlapping chunks
├── embeddings.py            # ChromaDB vector store management
├── retriever.py             # Semantic search over stored vectors
├── synthesizer.py           # LLM-based answer generation (gpt-5.2)
├── docs/                    # Sample documents
│   ├── architecture.md
│   ├── api-reference.md
│   └── troubleshooting.md
└── sample_queries.txt       # Example questions for batch mode
```

## Embedding Implementation

Currently, ChromaDB uses **in-memory embeddings** (fast, zero-cost, suitable for small document sets).

When `text-embedding-3-large` is deployed, you can switch to:

```python
# Future: Replace in-memory with text-embedding-3-large
from azure.openai import AzureOpenAI

client = AzureOpenAI(...)
embeddings = client.embeddings.create(
    model="text-embedding-3-large",
    input=texts
)
```

### Why ChromaDB Today?

- **No external dependency** — entirely in-memory and DevPod-local
- **Fast development** — test RAG logic without waiting for embeddings API
- **Fallback path** — works until text-embedding-3-large deploys

## The Routing Lesson

RAG doesn't require expensive models:

- **Embeddings:** Cheap (low-dimensional vectors)
- **Retrieval:** Free (vector search algorithm)
- **Synthesis:** Medium-cost (gpt-5.2 or gpt-5-mini, depending on response complexity)

**Avoid:** Using gpt-5.4 for RAG synthesis (overkill reasoning for a summarization task).
**Prefer:** gpt-5.2 (balanced cost/quality) or gpt-5-mini (ultra-cheap, still good at reading context).

## Extending This Demo

### Add Your Own Documents

Copy documents into `demos/rag-embeddings/docs/` and re-run:
```bash
uv run python demos/rag-embeddings/main.py
```

The system auto-discovers and re-indexes.

### Persistent Vector Store

Currently, the ChromaDB store is in-memory (cleared on exit). To persist:

1. Create `.gitignore` entry: `demos/rag-embeddings/.chroma/`
2. Update `embeddings.py` to use persistent ChromaDB:
   ```python
   db = chromadb.PersistentClient(path=".chroma")
   ```
3. The vector store now survives between runs

### Hybrid Retrieval

Combine semantic search with keyword matching:
```python
# Current: semantic search only
results = retriever.semantic_search(query, top_k=5)

# Future: keyword + semantic
keyword_results = retriever.keyword_search(query)
semantic_results = retriever.semantic_search(query)
combined = merge_and_rerank(keyword_results, semantic_results)
```

---

Next: [Data Analysis](data-analysis.md) to see Pandas workflows with chart output.
