"""STEP 4: testing and evaluation.   Run:  python evaluate.py

Part A  Caption-to-image retrieval test: use each caption as a query and check whether CLIP
        ranks the matching image in the top 1 / 5 / 10.   (saves outputs/metrics.json)
        Image embeddings are never built from captions, so this is a fair test of image mode.
        It is NOT general model accuracy: the captions are the dataset's own and one caption can fit
        several similar images. Do not run this test in caption/hybrid mode (the query would match its own text).
Part B  Runs the queries in tests/test_queries.txt and saves a picture of the top-5
        results for each one in outputs/results/   (you look at them and judge them).
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

from src import config
from src.search_engine import SearchEngine


def caption_to_image_test(engine):
    idx = np.where(engine.has_caption)[0]
    sims = engine.caption_emb[idx] @ engine.image_emb.T          # (n_captions, n_images)
    # rank of the true image for each caption (1 = best)
    true_scores = sims[np.arange(len(idx)), idx]
    ranks = (sims > true_scores[:, None]).sum(axis=1) + 1
    metrics = {
        "num_images": len(engine.filenames),
        "num_caption_queries": int(len(idx)),
        "recall@1": float((ranks <= 1).mean()),
        "recall@5": float((ranks <= 5).mean()),
        "recall@10": float((ranks <= 10).mean()),
        "mean_reciprocal_rank": float((1.0 / ranks).mean()),
        "median_rank": float(np.median(ranks)),
    }
    return metrics


def save_result_grid(query, results, out_path):
    fig, axes = plt.subplots(1, len(results), figsize=(3.2 * len(results), 3.6))
    for ax, r in zip(np.atleast_1d(axes), results):
        ax.imshow(Image.open(r["path"]).convert("RGB"))
        ax.set_title(f"{r['filename']}\n{r['score']:.3f}", fontsize=9)
        ax.axis("off")
    fig.suptitle(f"Query: {query}")
    fig.tight_layout()
    fig.savefig(out_path, dpi=100)
    plt.close(fig)


def main():
    engine = SearchEngine()
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("Part A: caption-to-image test")
    metrics = caption_to_image_test(engine)
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")
    with open(config.METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=2)

    first = config.IMAGE_DIR / engine.filenames[0]
    if not first.exists():
        raise SystemExit(f"Images not found in {config.IMAGE_DIR}. Set VISMA_IMAGE_DIR to your image folder.")

    print("\nPart B: test queries")
    queries = [q.strip() for q in open("tests/test_queries.txt", encoding="utf-8") if q.strip()]
    lines = []
    for n, q in enumerate(queries, 1):
        res = engine.search(q, top_k=5, mode="image")
        save_result_grid(q, res, config.RESULTS_DIR / f"query_{n:02d}.png")
        lines.append(f"{n}. {q}: " + ", ".join(f"{r['filename']} ({r['score']:.3f})" for r in res))
        print(" ", lines[-1])
    (config.RESULTS_DIR / "results.txt").write_text("\n".join(lines), encoding="utf-8")
    print("\nSaved pictures to", config.RESULTS_DIR)


if __name__ == "__main__":
    main()
