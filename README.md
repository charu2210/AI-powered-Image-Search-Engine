# AI-Powered Image Search Engine

A natural-language image search system built using **CLIP**, cosine similarity, and **Streamlit**. It retrieves images from a local dataset based on text descriptions instead of filenames or exact keywords.

## Features

- Search images using natural-language queries.
- Generate 512-dimensional image and text embeddings using pretrained CLIP.
- Support image, caption, and hybrid search modes.
- Rank results using cosine similarity.
- Display Top-K results with filenames, captions (when available), and similarity scores.
- Reuse previously generated image embeddings.
- Evaluate caption-to-image retrieval using Recall@K and Mean Reciprocal Rank (MRR).
- Use the system through a Streamlit interface or command line.

## Tech Stack

- Python
- PyTorch
- Hugging Face Transformers
- CLIP (`openai/clip-vit-base-patch32`)
- NumPy
- Streamlit
- Pillow
- Matplotlib

## How It Works

1. Images and their corresponding caption files are loaded.
2. CLIP converts images and captions into 512-dimensional embeddings.
3. The embeddings and their filename mappings are saved.
4. A text query is converted into an embedding.
5. Cosine similarity is used to compare the query with stored embeddings.
6. The most similar images are returned in ranked order.

### Search Modes

| Mode | Description |
|---|---|
| `image` | Compares the text query with image embeddings. |
| `caption` | Compares the query with available caption embeddings. |
| `hybrid` | Combines image and caption similarity scores. If an image has no usable caption, its image score is used. |

## Project Structure

```text
AI-powered-Image-Search-Engine/
│
├── app.py
├── build_index.py
├── evaluate.py
├── search_cli.py
├── requirements.txt
├── README.md
│
├── src/
│   ├── config.py
│   ├── clip_encoder.py
│   └── search_engine.py
│
├── data/
│   └── README.md
│
├── outputs/
├── tests/
│   └── test_queries.txt
│
├── docs/
└── report/
```

## Dataset

The project was evaluated on a dataset containing:

| Item | Count |
|---|---:|
| Images | 1,000 |
| Caption files | 941 |
| Non-empty captions | 940 |
| Images without a caption file | 59 |
| Empty caption files | 1 |

The dataset itself is not included in this repository. The images, captions, generated embeddings, and other dataset-derived files are excluded.

Expected dataset structure:

```text
data/
├── images/
│   ├── 3001.jpg
│   ├── 3002.jpg
│   └── ...
└── captions/
    ├── 3001.txt
    ├── 3002.txt
    └── ...
```

Caption filenames should match the corresponding image filename, with a `.txt` extension.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/charu2210/AI-powered-Image-Search-Engine.git
cd AI-powered-Image-Search-Engine
```

### 2. Create a virtual environment

**Windows:**

```cmd
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Configure Dataset Paths

The dataset paths can be configured using environment variables.

**Windows CMD:**

```cmd
set VISMA_IMAGE_DIR=C:\path\to\images
set VISMA_CAPTION_DIR=C:\path\to\captions
set VISMA_OUTPUT_DIR=C:\path\to\outputs
```

**PowerShell:**

```powershell
$env:VISMA_IMAGE_DIR = "C:\path\to\images"
$env:VISMA_CAPTION_DIR = "C:\path\to\captions"
$env:VISMA_OUTPUT_DIR = "C:\path\to\outputs"
```

**macOS / Linux:**

```bash
export VISMA_IMAGE_DIR="/path/to/images"
export VISMA_CAPTION_DIR="/path/to/captions"
export VISMA_OUTPUT_DIR="/path/to/outputs"
```

These variables apply to the current terminal session.

## Build the Search Index

To generate image and caption embeddings:

```bash
python build_index.py
```

To reuse existing image embeddings, provide the folder containing `image_embeddings.npy` and `image_filenames.npy`:

```bash
python build_index.py --image-embeddings "/path/to/existing/image/embeddings"
```

To force image re-encoding:

```bash
python build_index.py --force
```

The generated index contains:

```text
outputs/
├── image_embeddings.npy
├── caption_embeddings.npy
├── image_filenames.npy
├── captions.json
└── dataset_stats.json
```

## Run the Application

After building the index:

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal, usually:

```text
http://localhost:8501
```

Enter a text description, select a search mode, choose the number of results, and view the retrieved images.

## Command-Line Search

```bash
python search_cli.py "a red double-decker bus"
```

Replace the example query with any image description.

## Evaluation

Run:

```bash
python evaluate.py
```

The evaluation script:

- Performs caption-to-image retrieval using the available dataset captions.
- Calculates Recall@1, Recall@5, Recall@10, MRR, and median rank.
- Runs sample natural-language queries.
- Saves Top-5 result visualizations and a text summary.

## Results

The completed evaluation run produced:

| Metric | Result |
|---|---:|
| Images indexed | 1,000 |
| Caption queries evaluated | 940 |
| Recall@1 | 24.47% |
| Recall@5 | 49.89% |
| Recall@10 | 62.13% |
| Mean Reciprocal Rank | 0.3700 |
| Median Rank | 6 |

These metrics represent caption-to-image retrieval performance on this dataset. They are not general CLIP accuracy figures or results from an independent test set.

## Limitations

- Retrieval quality depends on the pretrained CLIP model and the query wording.
- Fine-grained details, exact object counts, and text within images may not be retrieved reliably.
- Caption search depends on the availability of non-empty captions.
- The current implementation compares stored embeddings directly, which may become slow for very large datasets.
- Hybrid search uses a simple average of image and caption similarity scores.

## Future Improvements

- Integrate FAISS for faster similarity search on larger datasets.
- Improve hybrid ranking through score calibration or weighting.
- Add filters and more search controls.
- Evaluate performance on a larger and more diverse dataset.

## Notes

- CLIP is used as a pretrained model; it is not fine-tuned in this project.
- The model generates 512-dimensional image and text embeddings.
- Similarity scores indicate relative similarity and should not be interpreted as probabilities.
- The first run requires an internet connection to download the pretrained model.

## Author

**Charu Malik**

[GitHub Repository](https://github.com/charu2210/AI-powered-Image-Search-Engine)
