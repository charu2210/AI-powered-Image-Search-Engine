"""STEP 3: demo web app.   Run:  streamlit run app.py"""
import os

import streamlit as st
from PIL import Image

from src.search_engine import SearchEngine

st.set_page_config(page_title="AI Image Search", layout="wide")
st.title("AI-Powered Image Search")
st.caption("Type what you are looking for. CLIP finds the most similar images in the dataset.")


@st.cache_resource
def load_engine():
    return SearchEngine()


try:
    engine = load_engine()
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()

EXAMPLES = ["a red double-decker bus", "a thatched roof cottage", "people walking on a busy street",
            "a quiet empty road", "a bridge over a river"]

with st.sidebar:
    st.header("Settings")
    top_k = st.slider("Number of results", 1, 12, 6)
    mode = st.radio("Search using", ["image", "hybrid", "caption"],
                    help="image = compare with pictures, caption = compare with caption text, "
                         "hybrid = both combined")
    st.write("Try an example:")
    for ex in EXAMPLES:
        if st.button(ex):
            st.session_state["query"] = ex

query = st.text_input("Search query", key="query", placeholder="e.g. a thatched roof cottage")

if query:
    with st.spinner("Searching..."):
        results = engine.search(query, top_k=top_k, mode=mode)
    cols = st.columns(3)
    for i, r in enumerate(results):
        with cols[i % 3]:
            if os.path.exists(r["path"]):
                img = Image.open(r["path"]).convert("RGB")
                img.thumbnail((500, 500))
                st.image(img)
            else:
                st.warning("Image file not found. Check the image folder (VISMA_IMAGE_DIR).")
            st.markdown(f"**#{i + 1}  {r['filename']}**  \nscore: `{r['score']:.3f}`")
            if r["caption"]:
                st.caption(r["caption"])
