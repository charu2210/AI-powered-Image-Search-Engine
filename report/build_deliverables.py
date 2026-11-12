"""Builds the final Project_Report.docx and Project_Presentation.pptx from your REAL results.

Run AFTER:  python build_index.py   and   python evaluate.py   and taking a screenshot of the app.

    python report/build_deliverables.py --github https://github.com/<you>/<repo> --screenshot my_app.png

Needs:  pip install python-docx python-pptx pillow
It stops with a clear message if anything is missing, so no empty placeholders end up in the files.
Optional: write report/discussion.txt (your own observations after looking at the result pictures);
it is added to the report under "Observations".
"""
import argparse
import json
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src import config  # noqa: E402


def fail(msg):
    raise SystemExit("ERROR: " + msg)


# ----------------------------------------------------------------- inputs
ap = argparse.ArgumentParser()
ap.add_argument("--github", required=True, help="your repository URL")
ap.add_argument("--screenshot", required=True, help="screenshot of the running Streamlit app")
ap.add_argument("--name", default="Charu Malik")
ap.add_argument("--examples", nargs="+", type=int, default=[1, 2, 3],
                help="numbers of the query_XX.png pictures to show (default 1 2 3)")
ap.add_argument("--out", default=str(ROOT / "report"))
a = ap.parse_args()

if not re.match(r"^https://github\.com/[^/\s]+/[^/\s]+/?$", a.github):
    fail("--github must look like https://github.com/username/repository")
shot = Path(a.screenshot)
if not shot.exists():
    fail(f"screenshot not found: {shot}")
for f in (config.METRICS_FILE, config.STATS_FILE, config.RESULTS_DIR / "results.txt"):
    if not f.exists():
        fail(f"{f} not found. Run build_index.py and evaluate.py first.")
M = json.load(open(config.METRICS_FILE))
S = json.load(open(config.STATS_FILE))
example_pics = []
for n in a.examples:
    p = config.RESULTS_DIR / f"query_{n:02d}.png"
    if not p.exists():
        fail(f"{p} not found")
    example_pics.append(p)
queries = []   # (query, top1 file, top1 score)
for line in (config.RESULTS_DIR / "results.txt").read_text(encoding="utf-8").splitlines():
    m = re.match(r"\d+\.\s+(.*?):\s+(\S+) \(([\d.]+)\)", line)
    if m:
        queries.append((m.group(1), m.group(2), float(m.group(3))))
user_notes = ""
dfile = Path(a.out) / "discussion.txt"
if dfile.exists():
    user_notes = dfile.read_text(encoding="utf-8").strip()

pct = lambda x: f"{100 * x:.1f}%"
N, NC = M["num_images"], M["num_caption_queries"]
chance1, chance10 = 1 / N, 10 / N
best = max(queries, key=lambda q: q[2]); worst = min(queries, key=lambda q: q[2])

discussion = (
    f"In this caption-to-image retrieval test (not a measure of general accuracy), using {NC} captions as queries over {N} images, the matching image was ranked first {pct(M['recall@1'])} of the time, "
    f"in the top 5 {pct(M['recall@5'])} and in the top 10 {pct(M['recall@10'])} (mean reciprocal rank {M['mean_reciprocal_rank']:.3f}, "
    f"median rank {M['median_rank']:.0f}). Random ranking would give about {pct(chance1)} at rank 1 and {pct(chance10)} in the top 10, "
    f"so the system is far better than chance. These numbers are conservative: many images in this dataset show similar street scenes, "
    f"so another image can be a valid match for a caption even when it is not the one the caption was written for. "
    f"Across the {len(queries)} free-text test queries, the highest top-1 similarity was {best[2]:.3f} (\"{best[0]}\") and the lowest was "
    f"{worst[2]:.3f} (\"{worst[0]}\"). CLIP similarity scores are small in absolute terms, so the ranking is what matters.")

# ----------------------------------------------------------------- REPORT
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

d = Document()
sec = d.sections[0]
for m_ in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
    setattr(sec, m_, Inches(1))
d.styles["Normal"].font.name = "Calibri"; d.styles["Normal"].font.size = Pt(11)
for n, sz in (("Heading 1", 16), ("Heading 2", 13)):
    s = d.styles[n]; s.font.name = "Calibri"; s.font.size = Pt(sz); s.font.bold = True
    s.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)


def P(text="", bold=False, italic=False, align=None, size=None, space=6):
    p = d.add_paragraph(); r = p.add_run(text); r.bold = bold; r.italic = italic
    if size: r.font.size = Pt(size)
    if align is not None: p.alignment = align
    p.paragraph_format.space_after = Pt(space); return p


def B(items):
    for t in items:
        p = d.add_paragraph(style="List Bullet"); p.add_run(t); p.paragraph_format.space_after = Pt(2)


def T(header, rows, widths):
    t = d.add_table(rows=1, cols=len(header)); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]; c.text = ""; r = c.paragraphs[0].add_run(h); r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:fill"), "1F3A5F"); c._tc.get_or_add_tcPr().append(sh)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = str(v)
    for row in t.rows:
        for i, w in enumerate(widths): row.cells[i].width = Inches(w)
    d.add_paragraph().paragraph_format.space_after = Pt(2)


def FIG(path, caption, width=6.2):
    d.add_picture(str(path), width=Inches(width)); d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    P(caption, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=9)


for _ in range(5): P()
P("AI-Powered Image Search Engine", True, align=WD_ALIGN_PARAGRAPH.CENTER, size=28)
P("Text-to-Image Retrieval using CLIP", italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=16, space=30)
P("Final Project Report", True, align=WD_ALIGN_PARAGRAPH.CENTER, size=14, space=30)
P("Undergraduate Research Internship", align=WD_ALIGN_PARAGRAPH.CENTER)
P("VISMA Lab, IIT Bhubaneswar", align=WD_ALIGN_PARAGRAPH.CENTER)
P("Supervisor: Dr. Debi Prosad Dogra", align=WD_ALIGN_PARAGRAPH.CENTER, space=30)
P(f"Submitted by: {a.name}", True, align=WD_ALIGN_PARAGRAPH.CENTER)
P("B.Tech CSE (Data Science), Manipal University Jaipur", align=WD_ALIGN_PARAGRAPH.CENTER)
P(f"Code: {a.github}", align=WD_ALIGN_PARAGRAPH.CENTER)
d.add_page_break()

d.add_heading("1. Abstract", 1)
P("This project builds a search engine that finds images from a written description. A pretrained CLIP model converts every "
  "image and every caption into a 512-number vector (an embedding). A text query is converted the same way and cosine similarity "
  f"ranks the images from most to least similar. The system was tested on {N} images; "
  f"in a caption-to-image retrieval test (each caption used as a query), the correct image was found at rank 1 in {pct(M['recall@1'])} and within the top 10 in {pct(M['recall@10'])} of cases. "
  "The project includes an index builder, a command-line search, a Streamlit web app and an evaluation script.")

d.add_heading("2. Introduction and Objectives", 1)
P("Traditional image search depends on filenames or tags. Semantic search compares meaning: the query \"a quiet street\" can find a suitable "
  "photo even if those words appear nowhere in its filename. CLIP (Contrastive Language-Image Pre-training) makes this possible because its "
  "text and image encoders place matching text and images close together in one shared space.")
P("Objectives:", True)
B(["Generate CLIP embeddings for the full image dataset and its captions.",
   "Retrieve the Top-K most relevant images for any text query.",
   "Provide a simple demo application.",
   "Test the system and report retrieval quality.",
   "Document the code so that others can install and run it."])

d.add_heading("3. Dataset", 1)
P("The dataset contains street-scene and building photographs with one English caption per image, stored as a .txt file with the same "
  "number as the image (for example 3001.jpg and 3001.txt). The dataset is confidential to the institute and is not included in the public repository.")
empty_names = ", ".join(S.get("empty_caption_names", [])) or "none"
T(["Item", "Value"],
  [["Images", S["images"]],
   ["Caption files", S["caption_files"]],
   ["Usable (non-empty) captions", S["non_empty_captions"]],
   ["Images without a caption file", S["images_without_caption_file"]],
   ["Empty caption files", f"{S['empty_caption_files']} ({empty_names})"],
   ["Embedding size", "512 numbers per item (CLIP ViT-B/32)"]],
  [3.0, 3.5])
P("Images without a usable caption remain searchable in image mode; they have no caption embedding.", italic=True)

d.add_heading("4. Methodology", 1)
d.add_heading("4.1 Pipeline", 2)
T(["Step", "What happens"],
  [["1. Load", "Read images and captions; match each caption to its image by filename."],
   ["2. Embed", "CLIP image encoder gives image embeddings; CLIP text encoder gives caption embeddings. All vectors are normalized to length 1."],
   ["3. Store", "Save embeddings, filenames and captions in outputs/ so they are computed only once."],
   ["4. Query", "Encode the user's text with the CLIP text encoder."],
   ["5. Rank", "Cosine similarity between the query and every stored vector; sort high to low."],
   ["6. Show", "Return the Top-K images with score and caption (web app or terminal)."]],
  [1.1, 5.4])
d.add_heading("4.2 Cosine similarity", 2)
P("Because all vectors have length 1, cosine similarity equals their dot product: score = query · image. A score near 1 means very similar. "
  "Typical CLIP text-image scores for good matches are low (about 0.2 to 0.35), so the ranking matters more than the absolute value.")
d.add_heading("4.3 Search modes", 2)
T(["Mode", "Query compared with", "Purpose"],
  [["image", "image embeddings", "Default visual search"],
   ["caption", "caption embeddings", "Match the written description"],
   ["hybrid", "average of image and caption score", "Combine both; images without a caption use the image score only"]],
  [1.1, 2.4, 3.0])

d.add_heading("5. Implementation", 1)
P("The project is written in Python with PyTorch and Hugging Face Transformers (model: openai/clip-vit-base-patch32), NumPy for similarity search and Streamlit for the demo.")
T(["File", "Role"],
  [["build_index.py", "Creates the index; can reuse image embeddings made earlier and only encode captions"],
   ["src/clip_encoder.py", "Loads CLIP; encode_images and encode_texts"],
   ["src/search_engine.py", "Loads embeddings; search(query, top_k, mode)"],
   ["search_cli.py", "Search from the terminal"],
   ["app.py", "Streamlit web app"],
   ["evaluate.py", "Recall@K metrics and result pictures"],
   ["docs/", "Installation, usage, workflow, GitHub and Colab guides"]],
  [2.0, 4.5])
P("Design decisions: filenames are stored next to the embeddings so rows can never get out of order (an index with misaligned rows gives chance-level "
  "evaluation scores, which makes mistakes easy to notice); embeddings are computed once and reused; CLIP is loaded only at the first search.")

d.add_heading("6. Learning Progress", 1)
B(["Week 3, MNIST MLP: built a 784-128-64-10 network in PyTorch with cross-entropy loss and Adam; learned the training loop, evaluation and saving a model.",
   "Week 4, CLIP embeddings: used pretrained CLIP ViT-B/32 to turn each image into a normalized 512-number vector, saved together with the filenames.",
   "Week 5, semantic retrieval: encoded text queries and ranked images by cosine similarity. For \"a photo of a dog\" the top-5 scores in that run were 0.263, 0.263, 0.262, 0.253 and 0.248, showing the typical low CLIP score range.",
   "Week 8: combined everything into one tested and documented project."])

d.add_heading("7. Testing and Evaluation", 1)
P("Two tests are run by evaluate.py:")
B([f"Test A, caption-to-image: each of the {NC} usable captions is a query. The system is correct if the caption's own image is ranked near the top. "
   "We report Recall@1, Recall@5, Recall@10 and mean reciprocal rank (MRR).",
   f"Test B, free-text queries: {len(queries)} queries from tests/test_queries.txt; the top-5 images for each are saved as pictures and checked by eye."])
P("Scope of the evaluation: this is a caption-to-image retrieval test of the image-embedding search, not a measure of general model accuracy. "
  "The captions were written for these same images and are not an independent test set, and one caption can fit several similar images. "
  "Caption and hybrid modes are not evaluated this way because their index is built from the same caption text.", italic=True)
d.add_heading("7.1 Results", 2)
T(["Metric", "Value"],
  [["Images in index", N], ["Caption queries", NC], ["Recall@1", pct(M["recall@1"])], ["Recall@5", pct(M["recall@5"])],
   ["Recall@10", pct(M["recall@10"])], ["Mean reciprocal rank", f"{M['mean_reciprocal_rank']:.3f}"],
   ["Median rank of correct image", f"{M['median_rank']:.0f}"]], [3.0, 3.0])
d.add_heading("7.2 Demo application", 2)
FIG(shot, "Figure 1. The Streamlit search application.")
d.add_heading("7.3 Example search results", 2)
for i, (pic, n) in enumerate(zip(example_pics, a.examples), 2):
    FIG(pic, f"Figure {i}. Top-5 results for test query {n}.")
d.add_heading("7.4 Discussion", 2)
P(discussion)
if user_notes:
    P("Observations", True)
    for para in user_notes.split("\n\n"):
        P(para)

d.add_heading("8. Limitations", 1)
B(["CLIP ViT-B/32 is a small model; fine details, counting and small text are often wrong.",
   f"{S['images'] - S['non_empty_captions']} images have no usable caption, so caption and hybrid modes cannot find them.",
   "Search compares the query with every image (brute force). This is fast for about a thousand images but would need an index such as FAISS for millions.",
   "Evaluation uses the dataset's own captions as ground truth; one caption can describe several similar images, so Recall is a conservative measure."])
d.add_heading("9. Conclusion and Future Work", 1)
P("The project delivers a working end-to-end pipeline from images and captions to embeddings, search and results, with a demo application, "
  "an evaluation script and documentation. Future work: a larger CLIP model (ViT-L/14), image-to-image search, fine-tuning on the captions, and a FAISS index for large datasets.")
d.add_heading("10. How to Run", 1)
P(f"pip install -r requirements.txt, then python build_index.py, then streamlit run app.py. Repository: {a.github}")
d.add_heading("11. References", 1)
B(["Radford et al., \"Learning Transferable Visual Models From Natural Language Supervision\" (CLIP), ICML 2021.",
   "Hugging Face Transformers documentation, CLIPModel (openai/clip-vit-base-patch32).",
   "Streamlit documentation, https://docs.streamlit.io"])
f = sec.footer.paragraphs[0]; f.alignment = WD_ALIGN_PARAGRAPH.CENTER; r = f.add_run()
for t, txt in (("begin", None), (None, "PAGE"), ("end", None)):
    if t:
        e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), t)
    else:
        e = OxmlElement("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = txt
    r._r.append(e)
Path(a.out).mkdir(exist_ok=True)
d.save(Path(a.out) / "Project_Report.docx")

# ----------------------------------------------------------------- SLIDES
from pptx import Presentation
from pptx.dml.color import RGBColor as RGB
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches as In, Pt as Pt_

DARK, TEAL, ORANGE, SOFT, INK = RGB(0x0E, 0x3B, 0x43), RGB(0x0E, 0x7C, 0x86), RGB(0xF2, 0x99, 0x4A), RGB(0xEE, 0xF4, 0xF4), RGB(0x1B, 0x2A, 0x33)
WHITE = RGB(255, 255, 255)
prs = Presentation(); prs.slide_width, prs.slide_height = In(13.333), In(7.5)
blank = prs.slide_layouts[6]


def box(s, x, y, w, h, fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    sh = s.shapes.add_shape(shape, In(x), In(y), In(w), In(h)); sh.fill.solid(); sh.fill.fore_color.rgb = fill
    sh.line.fill.background(); sh.shadow.inherit = False; return sh


def text(s, x, y, w, h, t, size=18, bold=False, color=INK, align=PP_ALIGN.LEFT, font="Calibri", anchor=MSO_ANCHOR.TOP):
    tb = s.shapes.add_textbox(In(x), In(y), In(w), In(h)); tf = tb.text_frame; tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    lines = t if isinstance(t, list) else [t]
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align; p.space_after = Pt_(6)
        r = p.add_run(); r.text = ln; r.font.size = Pt_(size); r.font.bold = bold; r.font.color.rgb = color; r.font.name = font
    return tb


def slide(title_text=None, bg=WHITE):
    s = prs.slides.add_slide(blank); s.background.fill.solid(); s.background.fill.fore_color.rgb = bg
    if title_text:
        text(s, 0.8, 0.5, 11.7, 0.9, title_text, 36, True, DARK, font="Cambria")
    return s


def fit_picture(s, path, x, y, w, h):
    iw, ih = Image.open(path).size; sc = min(w / iw, h / ih)
    pw, ph = iw * sc, ih * sc
    s.shapes.add_picture(str(path), In(x + (w - pw) / 2), In(y + (h - ph) / 2), In(pw), In(ph))


def card(s, x, y, w, h, head, lines):
    box(s, x, y, w, h, SOFT)
    text(s, x + 0.3, y + 0.25, w - 0.6, 0.5, head, 22, True, DARK, font="Cambria")
    text(s, x + 0.3, y + 0.95, w - 0.6, h - 1.1, lines, 18)


def stat(s, x, y, w, h, big, small):
    box(s, x, y, w, h, SOFT)
    text(s, x, y + 0.25, w, h * 0.5, big, 48, True, TEAL, PP_ALIGN.CENTER, "Cambria", MSO_ANCHOR.MIDDLE)
    text(s, x, y + h * 0.65, w, 0.5, small, 18, False, INK, PP_ALIGN.CENTER)


s = slide(bg=DARK)
text(s, 1.0, 2.0, 11.3, 1.4, "AI-Powered Image Search Engine", 48, True, WHITE, font="Cambria")
text(s, 1.0, 3.5, 11.3, 0.6, "Find images by describing them, using CLIP", 24, False, RGB(0xCF, 0xE6, 0xE8))
text(s, 1.0, 5.2, 11.3, 1.2, [a.name, "VISMA Lab, IIT Bhubaneswar  ·  Supervisor: Dr. Debi Prosad Dogra", a.github], 18, False, WHITE)

s = slide("The problem and the idea")
card(s, 0.8, 1.8, 5.7, 4.6, "Problem", ["Searching by filename or tags misses meaning.", "\"A quiet street\" finds nothing if no file has that name."])
card(s, 6.8, 1.8, 5.7, 4.6, "Idea", ["CLIP places text and images in the same 512-number space.", "Close vectors mean similar meaning, so a sentence can find a picture."])

s = slide("How it works")
steps = [("Images +\ncaptions", "data"), ("CLIP\nembeddings", "512 numbers"), ("Saved\nindex", "computed once"),
         ("Query\nembedding", "same space"), ("Cosine\nsimilarity", "rank all"), ("Top-K\nimages", "results")]
for i, (a_, b_) in enumerate(steps):
    x = 0.7 + i * 2.05
    box(s, x, 2.4, 1.8, 1.7, ORANGE if i == 5 else (TEAL if i % 2 else DARK))
    text(s, x, 2.4, 1.8, 1.7, a_.split("\n"), 18, True, WHITE, PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, x, 4.25, 1.8, 0.4, b_, 14, False, RGB(0x5A, 0x6B, 0x73), PP_ALIGN.CENTER)
text(s, 0.8, 5.5, 11.7, 1.0, "Vectors have length 1, so cosine similarity is just a dot product. Embeddings are built once; each search only encodes the short query.", 18)

s = slide("Dataset")
stat(s, 0.8, 1.7, 3.7, 2.2, f"{S['images']:,}", "images")
stat(s, 4.8, 1.7, 3.7, 2.2, f"{S['non_empty_captions']:,}", "usable captions")
stat(s, 8.8, 1.7, 3.7, 2.2, "512", "numbers per image")
text(s, 0.8, 4.4, 11.7, 2.2,
     [f"{S['caption_files']} caption files; {S['images_without_caption_file']} images have no caption file and {S['empty_caption_files']} caption file is empty.",
      "Images without a caption are still searchable in image mode.",
      "The dataset is confidential and is not on GitHub."], 18)

s = slide("Implementation")
rows = [("build_index.py", "images + captions → embeddings (reuses existing ones)"), ("src/clip_encoder.py", "CLIP: encode images and text"),
        ("src/search_engine.py", "search(query, top_k, mode)"), ("app.py", "Streamlit demo"), ("evaluate.py", "Recall@K + result pictures")]
for i, (f_, d_) in enumerate(rows):
    y = 1.7 + i * 0.85
    box(s, 0.8, y, 4.4, 0.65, DARK)
    text(s, 0.8, y, 4.4, 0.65, f_, 16, True, WHITE, PP_ALIGN.CENTER, "Courier New", MSO_ANCHOR.MIDDLE)
    text(s, 5.5, y, 7.0, 0.65, d_, 18, anchor=MSO_ANCHOR.MIDDLE)
text(s, 0.8, 6.3, 11.7, 0.5, "Python · PyTorch · Hugging Face Transformers (CLIP ViT-B/32) · NumPy · Streamlit", 16, False, RGB(0x5A, 0x6B, 0x73))

s = slide("Demo application")
fit_picture(s, shot, 0.8, 1.6, 8.2, 5.2)
text(s, 9.4, 1.8, 3.4, 3.5, ["Type any description", "Choose 1 to 12 results", "Modes: image, caption, hybrid", "Shows score and caption"], 18)
box(s, 9.4, 5.6, 3.4, 0.7, DARK)
text(s, 9.4, 5.6, 3.4, 0.7, "streamlit run app.py", 16, True, WHITE, PP_ALIGN.CENTER, "Courier New", MSO_ANCHOR.MIDDLE)

s = slide("Testing and results")
text(s, 0.8, 1.5, 11.7, 1.0, [f"Test A: {NC} captions used as queries; is the matching image in the top K?", f"Test B: {len(queries)} free-text queries, top-5 images checked by eye"], 18)
for i, (k, lab) in enumerate((("recall@1", "Recall@1"), ("recall@5", "Recall@5"), ("recall@10", "Recall@10"))):
    stat(s, 0.8 + i * 4.0, 2.9, 3.7, 2.0, pct(M[k]), lab)
text(s, 0.8, 5.4, 11.7, 1.2, f"Mean reciprocal rank {M['mean_reciprocal_rank']:.3f} · median rank {M['median_rank']:.0f} · random ranking would give {pct(chance1)} at rank 1.", 18)

for n, pic in zip(a.examples, example_pics):
    s = slide(f"Example results: test query {n}")
    q = queries[n - 1][0] if n - 1 < len(queries) else ""
    fit_picture(s, pic, 0.8, 1.5, 11.7, 4.6)
    text(s, 0.8, 6.3, 11.7, 0.6, f"Query: \"{q}\"", 18, False, INK)

s = slide("Limitations and future work")
card(s, 0.8, 1.8, 5.7, 4.6, "Limitations", ["Small CLIP model: weak on counting, exact colours, small details.",
                                           f"{S['images'] - S['non_empty_captions']} images have no usable caption.", "Brute-force search suits about 1,000 images."])
card(s, 6.8, 1.8, 5.7, 4.6, "Next steps", ["Larger CLIP (ViT-L/14).", "Fine-tune on the captions.", "FAISS index for large datasets.", "Image-to-image search."])

s = slide(bg=DARK)
text(s, 1.0, 2.6, 11.3, 1.2, "Thank you", 54, True, WHITE, font="Cambria")
text(s, 1.0, 4.0, 11.3, 0.6, f"Questions?   {a.github}", 22, False, RGB(0xCF, 0xE6, 0xE8))
prs.save(Path(a.out) / "Project_Presentation.pptx")
print("Created", Path(a.out) / "Project_Report.docx", "and", Path(a.out) / "Project_Presentation.pptx")
