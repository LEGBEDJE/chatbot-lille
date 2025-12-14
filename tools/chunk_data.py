"""Chunk source texts using LangChain RecursiveCharacterTextSplitter.

Usage:
  python tools/chunk_data.py --input_dir data --output data/chunks.jsonl
"""
import argparse
import json
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter


def load_text_files(input_dir: Path):
    for p in sorted(input_dir.glob("*.txt")):
        yield p.name, p.read_text(encoding="utf-8")


def main(input_dir: str, output: str, chunk_size: int = 1000, chunk_overlap: int = 200):
    input_dir = Path(input_dir)
    out_path = Path(output)
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    out_path.parent.mkdir(parents=True, exist_ok=True)

    idx = 0
    with out_path.open("w", encoding="utf-8") as fh:
        for fname, text in load_text_files(input_dir):
            docs = splitter.split_text(text)
            for i, d in enumerate(docs):
                rec = {
                    "id": f"{fname}__{i}",
                    "text": d,
                    "metadata": {"source": fname, "chunk": i},
                }
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                idx += 1

    print(f"Wrote {idx} chunks to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", default="data", help="Directory with .txt files")
    parser.add_argument("--output", default="data/chunks.jsonl", help="JSONL output file")
    parser.add_argument("--chunk_size", type=int, default=1000)
    parser.add_argument("--chunk_overlap", type=int, default=200)
    args = parser.parse_args()
    main(args.input_dir, args.output, args.chunk_size, args.chunk_overlap)
