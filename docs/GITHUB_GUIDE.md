# GitHub Guide (Day 4)

## Rules for this submission
- The dataset is confidential. **Nothing derived from it may be uploaded**: images, captions, embeddings (`.npy`), `captions.json`,
  `dataset_stats.json`, `metrics.json`, result pictures, app screenshots, and the generated report/slides (they contain dataset images and statistics).
- `.gitignore` already blocks all of these. Upload **source code and documentation only**.
- The report and presentation are submitted separately (not through a public repository).

## Steps

    git init
    git add .
    git status                      # check: no images or captions listed!
    git commit -m "Initial commit: CLIP image search engine"

Create an empty repository on github.com (no README), then:

    git branch -M main
    git remote add origin https://github.com/<your-username>/<repo-name>.git
    git push -u origin main

## Good habits
- Small commits with clear messages: `Add hybrid search mode`, `Fix missing caption bug`.
- Never commit data, model files or passwords.
- Keep the README up to date; it is the first thing evaluators read.
- Run `git status` before every push and check that no dataset-derived file is listed.
