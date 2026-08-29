"""
Test render_pdf.py

Renders a PDF for school 0001 / 2025 using the existing plots in
pyreporter/res/0001_2025/plots/.  No live LimeSurvey connection needed.

Run with:
    poetry run python -m pyreporter.test.test_render
"""

import pandas as pd
from pyreporter.render_pdf import render_pdf

# Minimal header_report matching plots that already exist on disk
header_report = pd.DataFrame({
    "plot":       ["A11", "A12", "A13"],
    "vars_count": [4,     4,     4],
    "header2":    [
        "A1.1 Der Unterricht wird durch Störungen nicht beeinträchtigt.",
        "A1.2 Die Lernzeit wird effizient genutzt.",
        "A1.3 Das Unterrichtsklima ist lernförderlich.",
    ],
})

if __name__ == "__main__":
    print("Testing render_pdf …")
    render_pdf(
        audience="sus",
        snr="0001",
        year="2025",
        sname="Testschule",
        survey_n="42",
        duration="3",
        header_report=header_report,
    )
    print("Done — check pyreporter/res/0001_2025/0001_results_sus.pdf")
