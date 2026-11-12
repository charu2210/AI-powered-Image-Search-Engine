"""Wraps CLIP so the rest of the project only calls encode_images / encode_texts."""
import numpy as np
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

from .config import MODEL_NAME


def _normalize(x):
    """Make every vector length 1, so dot product = cosine similarity."""
    return x / x.norm(dim=-1, keepdim=True)


class ClipEncoder:
    def __init__(self, model_name=MODEL_NAME):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = CLIPModel.from_pretrained(model_name).to(self.device).eval()
        self.processor = CLIPProcessor.from_pretrained(model_name)

    @torch.no_grad()
    def encode_images(self, image_paths, batch_size=32, progress=True):
        """Return an array of shape (num_images, 512)."""
        out = []
        for start in range(0, len(image_paths), batch_size):
            batch = image_paths[start:start + batch_size]
            images = [Image.open(p).convert("RGB") for p in batch]
            inputs = self.processor(images=images, return_tensors="pt")
            pixel_values = inputs["pixel_values"].to(self.device)
            pooled = self.model.vision_model(pixel_values=pixel_values).pooler_output
            feats = _normalize(self.model.visual_projection(pooled))
            out.append(feats.cpu().numpy())
            if progress:
                print(f"  images: {min(start + batch_size, len(image_paths))}/{len(image_paths)}")
        return np.concatenate(out)

    @torch.no_grad()
    def encode_texts(self, texts, batch_size=64):
        """Return an array of shape (num_texts, 512). Long texts are cut at 77 tokens."""
        out = []
        for start in range(0, len(texts), batch_size):
            batch = texts[start:start + batch_size]
            inputs = self.processor(text=batch, return_tensors="pt",
                                    padding=True, truncation=True, max_length=77)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            pooled = self.model.text_model(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"]).pooler_output
            feats = _normalize(self.model.text_projection(pooled))
            out.append(feats.cpu().numpy())
        return np.concatenate(out)
