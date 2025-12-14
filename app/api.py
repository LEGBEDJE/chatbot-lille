from typing import Any, Dict, Optional
import logging

from fastapi import FastAPI
from pydantic import BaseModel

from .test_llama import query_ollama
from .rag import answer_query

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Chatbot Univ Lille API")


class ChatRequest(BaseModel):
    query: str
    top_k: int = 3


class ChatResponse(BaseModel):
    answer: Optional[str]
    raw: Dict[str, Any] = {}
    sources: Optional[Any] = None


def _extract_text(resp: Dict[str, Any]) -> str:
    """Try to extract a human-readable text from an Ollama response."""
    if not isinstance(resp, dict):
        return str(resp)

    # common keys
    if "text" in resp and isinstance(resp["text"], str):
        return resp["text"]
    if "output" in resp and isinstance(resp["output"], str):
        return resp["output"]

    # Ollama sometimes returns 'result' with content array
    result = resp.get("result")
    if isinstance(result, list) and len(result) > 0:
        first = result[0]
        content = first.get("content") or first.get("outputs")
        if isinstance(content, list):
            texts = []
            for c in content:
                if isinstance(c, dict) and c.get("type") == "output_text":
                    texts.append(c.get("text", ""))
            if texts:
                return "\n".join(texts)

    # fallback: stringify
    return str(resp)


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Simple chat endpoint that forwards the prompt to a local Ollama instance.

    This is a minimal implementation intended as a starting point for a RAG pipeline.
    It currently does NOT perform retrieval; it calls the LLM directly.
    """
    prompt = f"Réponds de façon concise. Question:\n{req.query}\n"

    # Use RAG pipeline: retrieval + generation
    rag_res = answer_query(req.query, top_k=req.top_k, model="Mistral")
    answer = rag_res.get("answer")
    chunks = rag_res.get("chunks")

    return ChatResponse(answer=answer, raw={}, sources=chunks)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)
