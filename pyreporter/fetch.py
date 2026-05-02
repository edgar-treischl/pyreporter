"""
Data fetching module for pyreporter.

Handles LimeSurvey connection and raw data download with caching support.
"""

import os
import pandas as pd
from typing import Dict, Any, List
from pyreporter.limer import limer_connect, limer_SIDs, limer_release
from pyreporter.utils import get_n, get_data
from pyreporter.cache import get_cache


def fetch_raw_data(
    snr: str,
    stype: str,
    audience: str,
    ubb: bool,
    ganztag: bool,
    has_N: List[str],
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Fetch raw survey data from LimeSurvey.
    
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
    use_cache : bool, optional
        Whether to use cached data (default: True)
    
    Returns
    -------
    dict
        Dictionary containing:
        - 'raw_data': Combined DataFrame of all survey responses
        - 'sids_df': Survey metadata DataFrame
        - 'syear': Survey year string
        - 'result_n': Number of respondents string
        - 'config': Configuration dict for reference
    """
    cache = get_cache()
    
    # Check cache first
    cache_params = {
        'snr': snr,
        'ubb': ubb,
    }
    
    if use_cache:
        cached = cache.load('raw', **cache_params)
        if cached is not None:
            return cached
    
    print(f"\n📡 Fetching data from LimeSurvey for SNR={snr}, UBB={ubb}...")
    
    # Connect to LimeSurvey
    limer_connect()
    
    try:
        # Get survey metadata
        sids_df = limer_SIDs(snr=snr, ubb=ubb)
        print(f"   Found {len(sids_df)} survey(s)")
        
        # Get N results
        n_result = get_n(audience=audience, data=sids_df)
        result_n = n_result["tmp.n"]
        
        # Extract survey year from title
        surveyls_title = sids_df["surveyls_title"]
        second_set_of_digits = surveyls_title.str.extract(r'^[^_]+_([^_]+)')[0]
        years = second_set_of_digits.str[:4].unique()
        syear = str(years[0])
        
        # Fetch all survey responses
        dataframes = [
            get_data(id=sid, surveyls_title=title, ubb=ubb)
            for sid, title in zip(sids_df["sid"], sids_df["surveyls_title"])
        ]
        
        # Combine into single DataFrame
        raw_data = pd.concat(dataframes, ignore_index=True)
        print(f"   Downloaded {len(raw_data)} response rows")
        
    finally:
        # Always release the session
        limer_release()
    
    # Package results
    result = {
        'raw_data': raw_data,
        'sids_df': sids_df,
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
        cache.save(result, 'raw', **cache_params)
    
    return result


def main():
    """CLI entry point for fetch command."""
    import os
    
    # Read from environment (same as run.py)
    snr = os.getenv("SNR", "0001")
    stype = os.getenv("STYPE", "gy")
    audience = os.getenv("AUDIENCE", "sus")
    ubb = os.getenv("UBB", "False").lower() == "true"
    ganztag = os.getenv("GANZTAG", "False").lower() == "true"
    has_N = os.getenv("HAS_N", "sus,leh").split(",")
    
    # Force no cache if NO_CACHE is set
    use_cache = os.getenv("NO_CACHE", "").lower() != "true"
    
    result = fetch_raw_data(
        snr=snr,
        stype=stype,
        audience=audience,
        ubb=ubb,
        ganztag=ganztag,
        has_N=has_N,
        use_cache=use_cache
    )
    
    print(f"\n✅ Fetch complete:")
    print(f"   - Raw data preview:\n{result['raw_data'].head()}")
    print(f"\n✅ Fetch Summary:")
    print(f"   - School: {snr}")
    print(f"   - Year: {result['syear']}")
    print(f"   - Surveys: {len(result['sids_df'])}")
    print(f"   - Total responses: {len(result['raw_data'])}")
    print(f"   - N: {result['result_n']}")
    
    return result


if __name__ == "__main__":
    main()
