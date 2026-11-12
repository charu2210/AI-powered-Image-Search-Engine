# Running with Google Drive / Colab

Use this when the dataset lives in Google Drive. Upload the project folder (without data) to Drive too.

    from google.colab import drive
    drive.mount('/content/drive')

    %cd /content/drive/MyDrive/VISMA_Image_Search_Final     # your project folder
    !pip install -q -r requirements.txt

    import os
    os.environ["VISMA_IMAGE_DIR"]   = "/content/drive/MyDrive/25IN08"
    os.environ["VISMA_CAPTION_DIR"] = "/content/drive/MyDrive/25IN08/captions"
    os.environ["VISMA_OUTPUT_DIR"]  = "/content/drive/MyDrive/VISMA_Output"

    # reuse the image embeddings you already made (folder with image_embeddings.npy + image_filenames.npy)
    !python build_index.py --image-embeddings "/content/drive/MyDrive/CLIP_Project_Output"

    # STOP here and check the printed counts (1000 images, 941 caption files, 940 usable, 59 none, 1 empty)
    # Only then run:  !python evaluate.py

Environment variables set with os.environ are inherited by `!python ...`.
To run the Streamlit app, download the outputs folder and images to your PC and run `streamlit run app.py` there,
or set the three variables in your terminal (Windows: `set VISMA_IMAGE_DIR=...`, Mac/Linux: `export VISMA_IMAGE_DIR=...`).
