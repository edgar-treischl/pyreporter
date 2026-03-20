from typing import List, Optional
import os

from pyreporter.utils import (
    get_metadata, get_sname, get_data, match_meta_reports, get_n,
    create_directories, get_directory, clean_files
)
from pyreporter.meta_repository import MetaRepository
from pyreporter.limer import limer_connect, limer_SIDs
from pyreporter.plot import create_plotlist
from pyreporter.render_pdf import render_pdf

# --- Central defaults for testing ---
DEFAULTS = {
    "snr": "0001",
    "stype": "gy",
    "audience": "sus",
    "ubb": False,
    "ganztag": False,
    "has_N": ["sus", "elt"],
    "year": "2025"
}

def print_config(
    snr: str,
    stype: str,
    audience: str,
    ubb: bool,
    ganztag: bool,
    has_N: List[str],
    year: str
) -> None:
    """Print the effective configuration for this run."""
    print("\n--- Effective Configuration ---")
    print(f"SNR      : {snr}")
    print(f"SType    : {stype}")
    print(f"Audience : {audience}")
    print(f"UBB      : {ubb}")
    print(f"Ganztag  : {ganztag}")
    print(f"Has_N    : {has_N}")
    print(f"Year     : {year}")
    print("-------------------------------\n")

def main(
    snr: str = DEFAULTS["snr"],
    stype: str = DEFAULTS["stype"],
    audience: str = DEFAULTS["audience"],
    ubb: bool = DEFAULTS["ubb"],
    ganztag: bool = DEFAULTS["ganztag"],
    has_N: Optional[List[str]] = None,
    year: str = DEFAULTS["year"]
) -> None:
    if has_N is None:
        has_N = DEFAULTS["has_N"]

    # --- Print current effective configuration ---
    print_config(snr, stype, audience, ubb, ganztag, has_N, year)

    # --- Meta repository ---
    meta_repo = MetaRepository()
    meta_templates = meta_repo.meta_templates
    meta_reports = meta_repo.meta_reports
    meta_snames = meta_repo.meta_snames

    sname_meta = get_sname(meta_snames=meta_snames, snr=snr)
    print("\nReport for:", sname_meta)

    # --- Limer connection ---
    limer_connect()
    sids_df = limer_SIDs(snr=snr, ubb=ubb)
    sid = sids_df["sid"]
    print("\nSurvey ID:", sid[0])

    # --- N results ---
    n_result = get_n(audience=audience, data=sids_df)
    result_n = n_result["tmp.n"]

    surveyls_title = sids_df["surveyls_title"]
    second_set_of_digits = surveyls_title.str.extract(r'^[^_]+_([^_]+)')[0]
    years = second_set_of_digits.str[:4].unique()
    syear = str(years[0])

    create_directories(snr=snr, audience=audience, ubb=ubb, syear=syear)

    # --- Response data ---
    realdf = get_data(id="251539", surveyls_title="Bla", ubb=False)
    print("\nData downloaded:", realdf.head())

    # --- Report metadata ---
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

    # --- Export plots ---
    create_plotlist(
        meta_list=report_meta['meta'],
        snr=snr,
        year=syear,
        audience=audience,
        report=report_meta['report'],
        data=realdf,
        ubb=ubb,
        export=True
    )

    # --- Build header report ---
    header_report = match_meta_reports(
        survey_report=report_meta['report'],
        survey_plots=report_meta['meta']
    )

    # --- Render final PDF ---
    render_pdf(
        audience=audience,
        snr=snr,
        year=syear,
        sname=sname_meta,
        survey_n=result_n,
        duration="2",
        header_report=header_report
    )

    # --- Clean temporary files ---
    tmpdir = get_directory(snr=snr, syear=syear)
    clean_files(where=tmpdir)


if __name__ == "__main__":
    # Read environment variables for automation
    main(
        snr=os.getenv("SNR", DEFAULTS["snr"]),
        stype=os.getenv("STYPE", DEFAULTS["stype"]),
        audience=os.getenv("AUDIENCE", DEFAULTS["audience"]),
        ubb=os.getenv("UBB", str(DEFAULTS["ubb"])).lower() == "true",
        ganztag=os.getenv("GANZTAG", str(DEFAULTS["ganztag"])).lower() == "true",
        has_N=os.getenv("HAS_N", ",".join(DEFAULTS["has_N"])).split(","),
        year=os.getenv("YEAR", DEFAULTS["year"])
    )