# ai/chunking/scripts/test_chunker.py
import sys
import os
import random
from pathlib import Path

print("Current working directory:", os.getcwd())

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from backend.app.ai.chunking.chunker import chunk_text

def main():
    sample = ROOT / "Sem3DSAChapter1_api.txt"
    if not sample.exists():
        print("Put your extracted text into sample_text.txt at project root and re-run.")
        return

    raw = sample.read_text(encoding="utf-8")
    chunks = chunk_text(raw)

    total = len(chunks)
    print(f"\nTotal chunks: {total}")

    if total >= 5:
        start = random.randint(0, total - 5)
        print(f"\nShowing chunks {start+1} to {start+5}:\n")
        for i in range(start, start + 5):
            print(f"--- Chunk {i+1} ---\n{chunks[i]}\n")
    else:
        print("\nLess than 5 chunks available, printing all:\n")
        for i, c in enumerate(chunks, 1):
            print(f"--- Chunk {i} ---\n{c}\n")

if __name__ == "__main__":
    main()
