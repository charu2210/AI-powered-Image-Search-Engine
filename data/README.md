# Data folder (private, never uploaded)

The dataset is confidential. Do not commit or share these files.

    data/images/     <- your images (.jpg / .jpeg / .png), e.g. 3001.jpg
    data/captions/   <- one .txt caption per image, same number, e.g. 3001.txt

Or keep them elsewhere (e.g. Google Drive) and set VISMA_IMAGE_DIR / VISMA_CAPTION_DIR (see docs/COLAB.md).
An image without a caption still works in image mode; it just has no caption search.
The app needs the ORIGINAL images to display results, even when image embeddings are reused.
