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


import pandas as pd
import numpy as np


from pyreporter.limer import limer_connect, limer_responses, limer_release



def get_data(id, surveyls_title, ubb):
    """
    Get response data from LimeSurvey in long format.

    Parameters
    ----------
    id : int or str
        Survey ID
    surveyls_title : str
        Survey title
    ubb : any
        UBB (not used here but kept for compatibility)

    Returns
    -------
    pandas.DataFrame
    """

    # Connect to LimeSurvey
    tmp_session = limer_connect()

    # Get responses (short format)
    data = limer_responses(id, sResponseType="short")

    # Release session
    limer_release()

    # Ensure DataFrame
    data = pd.DataFrame(data)

    # Add id and surveyls_title
    data["sid"] = id
    data["surveyls_title"] = surveyls_title

    # Reorder columns: sid and surveyls_title first
    cols = ["sid", "surveyls_title"] + \
           [c for c in data.columns if c not in ["sid", "surveyls_title"]]
    data = data[cols]

    # Rename third column to "id" (Python is 0-based index)
    third_col = data.columns[2]
    data = data.rename(columns={third_col: "id"})

    # Move submitdate to last column if it exists
    if "submitdate" in data.columns:
        submitdate = data.pop("submitdate")
        data["submitdate"] = submitdate

    # Convert all columns to string
    data = data.astype(str)

    # Pivot longer (like tidyr::pivot_longer)
    value_vars = data.columns[3:]  # equivalent to 4:last_col() in R
    data = data.melt(
        id_vars=data.columns[:3],
        value_vars=value_vars,
        var_name="vars",
        value_name="vals"
    )

    # Remove dots and trim whitespace
    data["vars"] = data["vars"].str.replace(".", "", regex=False)
    data["vals"] = data["vals"].str.strip()

    # Save old vars
    data["vars_old"] = data["vars"]

    # Split at first "X"
    split_parts = data["vars"].str.split("X", n=1, expand=True)
    data["vars"] = split_parts[0]

    # Remove first 3 characters (equivalent to str_sub(4, ...))
    data["vars"] = data["vars"].str[3:]

    # Replace empty strings with NaN
    data["vals"] = data["vals"].replace("", np.nan)

    # Drop rows where vals is NA
    data = data.dropna(subset=["vals"])

    return data


import pandas as pd
import numpy as np
from pyreporter.meta_repository import MetaRepository


def get_plotdata(
    data: pd.DataFrame,
    report_name: str,
    plot_name: str,
    audience: str
):
    # -------------------------------------------------
    # Filter meta_raw for relevant vars
    # -------------------------------------------------
    meta_repo = MetaRepository()
    meta_raw = meta_repo.meta_reports
    meta_sets = meta_repo.meta_sets
    
    tmp_vars = (
        meta_raw
        .loc[
            (meta_raw["report"].isin([report_name])) &
            (meta_raw["plot"] == plot_name),
            ["vars", "plot", "label_short", "type"]
        ]
        .copy()
    )

    # -------------------------------------------------
    # Extract labelset
    # -------------------------------------------------
    labelset = (
        meta_raw
        .loc[
            (meta_raw["report"].isin([report_name])) &
            (meta_raw["plot"] == plot_name),
            "sets"
        ]
        .dropna()
        .unique()
    )

    if len(labelset) > 1:
        raise ValueError(
            "Error get_plotdata(): More than one labelset found."
        )

    if len(labelset) == 0:
        raise ValueError(
            "Error get_plotdata(): No labelset found."
        )

    labelset = labelset[0]

    # -------------------------------------------------
    # Get item labels from meta_sets
    # -------------------------------------------------
    tmp_item_labels = (
        meta_sets
        .loc[meta_sets["set"] == labelset]
        .sort_values("sort", ascending=False)
        .copy()
    )

    # -------------------------------------------------
    # Remove old vars column
    # -------------------------------------------------
    if "vars_old" in data.columns:
        data = data.drop(columns=["vars_old"])

    # -------------------------------------------------
    # Join survey data with meta
    # -------------------------------------------------
    tmp_data_plot = (
        data
        .merge(tmp_vars, on="vars", how="left")
        .loc[lambda df: df["plot"].notna()]
        .copy()
    )

    if tmp_data_plot.shape[0] == 0:
        vars_list = ", ".join(tmp_vars["vars"].unique())
        raise ValueError(
            f"Error in get_plotdata(): Can't join meta data with "
            f"limesurvey data. Check: {vars_list}"
        )

    # -------------------------------------------------
    # Convert vals to categorical with labels
    # -------------------------------------------------
    tmp_data_plot["vals"] = pd.Categorical(
        tmp_data_plot["vals"],
        categories=tmp_item_labels["code"],
        ordered=True
    )

    # Replace codes with label names
    label_map = dict(
        zip(tmp_item_labels["code"], tmp_item_labels["labels"])
    )

    tmp_data_plot["vals"] = tmp_data_plot["vals"].map(label_map)

    # -------------------------------------------------
    # Adjust vars label if audience == "all"
    # -------------------------------------------------
    if audience == "all":
        tmp_data_plot["vars"] = (
            tmp_data_plot["vars"]
            + " ("
            + tmp_data_plot["type"]
            + ")"
        )

    # -------------------------------------------------
    # Group and summarise
    # -------------------------------------------------
    plotdata = (
        tmp_data_plot
        .groupby(["vars", "vals", "label_short"], dropna=False)
        .size()
        .reset_index(name="anz")
    )

    # Calculate percentages per vars
    plotdata["p"] = (
        plotdata
        .groupby("vars")["anz"]
        .transform(lambda x: round(x / x.sum() * 100, 1))
    )

    plotdata["label_n"] = plotdata["p"].round(0).astype(int).astype(str) + "%"

    plotdata["set"] = str(labelset)

    return plotdata
