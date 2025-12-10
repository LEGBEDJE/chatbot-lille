import os
import requests
import logging

logging.basicConfig(level=logging.INFO)


def query_ollama(prompt, model="Mistral", stream=False, host=None, timeout=10):
    """Query a local Ollama instance. Returns parsed JSON or an error dict."""
    if host is None:
        host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

    url = f"{host}/api/generate"
    try:
        resp = requests.post(
            url,
            json={"model": model, "prompt": prompt, "stream": stream},
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logging.error("Ollama request failed: %s", e)
        return {"error": str(e)}


if __name__ == "__main__":
    print(query_ollama("the capital of France?"))