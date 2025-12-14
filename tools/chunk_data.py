"""Chunk source texts using LangChain RecursiveCharacterTextSplitter.

Usage:
  python tools/chunk_data.py --input_dir data --output data/chunks.jsonl
"""
import argparse
import json
from pathlib import Path

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    HAS_LANGCHAIN = True
except Exception:
    # Provide a lightweight fallback splitter to avoid failing when langchain
    # is not installed. This splitter works on character windows with overlap.
    HAS_LANGCHAIN = False

    class RecursiveCharacterTextSplitter:
        def __init__(self, chunk_size=1000, chunk_overlap=200):
            self.chunk_size = int(chunk_size)
            self.chunk_overlap = int(chunk_overlap)

        def split_text(self, text: str):
            text = text.replace("\r\n", "\n")
            L = len(text)
            if L == 0:
                return []
            chunks = []
            start = 0
            while start < L:
                end = start + self.chunk_size
                if end >= L:
                    chunk = text[start:L]
                    chunks.append(chunk.strip())
                    break
                # try to cut at last newline or space to avoid breaking words
                window = text[start:end]
                cut = window.rfind("\n")
                if cut == -1:
                    cut = window.rfind(" ")
                if cut <= 0:
                    cut = end
                else:
                    cut = start + cut
                chunk = text[start:cut]
                chunks.append(chunk.strip())
                start = cut - self.chunk_overlap
                if start < 0:
                    start = 0
            return [c for c in chunks if c]


def load_text_files(input_dir: Path):
    for p in sorted(input_dir.glob("*.txt")):
        yield p.name, p.read_text(encoding="utf-8")


def main(input_dir: str, output: str, chunk_size: int = 1000, chunk_overlap: int = 200):
    input_dir = Path(input_dir)
    out_path = Path(output)
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    if not HAS_LANGCHAIN:
        print("Warning: langchain not installed — using fallback splitter. Install with: pip install langchain")

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
