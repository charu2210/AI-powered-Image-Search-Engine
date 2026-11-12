"""STEP 1: create the search index in outputs/.

Usage
  python build_index.py                              first run: encodes images AND captions
  python build_index.py --image-embeddings DIR       REUSE image embeddings you already made
                                                     (DIR has image_embeddings.npy + image_filenames.npy,
                                                     e.g. your Week 4 output folder); only captions are encoded
  python build_index.py --force                      re-encode the images even if they exist
"""
import argparse
import json
import shutil
from pathlib import Path

import numpy as np

from src import config


def load_image_embeddings(folder):
    """Load + check embeddings made earlier. Row i belongs to filenames[i]."""
    folder = Path(folder)
    emb_file, names_file = folder / "image_embeddings.npy", folder / "image_filenames.npy"
    for f in (emb_file, names_file):
        if not f.exists():
            raise SystemExit(f"Missing {f}")
    emb = np.load(emb_file).astype("float32")
    names = [str(n) for n in np.load(names_file)]
    if emb.ndim != 2 or emb.shape[1] != 512:
        raise SystemExit(f"Expected embeddings of shape (N, 512), got {emb.shape}")
    if emb.shape[0] != len(names):
        raise SystemExit(f"{emb.shape[0]} embeddings but {len(names)} filenames: files do not match")
    if len(set(names)) != len(names):
        raise SystemExit("image_filenames.npy contains duplicate names")
    emb /= np.linalg.norm(emb, axis=1, keepdims=True)      # make sure length = 1
    return emb, names


def read_caption(stem):
    path = config.CAPTION_DIR / f"{stem}.txt"
    if not path.exists():
        return None                                         # no caption file
    return path.read_text(encoding="utf-8", errors="ignore").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image-embeddings", help="folder with existing image_embeddings.npy + image_filenames.npy")
    ap.add_argument("--force", action="store_true", help="re-encode images even if embeddings exist")
    args = ap.parse_args()

    from src.clip_encoder import ClipEncoder          # imported late: heavy
    encoder = ClipEncoder()
    print("Device:", encoder.device)

    # ---- 1. image embeddings: reuse or create
    reuse_dir = args.image_embeddings
    if not reuse_dir and not args.force and config.IMAGE_EMB_FILE.exists() and config.FILENAMES_FILE.exists():
        reuse_dir = config.OUTPUT_DIR
    if reuse_dir and not args.force:
        print(f"Reusing image embeddings from {reuse_dir}")
        image_emb, filenames = load_image_embeddings(reuse_dir)
    else:
        image_paths = sorted(p for p in config.IMAGE_DIR.iterdir()
                             if p.suffix.lower() in config.IMAGE_EXTENSIONS) if config.IMAGE_DIR.exists() else []
        if not image_paths:
            raise SystemExit(f"No images in {config.IMAGE_DIR}. Set VISMA_IMAGE_DIR or use --image-embeddings")
        filenames = [p.name for p in image_paths]
        print("Encoding images...")
        image_emb = encoder.encode_images(image_paths)

    # ---- 2. check the images are available for DISPLAY (not needed to build)
    if config.IMAGE_DIR.exists():
        absent = [n for n in filenames if not (config.IMAGE_DIR / n).exists()]
        if absent:
            print(f"WARNING: {len(absent)} embedded images are not in {config.IMAGE_DIR} "
                  f"(e.g. {absent[:3]}). They cannot be shown in results.")
    else:
        print(f"NOTE: image folder {config.IMAGE_DIR} not found. The index will work, but the app "
              "needs the images to display results.")

    # ---- 3. captions
    raw = {n: read_caption(Path(n).stem) for n in filenames}
    captions = {n: (c or "") for n, c in raw.items()}
    no_file = [n for n, c in raw.items() if c is None]
    empty = [n for n, c in raw.items() if c == ""]
    usable = [n for n in filenames if captions[n]]
    caption_files = len(filenames) - len(no_file)
    stats = {"images": len(filenames), "caption_files": caption_files,
             "non_empty_captions": len(usable), "images_without_caption_file": len(no_file),
             "empty_caption_files": len(empty), "empty_caption_names": empty}
    print(f"Images: {stats['images']} | caption files: {caption_files} | usable captions: {len(usable)} "
          f"| no caption file: {len(no_file)} | empty caption file: {len(empty)} {empty}")

    print("Encoding captions...")
    caption_emb = np.zeros_like(image_emb)                  # zero row = no caption
    idx = [i for i, n in enumerate(filenames) if captions[n]]
    caption_emb[idx] = encoder.encode_texts([captions[filenames[i]] for i in idx])

    # ---- 4. save
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    np.save(config.IMAGE_EMB_FILE, image_emb)
    np.save(config.CAPTION_EMB_FILE, caption_emb)
    np.save(config.FILENAMES_FILE, np.array(filenames))
    with open(config.CAPTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(captions, f, indent=1)
    with open(config.STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)
    print("Saved to", config.OUTPUT_DIR, "| image embeddings:", image_emb.shape)


if __name__ == "__main__":
    main()
