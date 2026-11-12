"""Loads the saved embeddings and answers text queries."""
import json
import numpy as np

from . import config


class SearchEngine:
    def __init__(self, encoder=None):
        for f in (config.IMAGE_EMB_FILE, config.FILENAMES_FILE,
                  config.CAPTION_EMB_FILE, config.CAPTIONS_FILE):
            if not f.exists():
                raise FileNotFoundError(f"{f.name} not found. Run:  python build_index.py")
        self.image_emb = np.load(config.IMAGE_EMB_FILE)
        self.filenames = [str(x) for x in np.load(config.FILENAMES_FILE)]
        self.caption_emb = np.load(config.CAPTION_EMB_FILE)
        with open(config.CAPTIONS_FILE, encoding="utf-8") as f:
            self.captions = json.load(f)          # {filename: caption text}
        # which images have a caption
        self.has_caption = np.array([bool(self.captions.get(n)) for n in self.filenames])
        self._encoder = encoder

    @property
    def encoder(self):
        """CLIP is loaded only when the first search happens."""
        if self._encoder is None:
            from .clip_encoder import ClipEncoder
            self._encoder = ClipEncoder()
        return self._encoder

    def search(self, query, top_k=config.DEFAULT_TOP_K, mode="image"):
        """
        mode = "image"   : compare query with image embeddings (default)
               "caption" : compare query with caption embeddings
               "hybrid"  : average of both (images without caption use image score only)
        Returns a list of dicts: filename, path, caption, score.
        """
        q = self.encoder.encode_texts([query])[0]
        img_scores = self.image_emb @ q
        cap_scores = self.caption_emb @ q

        if mode == "image":
            scores = img_scores
        elif mode == "caption":
            scores = np.where(self.has_caption, cap_scores, -1.0)
        elif mode == "hybrid":
            scores = np.where(self.has_caption, (img_scores + cap_scores) / 2, img_scores)
        else:
            raise ValueError("mode must be image, caption or hybrid")

        top = np.argsort(scores)[::-1][:top_k]
        return [{
            "filename": self.filenames[i],
            "path": str(config.IMAGE_DIR / self.filenames[i]),
            "caption": self.captions.get(self.filenames[i], ""),
            "score": float(scores[i]),
        } for i in top]
