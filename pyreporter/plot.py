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
    # 🔧 Ensure numeric columns are numeric
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
    # UBB CASE
    # -------------------------------------------------
    if ubb:

        df["newlable"] = pd.Categorical(df["label_short"])

        def wrap_label(x):
            return textwrap.fill(str(x), width=35)

        df["bold_labels"] = df["newlable"].astype(str).apply(wrap_label)

        reversed_levels = list(df["newlable"].cat.categories[::-1])

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
                breaks=list(reversed(labels["labels"])),
                values=list(reversed(labels["colors"])),
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
                breaks=list(reversed(labels["labels"])),
                values=list(reversed(labels["colors"])),
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