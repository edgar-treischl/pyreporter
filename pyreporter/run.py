from typing import List, Optional
import json
import os
import pandas as pd

from pyreporter.fetch import fetch_raw_data
from pyreporter.prepare import prepare_data
from pyreporter.utils import create_directories, get_directory, clean_files
from pyreporter.plot import create_plotlist
from pyreporter.render_pdf import render_pdf

# --- Central defaults for testing ---
DEFAULTS = {
    "snr": "0001",
    "stype": "gy",
    "audience": "sus",
    "ubb": False,
    "ganztag": False,
    "has_N": ["sus", "leh"],
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
    """Print the effective configuration as JSON for easy reading."""
    config = {
        "SNR": snr,
        "SType": stype,
        "Audience": audience,
        "UBB": ubb,
        "Ganztag": ganztag,
        "Has_N": has_N,
        "Year": year
    }
    print("\n--- Effective Configuration ---")
    print(json.dumps(config, indent=4))
    print("-------------------------------\n")

def main(
    snr: str = DEFAULTS["snr"],
    stype: str = DEFAULTS["stype"],
    audience: str = DEFAULTS["audience"],
    ubb: bool = DEFAULTS["ubb"],
    ganztag: bool = DEFAULTS["ganztag"],
    has_N: Optional[List[str]] = None,
    year: str = DEFAULTS["year"],
    use_cache: bool = True
) -> None:
    if has_N is None:
        has_N = DEFAULTS["has_N"]

    # --- Print current effective configuration ---
    print_config(snr, stype, audience, ubb, ganztag, has_N, year)

    # --- Step 1: Fetch raw data ---
    print("\n" + "="*60)
    print("STEP 1: FETCH RAW DATA")
    print("="*60)
    
    fetch_result = fetch_raw_data(
        snr=snr,
        stype=stype,
        audience=audience,
        ubb=ubb,
        ganztag=ganztag,
        has_N=has_N,
        use_cache=use_cache
    )
    
    raw_data = fetch_result['raw_data']
    syear = fetch_result['syear']
    result_n = fetch_result['result_n']
    
    print(f"✓ Fetched {len(raw_data)} response rows")

    # --- Step 2: Prepare data ---
    print("\n" + "="*60)
    print("STEP 2: PREPARE DATA")
    print("="*60)
    
    prepared = prepare_data(
        snr=snr,
        stype=stype,
        audience=audience,
        ubb=ubb,
        ganztag=ganztag,
        has_N=has_N,
        raw_data=raw_data,
        use_cache=use_cache
    )
    
    report_meta = prepared['report_meta']
    header_report = prepared['header_report']
    sname = prepared['sname']
    
    print(f"✓ Prepared {len(prepared['plot_data'])} plots")

    # --- Step 3: Create directories ---
    print("\n" + "="*60)
    print("STEP 3: SETUP OUTPUT DIRECTORY")
    print("="*60)
    
    create_directories(snr=snr, audience=audience, ubb=ubb, syear=syear)
    print(f"✓ Created directory structure in res/{snr}_{syear}/")

    # --- Step 4: Generate plots ---
    print("\n" + "="*60)
    print("STEP 4: GENERATE PLOTS")
    print("="*60)
    
    create_plotlist(
        meta_list=report_meta['meta'],
        snr=snr,
        year=syear,
        audience=audience,
        report=report_meta['report'],
        data=raw_data,
        ubb=ubb,
        export=True
    )
    
    print(f"✓ Generated {len(report_meta['meta'])} plots")

    # --- Step 5: Render PDF ---
    print("\n" + "="*60)
    print("STEP 5: RENDER PDF")
    print("="*60)
    
    render_pdf(
        audience=audience,
        snr=snr,
        year=syear,
        sname=sname,
        survey_n=result_n,
        duration="2",
        header_report=header_report
    )
    
    print(f"✓ Rendered PDF report")

    # --- Step 6: Clean temporary files ---
    print("\n" + "="*60)
    print("STEP 6: CLEANUP")
    print("="*60)
    
    tmpdir = get_directory(snr=snr, syear=syear)
    clean_files(where=tmpdir)
    
    print("\n" + "="*60)
    print("✅ PIPELINE COMPLETE!")
    print("="*60)
    print(f"\nReport saved to: {tmpdir}/{snr}_results_{audience}.pdf")


if __name__ == "__main__":
    # Read environment variables for automation
    use_cache = os.getenv("NO_CACHE", "").lower() != "true"
    
    main(
        snr=os.getenv("SNR", DEFAULTS["snr"]),
        stype=os.getenv("STYPE", DEFAULTS["stype"]),
        audience=os.getenv("AUDIENCE", DEFAULTS["audience"]),
        ubb=os.getenv("UBB", str(DEFAULTS["ubb"])).lower() == "true",
        ganztag=os.getenv("GANZTAG", str(DEFAULTS["ganztag"])).lower() == "true",
        has_N=os.getenv("HAS_N", ",".join(DEFAULTS["has_N"])).split(","),
        year=os.getenv("YEAR", DEFAULTS["year"]),
        use_cache=use_cache
    )