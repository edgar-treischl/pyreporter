import pandas as pd
from typing import Optional, Iterable, Dict, Any


def _as_bool(series: pd.Series) -> pd.Series:
    """
    Normalize boolean-like columns coming from CSV.
    """
    if series.dtype == bool:
        return series

    return series.map(
        lambda x: bool(int(x)) if str(x).isdigit()
        else str(x).lower() == "true"
    )


def get_metadata(
    meta_templates: pd.DataFrame,
    meta_reports: pd.DataFrame,
    school: str,
    audience: str,
    ub: bool,
    gt: bool,
    data_avail: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    """
    Get meta data for a report template.
    """

    # --- Normalize boolean columns ---
    mt = meta_templates.copy()
    mt["ubb"] = _as_bool(mt["ubb"])
    mt["ganztag"] = _as_bool(mt["ganztag"])

    # --- Select report template ---
    tmpl_mask = (
        (mt["stype"] == school)
        & (mt["type"] == audience)
        & (mt["ubb"] == bool(ub))
        & (mt["ganztag"] == bool(gt))
    )

    report_templates = (
        mt.loc[tmpl_mask, "report_tmpl"]
        .unique()
    )

    if len(report_templates) > 1:
        raise ValueError(
            f"Error in get_metadata(): More than 1 report template found "
            f"(school={school}, audience={audience}, ubb={ub}, ganztag={gt})"
        )

    if len(report_templates) == 0:
        raise ValueError(
            f"Error in get_metadata(): No report template found "
            f"(school={school}, audience={audience}, ubb={ub}, ganztag={gt})"
        )

    report_template = report_templates[0]

    # --- Select report meta (plots) ---
    report_meta_df = meta_reports[
        meta_reports["report"] == report_template
    ]

    if audience == "all":
        if data_avail is None:
            raise ValueError(
                "Error in get_metadata(): data_avail must be provided "
                "for audience='all'."
            )

        report_meta_df = report_meta_df[
            report_meta_df["type"].isin(data_avail)
        ]

    report_meta = (
        report_meta_df
        .sort_values("plot")
        ["plot"]
        .dropna()
        .unique()
        .tolist()
    )

    if not report_meta:
        raise ValueError(
            f"Error in get_metadata(): Plot(s) not found in meta data "
            f"for report '{report_template}'."
        )

    return {
        "report": report_template,
        "meta": report_meta,
    }




import pandas as pd

def get_sname(snr: str, meta_snames: pd.DataFrame) -> str:
    """
    Get school name based on school number.

    Parameters
    ----------
    snr : str
        School number as a string
    meta_snames : pd.DataFrame
        DataFrame containing school metadata with columns 'SNR' and 'SNAME'

    Returns
    -------
    str
        School name, or a default message if not found
    """

    # Filter for the given school number
    tmp_name = meta_snames[meta_snames['SNR'] == snr]

    # Check if more than one name is found
    if len(tmp_name) > 1:
        raise ValueError("Error in get_sname(): More than one school name found.")

    # If no name is found
    if len(tmp_name) == 0:
        return "School name not available."

    # Return the school name (as a string)
    return tmp_name.iloc[0]['SNAME']

