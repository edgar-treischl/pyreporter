"""
Data preparation module for pyreporter.

Transforms raw survey data into plot-ready format with metadata.
"""

import os
import pandas as pd
from typing import Dict, Any, List, Optional
from pyreporter.meta_repository import MetaRepository
from pyreporter.utils import get_metadata, get_plotdata, get_sname, match_meta_reports
from pyreporter.cache import get_cache
from pyreporter.fetch import fetch_raw_data


def prepare_data(
    snr: str,
    stype: str,
    audience: str,
    ubb: bool,
    ganztag: bool,
    has_N: List[str],
    raw_data: Optional[pd.DataFrame] = None,
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Prepare plot-ready data from raw survey responses.
    
    Parameters
    ----------
    snr : str
        School number
    stype : str
        School type
    audience : str
        Target audience
    ubb : bool
        UBB flag
    ganztag : bool
        Full-day school flag
    has_N : list of str
        Available audiences
    raw_data : pd.DataFrame, optional
        Pre-fetched raw data. If None, will fetch from cache/API
    use_cache : bool, optional
        Whether to use cached data (default: True)
    
    Returns
    -------
    dict
        Dictionary containing:
        - 'plot_data': Dict mapping plot names to prepared DataFrames
        - 'report_meta': Report metadata dict with 'report' and 'meta' keys
        - 'header_report': DataFrame for report headers
        - 'sname': School name
        - 'config': Configuration dict
    """
    cache = get_cache()
    
    # Check cache first
    cache_params = {
        'snr': snr,
        'stype': stype,
        'audience': audience,
        'ubb': ubb,
        'ganztag': ganztag,
        'has_N': ','.join(sorted(has_N)),
    }
    
    if use_cache:
        cached = cache.load('prepared', **cache_params)
        if cached is not None:
            return cached
    
    print(f"\n🔧 Preparing data for {audience} audience...")
    
    # If no raw_data provided, fetch it
    if raw_data is None:
        print("   Raw data not provided, fetching...")
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
    else:
        # Extract year from raw_data if available
        if 'surveyls_title' in raw_data.columns:
            surveyls_title = raw_data["surveyls_title"]
            second_set_of_digits = surveyls_title.str.extract(r'^[^_]+_([^_]+)')[0]
            years = second_set_of_digits.str[:4].unique()
            syear = str(years[0]) if len(years) > 0 else "unknown"
        else:
            syear = "unknown"
        result_n = "unknown"
    
    # Load metadata
    meta_repo = MetaRepository()
    meta_templates = meta_repo.meta_templates
    meta_reports = meta_repo.meta_reports
    meta_snames = meta_repo.meta_snames
    
    # Get school name
    sname = get_sname(meta_snames=meta_snames, snr=snr)
    
    # Get report metadata (which plots to generate)
    report_meta = get_metadata(
        meta_templates=meta_templates,
        meta_reports=meta_reports,
        school=stype,
        audience=audience,
        ub=ubb,
        gt=ganztag,
        data_avail=has_N
    )
    
    print(f"   Report template: {report_meta['report']}")
    print(f"   Plots to generate: {len(report_meta['meta'])}")
    
    # Prepare data for each plot
    plot_data = {}
    for plot_name in report_meta['meta']:
        try:
            plotdata = get_plotdata(
                data=raw_data,
                report_name=report_meta['report'],
                plot_name=plot_name,
                audience=audience
            )
            plot_data[plot_name] = plotdata
            print(f"   ✓ {plot_name}: {len(plotdata)} data points")
        except Exception as e:
            print(f"   ✗ {plot_name}: {e}")
            raise
    
    # Build header report
    header_report = match_meta_reports(
        survey_report=report_meta['report'],
        survey_plots=report_meta['meta']
    )
    
    # Package results
    result = {
        'plot_data': plot_data,
        'report_meta': report_meta,
        'header_report': header_report,
        'sname': sname,
        'syear': syear,
        'result_n': result_n,
        'config': {
            'snr': snr,
            'stype': stype,
            'audience': audience,
            'ubb': ubb,
            'ganztag': ganztag,
            'has_N': has_N,
        }
    }
    
    # Save to cache
    if use_cache:
        cache.save(result, 'prepared', **cache_params)
    
    return result


def main():
    """CLI entry point for prepare command."""
    import os
    
    # Read from environment
    snr = os.getenv("SNR", "0001")
    stype = os.getenv("STYPE", "gy")
    audience = os.getenv("AUDIENCE", "sus")
    ubb = os.getenv("UBB", "False").lower() == "true"
    ganztag = os.getenv("GANZTAG", "False").lower() == "true"
    has_N = os.getenv("HAS_N", "sus,leh").split(",")
    
    # Force no cache if NO_CACHE is set
    use_cache = os.getenv("NO_CACHE", "").lower() != "true"
    
    result = prepare_data(
        snr=snr,
        stype=stype,
        audience=audience,
        ubb=ubb,
        ganztag=ganztag,
        has_N=has_N,
        use_cache=use_cache
    )
    
    print(f"\n✅ Preparation complete:")
    print(f"   - School: {result['sname']} ({snr})")
    print(f"   - Year: {result['syear']}")
    print(f"   - Report: {result['report_meta']['report']}")
    print(f"   - Plots ready: {len(result['plot_data'])}")
    
    return result


if __name__ == "__main__":
    main()
