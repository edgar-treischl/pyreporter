import subprocess
from pathlib import Path
import yaml
import pandas as pd
from pyreporter.utils import get_directory


def render_pdf(audience, snr, year, sname, survey_n, duration, header_report: pd.DataFrame):

    tmp_dir = Path(get_directory(snr=snr, syear=year))

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
        "d": str(duration),
        "fb": results,
        "meta": header_report["plot"].tolist(),
        "num_bars": [int(x) for x in header_report["vars_count"].tolist()],
        "header": header_report["header2"].tolist(),
    }

    # Write params to YAML file (required by --execute-params)
    params_file = tmp_dir / "params.yml"
    with open(params_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(params, f, allow_unicode=True, sort_keys=False)
        #yaml.dump(params, f, allow_unicode=True, default_flow_style=False)

    cmd = [
        "quarto",
        "render",
        "template.qmd",
        "--to", "pdf",
        "--output", output_file,
        "--execute-params", "params.yml"
    ]

    print("Running command:", " ".join(cmd))

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(tmp_dir)
    )

    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)

    result.check_returncode()  # Will raise CalledProcessError if non-zero