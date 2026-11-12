# Report and presentation

They are generated from your real results, so no empty placeholders remain:

    python build_index.py
    python evaluate.py
    streamlit run app.py              # take a screenshot of a search -> app.png
    pip install python-docx python-pptx
    python report/build_deliverables.py --github https://github.com/<you>/<repo> --screenshot app.png

Optional: write your own observations (after looking at outputs/results/*.png) in report/discussion.txt.
They are added to the report under "Observations". Choose which result pictures to show with `--examples 3 4 7`.
