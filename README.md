# AI-Powered Image Search Engine

Type a sentence like *"a thatched roof cottage"* and get the most similar images from the dataset.
Built with **CLIP** (a model that understands both text and images) during the VISMA Lab internship, IIT Bhubaneswar.

## How it works (4 steps)

    captions (.txt) ─┐
                     ├─> CLIP embeddings ─> saved in outputs/ ─┐
    images (.jpg)  ──┘                                         ├─> cosine similarity ─> Top-K images
    your text query ───────> CLIP text embedding ──────────────┘

1. CLIP turns every image (and every caption) into a list of 512 numbers (an *embedding*).
2. Your query is turned into 512 numbers the same way.
3. We compare the query with every image using cosine similarity (higher = more similar).
4. The best K images are shown.

## Project structure

    ├── build_index.py        STEP 1  create embeddings from images + captions
    ├── search_cli.py         STEP 2  quick search in the terminal
    ├── app.py                STEP 3  demo web app (Streamlit)
    ├── evaluate.py           STEP 4  testing + accuracy numbers + result pictures
    ├── src/
    │   ├── config.py         paths and settings
    │   ├── clip_encoder.py   loads CLIP, makes embeddings
    │   └── search_engine.py  similarity search
    ├── tests/test_queries.txt  queries used by evaluate.py
    ├── data/                 YOUR images + captions (NOT on GitHub)
    ├── outputs/              embeddings, metrics, result pictures (made by the scripts)
    └── docs/                 installation, workflow, usage, GitHub guide

## Quick start

    pip install -r requirements.txt
    # put images in data/images/ and captions in data/captions/   (see data/README.md)
    python build_index.py          # a few minutes on CPU
    streamlit run app.py           # opens the demo in your browser

Already have image embeddings (for example from Week 4)? Reuse them, only the captions are encoded:

    python build_index.py --image-embeddings path/to/folder_with_image_embeddings.npy

Data in another folder (e.g. Google Drive)? Set `VISMA_IMAGE_DIR`, `VISMA_CAPTION_DIR`, `VISMA_OUTPUT_DIR` (see docs/COLAB.md).

More detail: [docs/INSTALLATION.md](docs/INSTALLATION.md) · [docs/USAGE.md](docs/USAGE.md) · [docs/WORKFLOW.md](docs/WORKFLOW.md) · [docs/GITHUB_GUIDE.md](docs/GITHUB_GUIDE.md)

## Search modes

| Mode | Compares the query with | Use when |
|---|---|---|
| image (default) | image embeddings | normal visual search |
| caption | caption embeddings | you want to match the written description |
| hybrid | average of both | best of both; images with no caption fall back to image score |

## Results

Run `python evaluate.py`. It prints Recall@1/5/10 and saves a picture of the top-5 results for every test query in `outputs/results/`.

## Limitations

- CLIP ViT-B/32 is small and sometimes confuses fine details (counting, colours, small objects).
- Similarity scores are low (about 0.2–0.3) even for good matches. That is normal for CLIP. Look at the ranking, not the number.
- Images without a caption can only be found in image mode.

## Confidentiality

The images and captions belong to the institute's confidential dataset. They are **not** included, and `.gitignore` also blocks every file made from them (embeddings, `captions.json`, result pictures). Never upload them to a public repository. Folder layout: `data/README.md`.

## Final report and slides

After `build_index.py`, `evaluate.py` and a screenshot of the app:

    pip install python-docx python-pptx
    python report/build_deliverables.py --github https://github.com/<you>/<repo> --screenshot app.png

This writes `report/Project_Report.docx` and `report/Project_Presentation.pptx` from your real results.
