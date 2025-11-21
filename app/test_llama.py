import requests

import requests

def query_ollama(prompt, model="Mistral", stream=False):
    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": stream},
            timeout=10
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print(query_ollama("the capital of France?"))