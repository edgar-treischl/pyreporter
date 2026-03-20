import os
import pandas as pd
from typing import Optional, List

from pyreporter.utils import (
    get_metadata,
    get_sname,
    get_data,
    match_meta_reports,
    get_n,
    create_directories,
    get_directory
)
from pyreporter.meta_repository import MetaRepository
from pyreporter.plot import create_plotlist

# Default values (can be overridden via Makefile / env)
DEFAULTS = {
    "snr": "0001",
    "stype": "gy",
    "audience": "sus",
    "ubb": False,
    "ganztag": False,
    "has_N": ["sus", "leh"],
    "year": "2024"
}

def download_and_combine(sids_df: pd.DataFrame, ubb: bool) -> pd.DataFrame:
    """
    Download all survey data for the given survey IDs and combine into a single DataFrame.
    Keeps all audiences; filtering happens later per report if needed.
    """
    dfs = [
        get_data(id=sid, surveyls_title=title, ubb=ubb)
        for sid, title in zip(sids_df["sid"], sids_df["surveyls_title"])
        if pd.notna(title)
    ]
    combined_df = pd.concat(dfs, ignore_index=True)
    return combined_df


def export_data(
    snr: str = DEFAULTS["snr"],
    stype: str = DEFAULTS["stype"],
    audience: str = DEFAULTS["audience"],
    ubb: bool = DEFAULTS["ubb"],
    ganztag: bool = DEFAULTS["ganztag"],
    has_N: Optional[List[str]] = None,
    year: str = DEFAULTS["year"]
):
    """
    Run the report pipeline up to data download and plot metadata resolution.
    Instead of generating PDFs, exports all artifacts to CSV for inspection.
    """
    if has_N is None:
        has_N = DEFAULTS["has_N"]

    # --- Repository & metadata ---
    meta_repo = MetaRepository()
    meta_templates = meta_repo.meta_templates
    meta_reports = meta_repo.meta_reports
    meta_snames = meta_repo.meta_snames

    # --- School name ---
    sname_meta = get_sname(meta_snames=meta_snames, snr=snr)
    print("\nReport for:", sname_meta)

    # --- Survey IDs & basic Limesurvey info ---
    from pyreporter.limer import limer_connect, limer_SIDs
    limer_connect()
    sids_df = limer_SIDs(snr=snr, ubb=ubb)
    print("\nSurvey IDs found:\n", sids_df)

    # --- Download all survey data ---
    realdf = download_and_combine(sids_df=sids_df, ubb=ubb)
    print("\nData downloaded:\n", realdf.head())

    # --- Resolve report metadata ---
    report_meta = get_metadata(
        meta_templates=meta_templates,
        meta_reports=meta_reports,
        school=stype,
        audience=audience,
        ub=ubb,
        gt=ganztag,
        data_avail=has_N
    )
    print("\nReport meta:", report_meta)

    # --- Export artifacts as CSV ---
    export_dir = get_directory(snr=snr, syear=year)
    os.makedirs(export_dir, exist_ok=True)

    # Save combined survey data
    realdf.to_csv(os.path.join(export_dir, f"{snr}_all_surveys.csv"), index=False)
    print(f"Survey data exported to {export_dir}/{snr}_all_surveys.csv")

    # Save metadata
    meta_df = pd.DataFrame({"variable": report_meta['meta']})
    meta_df.to_csv(os.path.join(export_dir, f"{snr}_report_meta.csv"), index=False)
    print(f"Report metadata exported to {export_dir}/{snr}_report_meta.csv")

    # Optional: export survey counts
    n_result = get_n(audience=audience, data=sids_df)
    n_df = pd.DataFrame({"audience": [audience], "n": [n_result["tmp.n"]]})
    n_df.to_csv(os.path.join(export_dir, f"{snr}_n_counts.csv"), index=False)
    print(f"Survey counts exported to {export_dir}/{snr}_n_counts.csv")

    # Optional: export plot list placeholders
    plot_list = create_plotlist(
        meta_list=report_meta['meta'],
        snr=snr,
        year=year,
        audience=audience,
        report=report_meta['report'],
        data=realdf,
        ubb=ubb,
        export=False  # don't actually export plots yet
    )
    plot_df = pd.DataFrame({"plot_meta": plot_list})
    plot_df.to_csv(os.path.join(export_dir, f"{snr}_plotlist.csv"), index=False)
    print(f"Plot list exported to {export_dir}/{snr}_plotlist.csv")

    print("\n--- Export complete ---")

    
    


if __name__ == "__main__":
    # Call with defaults; can later read env vars or CLI args
    export_data()