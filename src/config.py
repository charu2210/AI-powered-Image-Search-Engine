"""All settings in one place.

Folders can be changed WITHOUT editing code by setting environment variables
(useful for Google Drive / Colab):
    VISMA_IMAGE_DIR    folder with the images
    VISMA_CAPTION_DIR  folder with the caption .txt files
    VISMA_OUTPUT_DIR   folder where embeddings / results are saved
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _path(env_name, default):
    value = os.environ.get(env_name)
    return Path(value).expanduser() if value else default


IMAGE_DIR = _path("VISMA_IMAGE_DIR", ROOT / "data" / "images")
CAPTION_DIR = _path("VISMA_CAPTION_DIR", ROOT / "data" / "captions")
OUTPUT_DIR = _path("VISMA_OUTPUT_DIR", ROOT / "outputs")
RESULTS_DIR = OUTPUT_DIR / "results"

# Files used by the search engine
IMAGE_EMB_FILE = OUTPUT_DIR / "image_embeddings.npy"
CAPTION_EMB_FILE = OUTPUT_DIR / "caption_embeddings.npy"
FILENAMES_FILE = OUTPUT_DIR / "image_filenames.npy"
CAPTIONS_FILE = OUTPUT_DIR / "captions.json"
METRICS_FILE = OUTPUT_DIR / "metrics.json"
STATS_FILE = OUTPUT_DIR / "dataset_stats.json"

MODEL_NAME = "openai/clip-vit-base-patch32"
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")
DEFAULT_TOP_K = 5
