# Usage

## 1. Web app (demo)

    streamlit run app.py

- Type a query or click an example in the sidebar.
- Choose how many results (1–12) and the search mode (image / hybrid / caption).
- Each result shows the image, filename, similarity score and caption.

## 2. Terminal

    python search_cli.py "a red bus on a street"

## 3. Testing and evaluation (needs the original images for the result pictures)

    python evaluate.py

Creates:
- `outputs/metrics.json` : Recall@1, Recall@5, Recall@10, MRR
- `outputs/results/query_XX.png` : top-5 images for each query in `tests/test_queries.txt`
- `outputs/results/results.txt` : the same results as text

To test your own queries, add lines to `tests/test_queries.txt`.

## 4. Use it from Python

    from src.search_engine import SearchEngine
    engine = SearchEngine()
    for r in engine.search("a quiet street", top_k=5, mode="image"):
        print(r["filename"], r["score"])

## Tips for good queries

- Describe the scene, like a caption: "a white cottage with a thatched roof".
- Short object names work too: "bus", "bridge".
- Very specific details (numbers, small text, exact colours) are CLIP's weak spot.
