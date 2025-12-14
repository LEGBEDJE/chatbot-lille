"""Index embeddings into a local ChromaDB collection.

Usage:
  python tools/index_chroma.py --input data/chunks_emb.jsonl --persist_dir ./chroma_db --collection chatbot
"""
import argparse
import json
from pathlib import Path

import chromadb
from chromadb.config import Settings


def load_embs(path: Path):
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            yield json.loads(line)


def main(input_path: str, persist_dir: str = "./chroma_db", collection_name: str = "chatbot"):
    input_path = Path(input_path)
    persist_dir = str(persist_dir)

    # Try new client constructor first (no Settings) for newer chromadb versions,
    # passing `persist_directory` if supported. Fall back to the Settings-based
    # constructor for older versions.
    client = None
    try:
        # Newer chromadb may accept persist_directory directly
        client = chromadb.Client(persist_directory=persist_dir)
    except Exception:
        try:
            settings = Settings(chroma_db_impl="duckdb+parquet", persist_directory=persist_dir)
            client = chromadb.Client(settings)
        except Exception as e:
            raise RuntimeError(
                "Could not construct a Chroma client. If you have an old Chroma database, run 'pip install chroma-migrate' and use chroma-migrate to upgrade, see https://docs.trychroma.com/deployment/migration. Original error: "
                + str(e)
            )

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
        # persist to disk
        try:
            client.persist()
        except Exception:
            # some chroma builds persist automatically or expose different API
            pass

        print(f"Indexed {len(ids)} records into Chroma collection '{collection_name}' (persisted to {persist_dir})")
    else:
        print("No records to index")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/chunks_emb.jsonl")
    parser.add_argument("--persist_dir", default="./chroma_db")
    parser.add_argument("--collection", default="chatbot")
    args = parser.parse_args()
    main(args.input, args.persist_dir, args.collection)
