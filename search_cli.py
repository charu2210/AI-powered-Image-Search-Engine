"""STEP 2 (quick test in terminal).   Run:  python search_cli.py "a red bus on a street" """
import sys
from src.search_engine import SearchEngine

query = " ".join(sys.argv[1:]) or input("Query: ")
engine = SearchEngine()
for rank, r in enumerate(engine.search(query, top_k=5), 1):
    print(f"{rank}. {r['filename']}  score={r['score']:.4f}  {r['caption'][:80]}")
