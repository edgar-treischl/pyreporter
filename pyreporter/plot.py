import pandas as pd
import numpy as np
import textwrap

from plotnine import (
    ggplot, aes, geom_bar, geom_label,
    scale_fill_manual, scale_x_discrete, scale_y_continuous,
    coord_flip, theme_minimal, theme, labs, guides, guide_legend,
    element_text, position_stack
)
from mizani.formatters import number_format


def create_ggplot(data: pd.DataFrame, ubb: bool, labels: dict):

    df = data.copy()

    # -------------------------------------------------
    # Ensure numeric columns are numeric
    # -------------------------------------------------
    for col in ["anz", "p"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Ensure stable stacking order
    df["vals"] = pd.Categorical(
        df["vals"],
        categories=labels["labels"],
        ordered=True
    )

    # -------------------------------------------------
    # UBB
    # -------------------------------------------------
    if ubb:

        df["newlable"] = pd.Categorical(df["label_short"])

        def wrap_label(x):
            return textwrap.fill(str(x), width=35)

        df["bold_labels"] = df["newlable"].astype(str).apply(wrap_label)

        reversed_levels = list(df["newlable"].cat.categories[::-1])

        breaks = list(reversed(labels["labels"].tolist()))
        colors = list(reversed(labels["colors"].tolist()))


        p = (
            ggplot(df, aes(x="newlable", y="anz", fill="vals"))
            + geom_bar(
                stat="identity",
                position="stack",
                width=0.5
            )
            + geom_label(
                aes(label="anz"),
                position=position_stack(vjust=0.5),
                size=8,
                fill="white",
                color="black"
            )
            + scale_fill_manual(
                breaks=breaks,
                values=colors,
                drop=True
            )
            + scale_x_discrete(limits=reversed_levels)
            + scale_y_continuous(
                labels=number_format(accuracy=1)  # removed breaks="pretty" for stability
            )
            + coord_flip()
            + theme_minimal(base_size=14)
            + theme(
                legend_position="bottom",
                legend_text=element_text(size=12),
                axis_text_x=element_text(size=16),
                axis_text_y=element_text(ha="left")
            )
            + labs(x="", y="Anzahl", fill="")
        )

    # -------------------------------------------------
    # NON-UBB CASE
    # -------------------------------------------------
    else:

        df["newlable"] = (
            df["vars"].astype(str)
            + ": "
            + df["label_short"].astype(str)
        )

        df["newlable"] = pd.Categorical(df["newlable"])

        def wrap_label(x):
            return textwrap.fill(str(x), width=45)

        df["bold_labels"] = df["newlable"].astype(str).apply(wrap_label)

        df["geom_label_text"] = np.where(
            df["p"] > 3,
            df["label_n"].astype(str) + "\n" + df["anz"].astype(str),
            ""
        )

        reversed_levels = list(df["newlable"].cat.categories[::-1])
        #list(reversed(labels["labels"])),
        #list(reversed(labels["colors"])),
        breaks = list(reversed(labels["labels"].tolist()))
        colors = list(reversed(labels["colors"].tolist()))

        p = (
            ggplot(df, aes(x="newlable", y="p", fill="vals"))
            + geom_bar(
                stat="identity",
                position="stack",
                width=0.5
            )
            + geom_label(
                aes(label="geom_label_text"),
                position=position_stack(vjust=0.5),
                size=8,
                fill="white",
                color="black"
            )
            + scale_fill_manual(
                breaks=breaks,
                values=colors,
                drop=True
            )
            + scale_x_discrete(limits=reversed_levels)
            + coord_flip()
            + scale_y_continuous(
                labels=number_format(accuracy=1)  # safe numeric scale
            )
            + theme_minimal(base_size=14)
            + theme(
                legend_position="bottom",
                legend_text=element_text(size=12, lineheight=0.8),
                axis_text_x=element_text(size=16),
                axis_text_y=element_text(ha="left")
            )
            + labs(x="", y="Prozent", fill="")
            + guides(fill=guide_legend(nrow=1))
        )

    return p



import pandas as pd
from pathlib import Path
from plotnine import ggsave, ggplot, aes, geom_text, theme_void
from pyreporter.meta_repository import MetaRepository
from pyreporter.utils import get_directory, get_plotdata
from pyreporter.plot import create_ggplot


def export_plot(meta,
                snr,
                audience,
                report,
                data,
                ubb=False,
                year=None,
                export=True):
    """
    Export a plot for the OES report.

    Parameters
    ----------
    meta : str
        Plot name / ID (e.g., 'A12', 'A3a', etc.).
    snr : str or int
        School number.
    audience : str
        Audience type.
    report : str
        Report template name.
    data : pd.DataFrame
        Preprocessed long-format plot data with 'vars', 'vals', 'label_short', 'set'.
    ubb : bool
        Flag passed if UBB or not.
    year : str or int
        School year (used for directory).
    export : bool
        If True, saves the plot to PDF; else returns the plot.
    """

    plot_df = get_plotdata(
        data=data,
        report_name=report,
        plot_name=meta,
        audience=audience
    )

    if plot_df.shape[0] == 0:
        # fallback empty plot
        tmp_var_plot = 6
        tmp_p = (
            ggplot(pd.DataFrame({'x':[0], 'y':[0]}), aes('x','y'))
            + geom_text(
                aes(label="Uppps ... \nhier ist etwas schief gelaufen. \n"
                          "Bitte kontaktieren Sie: \n'oes@isb.bayern.de'"),
                size=14
            )
            + theme_void()
        )
    else:
        tmp_var_plot = plot_df["vars"].nunique()

        # Optional: filter out "k. A."
        plot_df = plot_df[plot_df["vals"] != "k. A."]

        # Retrieve item labels from meta_sets for this set
        meta_repo = MetaRepository()
        meta_sets = meta_repo.meta_sets

        tmp_set_list = plot_df.groupby("set").size().reset_index(name="anz")["set"].tolist()
        if not tmp_set_list or tmp_set_list[0] is None:
            raise ValueError("No set found for plot.")
        if len(tmp_set_list) > 1:
            raise ValueError("More than one set found for plot.")

        tmp_set = tmp_set_list[0]

        tmp_item_labels = (
            meta_sets.loc[meta_sets["set"] == tmp_set]
            .sort_values("sort", ascending=True)
            .copy()
        )

        # Create the plot
        # Check which vals are missing in labels
        #missing = set(plot_df["vals"].unique()) - set(labels["labels"])
        #print(plot_df.head())
        #print(tmp_item_labels)

        #print("Missing categories:", missing)
        tmp_p = create_ggplot(plot_df, ubb=ubb, labels=tmp_item_labels)

    if export:
        # Dynamic height based on number of vars
        min_height = 4
        max_height = 8.27
        height_plot = max_height if tmp_var_plot > 5 else min_height + (max_height - min_height) * (tmp_var_plot - 1) / 4

        # Ensure directory exists
        tmp_dir = Path(get_directory(snr=snr, syear=year), "plots")
        tmp_dir.mkdir(parents=True, exist_ok=True)

        # Save plot
        tmp_p.save(
            filename=tmp_dir / f"{meta}_plot.pdf",
            width=11.69,
            height=height_plot,
            dpi=300,
            units="in"
            )
        print(f"Export plot: {meta}")
    else:
        return tmp_p


def create_plotlist(meta_list, snr, year, audience, report, data, ubb=False, export=True):
    """
    Export all plots for a report by calling export_plot for each item in meta_list.

    Parameters
    ----------
    meta_list : list[str]
        List of plot names (e.g. ['A11', 'A12', ...]).
    snr : str
        School number.
    year : str or int
        School year.
    audience : str
        Audience type (e.g. 'sus', 'elt').
    report : str
        Report template name.
    data : pd.DataFrame
        Long-format survey response data.
    ubb : bool
        Whether this is a classroom observation report.
    export : bool
        If True, saves plots to PDF; if False, returns plot objects.

    Returns
    -------
    list
        List of return values from export_plot (None when export=True).
    """
    return list(map(
        lambda x: export_plot(
            meta=x,
            snr=snr,
            year=year,
            audience=audience,
            report=report,
            data=data,
            ubb=ubb,
            export=export
        ),
        meta_list
    ))