"""RAG pipeline: retrieval from Chroma + generation via Ollama.

This module provides `answer_query` which returns the generated answer and sources.
It uses sentence-transformers for query embeddings (same model as used for indexing).
"""
from typing import Any, Dict, List
import os
from sentence_transformers import SentenceTransformer
import chromadb
from .test_llama import query_ollama

EMBED_MODEL_LOCAL = "all-MiniLM-L6-v2"
CHROMA_COLLECTION = os.environ.get("CHROMA_COLLECTION", "chatbot")


def _get_chroma_collection(collection_name: str = CHROMA_COLLECTION):
    client = chromadb.Client()
    try:
        return client.get_collection(collection_name)
    except Exception:
        return client.create_collection(collection_name)


def _get_query_embedding(text: str):
    model = SentenceTransformer(EMBED_MODEL_LOCAL)
    emb = model.encode([text])[0]
    return emb.tolist()


def answer_query(query: str, top_k: int = 3, model: str = "Mistral") -> Dict[str, Any]:
    """Retrieve top_k chunks from Chroma and call Ollama to generate an answer."""
    coll = _get_chroma_collection()
    q_emb = _get_query_embedding(query)

    results = coll.query(query_embeddings=[q_emb], n_results=top_k)

    docs = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    ids = results.get("ids", [[]])[0]

    # build context
    context = "\n---\n".join([f"Source: {m.get('source') if m else ids[i]}\n{docs[i]}" for i in range(len(docs))])

    prompt = f"You are a helpful assistant. Use the following context to answer the question.\n\nCONTEXT:\n{context}\n\nQuestion: {query}\nAnswer concisely and mention which sources you used."

    resp = query_ollama(prompt, model=model, stream=False)

    # try to extract text-like response
    answer = None
    if isinstance(resp, dict):
        # common keys
        for k in ("text", "output"):
            if k in resp and isinstance(resp[k], str):
                answer = resp[k]
                break
    if answer is None:
        answer = str(resp)

    return {"answer": answer, "chunks": list(zip(ids, docs, metadatas))}
