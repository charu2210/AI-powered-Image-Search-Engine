# Installation

You need Python 3.9+ and about 1 GB of free space (the CLIP model downloads once).

1. Open a terminal in the project folder.
2. (Recommended) create a virtual environment:

       python -m venv venv
       venv\Scripts\activate          # Windows
       source venv/bin/activate       # Mac / Linux

3. Install the libraries:

       pip install -r requirements.txt

4. Add your data:

       data/images/    -> 3001.jpg, 3002.jpg ...
       data/captions/  -> 3001.txt, 3002.txt ...

5. Build the search index (first run downloads CLIP):

       python build_index.py

Done when you see `Saved to ... outputs` and `image embedding shape: (N, 512)`.

## Common problems

| Problem | Fix |
|---|---|
| `OSError ... c10.dll` (Windows, on `import torch`) | Install the Microsoft Visual C++ Redistributable (x64), restart, then `pip install --force-reinstall torch`. Or run the project on Google Colab. |
| `No images found` | Images must be directly inside `data/images/`, not in a sub-folder. |
| `embeddings not found` | Run `python build_index.py` first. |
| Very slow | Normal on CPU (about 1–3 minutes per 1000 images is typical, slower on weak laptops). |
