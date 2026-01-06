"""RAG pipeline: retrieval from Chroma + generation via Ollama.

This module provides `answer_query` which returns the generated answer and sources.
It uses sentence-transformers for query embeddings (same model as used for indexing).
"""
from typing import Any, Dict, List
import os
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from .test_llama import query_ollama

EMBED_MODEL_LOCAL = "all-MiniLM-L6-v2"
CHROMA_COLLECTION = os.environ.get("CHROMA_COLLECTION", "chatbot")


def _get_chroma_collection(collection_name: str = CHROMA_COLLECTION):
    # Use the same persistence directory as indexer (default ./chroma_db)
    persist_dir = os.environ.get("CHROMA_PERSIST_DIR", "./chroma_db")
    client = None
    try:
        client = chromadb.Client(persist_directory=str(persist_dir))
    except Exception:
        try:
            settings = Settings(chroma_db_impl="duckdb+parquet", persist_directory=str(persist_dir))
            client = chromadb.Client(settings)
        except Exception as e:
            raise RuntimeError(
                "Could not construct a Chroma client. If you have an old Chroma database, run 'pip install chroma-migrate' and use chroma-migrate to upgrade, see https://docs.trychroma.com/deployment/migration. Original error: "
                + str(e)
            )
    try:
        return client.get_collection(collection_name)
    except Exception:
        return client.create_collection(collection_name)


def _fallback_text_search(query: str, chunks_path: Path = Path("data/chunks.jsonl"), top_k: int = 3):
    """Fallback: simple text search in chunks.jsonl (no embeddings)."""
    if not chunks_path.exists():
        return []
    query_lower = query.lower()
    results = []
    with chunks_path.open(encoding="utf-8") as fh:
        for line in fh:
            rec = json.loads(line)
            text = rec.get("text", "").lower()
            score = text.count(query_lower)  # simple word count as score
            if score > 0:
                results.append((rec["id"], rec["text"], rec.get("metadata", {}), score))
    # sort by score desc, take top_k
    results.sort(key=lambda x: x[3], reverse=True)
    return results[:top_k]


def _get_query_embedding(text: str):
    model = SentenceTransformer(EMBED_MODEL_LOCAL)
    emb = model.encode([text])[0]
    return emb.tolist()


def answer_query(query: str, top_k: int = 3, model: str = "Mistral") -> Dict[str, Any]:
    """Retrieve top_k chunks from Chroma and call Ollama to generate an answer."""
    try:
        coll = _get_chroma_collection()
        q_emb = _get_query_embedding(query)
        results = coll.query(query_embeddings=[q_emb], n_results=top_k)
        docs = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        ids = results.get("ids", [[]])[0]
        distances = results.get("distances", [[]])[0]  # add distances if available
        chunks = list(zip(ids, docs, metadatas, distances or [None]*len(ids)))
    except Exception as e:
        print(f"Chroma retrieval failed: {e}. Using fallback text search.")
        chunks = _fallback_text_search(query, top_k=top_k)
        results = {"fallback": True, "error": str(e)}

    # build context
    context_parts = []
    for chunk in chunks:
        if len(chunk) == 4:  # chroma: id, doc, meta, dist
            cid, doc, meta, dist = chunk
            source = meta.get("source", cid) if meta else cid
            context_parts.append(f"Source: {source}\n{doc}")
        else:  # fallback: id, doc, meta, score
            cid, doc, meta, score = chunk
            source = meta.get("source", cid) if meta else cid
            context_parts.append(f"Source: {source}\n{doc}")
    context = "\n---\n".join(context_parts) if context_parts else ""

    prompt = f"You are a helpful assistant. Use the following context to answer the question.\n\nCONTEXT:\n{context}\n\nQuestion: {query}\nAnswer concisely and mention which sources you used."

    resp = query_ollama(prompt, model=model, stream=False)

    # try to extract text-like response, supporting common Ollama shapes
    answer = None
    if isinstance(resp, dict):
        # check common keys
        for k in ("response", "text", "output", "answer"):
            if k in resp and isinstance(resp[k], str):
                answer = resp[k]
                break
        # sometimes the useful string is nested under 'response' -> 'output' or similar
        if answer is None and "response" in resp and isinstance(resp["response"], dict):
            # flatten possible nested structures
            nested = resp["response"]
            for k in ("text", "output", "answer"):
                if k in nested and isinstance(nested[k], str):
                    answer = nested[k]
                    break

    if answer is None:
        # fallback to stringifying the whole response
        answer = str(resp)

    return {"answer": answer, "chunks": chunks, "raw_llm": resp, "retrieval": results}
