"""Index embeddings into a local ChromaDB collection.

Usage:
  python tools/index_chroma.py --input data/chunks_emb.jsonl --persist_dir ./chroma_db --collection chatbot
"""
import argparse
import json
from pathlib import Path

import chromadb


def load_embs(path: Path):
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            yield json.loads(line)


def main(input_path: str, persist_dir: str = "./chroma_db", collection_name: str = "chatbot"):
    input_path = Path(input_path)
    client = chromadb.Client()

    # create or get collection
    try:
        collection = client.get_collection(collection_name)
    except Exception:
        collection = client.create_collection(collection_name)

    ids = []
    docs = []
    metadatas = []
    embeddings = []

    for rec in load_embs(input_path):
        ids.append(rec["id"]) 
        docs.append(rec["text"]) 
        metadatas.append(rec.get("metadata", {}))
        embeddings.append(rec.get("embedding"))

    if ids:
        # add to collection
        collection.add(ids=ids, documents=docs, metadatas=metadatas, embeddings=embeddings)
        print(f"Indexed {len(ids)} records into Chroma collection '{collection_name}'")
    else:
        print("No records to index")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/chunks_emb.jsonl")
    parser.add_argument("--persist_dir", default="./chroma_db")
    parser.add_argument("--collection", default="chatbot")
    args = parser.parse_args()
    main(args.input, args.persist_dir, args.collection)
