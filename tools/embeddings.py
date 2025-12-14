"""Compute embeddings for chunks.

By default this uses sentence-transformers locally as a reliable fallback.
If you prefer to use Ollama + nomic-embed-text, modify `get_embeddings` accordingly.

Usage:
  python tools/embeddings.py --input data/chunks.jsonl --output data/chunks_emb.jsonl
"""
import argparse
import json
from pathlib import Path
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


def load_chunks(path: Path):
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            yield json.loads(line)


def get_embeddings(texts: List[str], model_name: str = MODEL_NAME):
    model = SentenceTransformer(model_name)
    embs = model.encode(texts, convert_to_numpy=True)
    return embs.tolist()


def main(input_path: str, output_path: str):
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # load texts
    recs = list(load_chunks(input_path))
    texts = [r["text"] for r in recs]

    print(f"Computing embeddings for {len(texts)} chunks using {MODEL_NAME}...")
    embs = get_embeddings(texts)

    with output_path.open("w", encoding="utf-8") as fh:
        for r, e in zip(recs, embs):
            out = {
                "id": r["id"],
                "text": r["text"],
                "metadata": r.get("metadata", {}),
                "embedding": e,
            }
            fh.write(json.dumps(out, ensure_ascii=False) + "\n")

    print(f"Wrote embeddings to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/chunks.jsonl")
    parser.add_argument("--output", default="data/chunks_emb.jsonl")
    args = parser.parse_args()
    main(args.input, args.output)
