"""
In-memory RAG demo using ChromaDB and Azure OpenAI embeddings.

Demonstrates grounding LLM responses in retrieved context using text-embedding-3-large.
Documents are stored in-memory and queried based on semantic similarity.

Env vars:
  AZURE_OPENAI_ENDPOINT: Azure OpenAI deployment endpoint
  AZURE_OPENAI_API_KEY: Azure OpenAI API key
"""

import logging
import os

from dotenv import load_dotenv
from openai import AzureOpenAI, OpenAIError

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

try:
    import chromadb
except ImportError:
    logger.error("chromadb not installed. Install via: uv add chromadb")
    raise


def init_azure_client() -> AzureOpenAI | None:
    """Initialize Azure OpenAI client from environment variables."""
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")

    if not endpoint or not api_key:
        logger.error("Missing Azure credentials: AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_API_KEY not set")
        return None

    try:
        return AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview"),
        )
    except Exception as e:
        logger.error(f"Failed to initialize Azure OpenAI client: {e}")
        return None


def get_embedding(client: AzureOpenAI, text: str) -> list[float]:
    """Fetch embedding for text using text-embedding-3-large."""
    try:
        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-large"
        )
        return response.data[0].embedding
    except OpenAIError as e:
        logger.error(f"Embedding API error: {e}")
        raise


def setup_collection(client: AzureOpenAI) -> chromadb.Collection:
    """Create in-memory ChromaDB collection and ingest sample documents."""
    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection(
        name="policy_docs",
        metadata={"hnsw:space": "cosine"}
    )

    documents = [
        "Employees are permitted up to $500 per year for home office equipment.",
        "Travel requests exceeding $1000 require VP approval.",
        "The standard core working hours are 10:00 AM to 3:00 PM local time.",
    ]

    for idx, doc in enumerate(documents):
        try:
            embedding = get_embedding(client, doc)
            collection.add(
                ids=[f"doc_{idx}"],
                embeddings=[embedding],
                documents=[doc],
                metadatas=[{"source": "policy_handbook"}]
            )
            logger.info(f"Ingested document {idx}: {doc[:50]}...")
        except Exception as e:
            logger.error(f"Failed to ingest document {idx}: {e}")
            raise

    return collection


def query_and_answer(client: AzureOpenAI, collection: chromadb.Collection, query: str):
    """Query collection, retrieve context, and generate answer."""
    try:
        query_embedding = get_embedding(client, query)
        logger.info(f"Query: {query}")

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=1
        )

        if not results["documents"] or not results["documents"][0]:
            logger.warning("No documents retrieved.")
            return

        context = results["documents"][0][0]
        logger.info(f"Retrieved context: {context}")

        response = client.responses.create(
            model="gpt-5-mini",
            instructions="You are a helpful assistant. Answer only using the provided context.",
            input=f"Context: {context}\n\nQuestion: {query}",
        )

        answer = response.output_text
        logger.info(f"Answer: {answer}")
        print(f"\nFinal Answer:\n{answer}")

    except Exception as e:
        logger.error(f"Query/answer error: {e}")
        raise


def main():
    """Run RAG demo."""
    load_dotenv()
    client = init_azure_client()
    if not client:
        logger.error("Cannot proceed without Azure OpenAI client.")
        return

    logger.info("Setting up in-memory RAG collection...")
    collection = setup_collection(client)

    query = "What is the policy for buying a new desk chair for my house?"
    query_and_answer(client, collection, query)


if __name__ == "__main__":
    main()
