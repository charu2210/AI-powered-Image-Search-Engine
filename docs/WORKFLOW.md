# Project Workflow

| Week | What was done | File |
|---|---|---|
| 3 | Built an MLP in PyTorch on MNIST (basics of training a neural network) | notebooks (not part of the final app) |
| 4 | Generated CLIP image embeddings (512 numbers per image) | `src/clip_encoder.py` |
| 5 | Text query -> CLIP text embedding -> cosine similarity -> Top-5 images | `src/search_engine.py` |
| 8 | Combined everything into one project: index builder, search, web app, evaluation, docs | whole repo |

## Pipeline in code

1. `build_index.py`
   - lists images in `data/images/`, reads matching captions from `data/captions/`
   - `ClipEncoder.encode_images` -> `outputs/image_embeddings.npy`
   - `ClipEncoder.encode_texts` -> `outputs/caption_embeddings.npy`
   - saves filenames and captions so that row *i* always means the same image
2. `SearchEngine.search(query)`
   - encodes the query, takes the dot product with all embeddings (vectors are normalized, so this equals cosine similarity), returns the top K
3. `app.py` shows the results; `evaluate.py` measures them.

## Design choices

- **Filenames are saved with the embeddings**, so images and embeddings can never get out of order.
- **Embeddings are computed once** and stored; a search only encodes the short query.
- **Normalized vectors**, so no extra similarity library is needed (NumPy only).
