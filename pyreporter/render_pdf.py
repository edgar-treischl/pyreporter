import subprocess
from pathlib import Path
import json
from pyreporter.utils import get_directory


def render_pdf(audience, snr, year, sname, survey_n, duration):

    tmp_dir = Path("/Users/edgar/Develop/backend/pyreporter/pyreporter/res") / f"{snr}_{year}"

    results_map = {
        "elt": "Eltern",
        "sus": "Schülerinnen und Schüler",
        "ubb": "Unterrichtsbeobachtungen",
        "all": "Alle Befragtengruppen",
        "aus": "Ausbilder",
        "leh": "Lehrkräfte"
    }
    results = results_map.get(audience, audience)

    output_file = f"{snr}_results_{audience}.pdf"

    params = {
        "snr": snr,
        "name": sname,
        "n": survey_n,
        "d": duration,
        "fb": results
    }

    cmd = [
        "quarto",
        "render",
        str(tmp_dir / "template.qmd"),
        "--to", "pdf",
        "--output", output_file,
        "--execute-params", json.dumps(params)
    ]

    print("Running command:", " ".join(cmd))

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)

    result.check_returncode()  # Will raise CalledProcessError if non-zero