import pandas as pd
from importlib.resources import files
from typing import Optional, Iterable, Dict, Any


class MetadataNotAvailableError(RuntimeError):
    pass


class MetaRepository:
    def __init__(self):
        data_dir = files("pyreporter.data")

        self.meta_templates = pd.read_csv(data_dir / "meta_templates.csv")
        self.meta_reports = pd.read_csv(data_dir / "meta_reports.csv")

        self._validate_schema()

    def _validate_schema(self):
        required_templates = {
            "stype", "type", "ubb", "ganztag", "report_tmpl"
        }
        required_reports = {"report", "plot", "type"}

        if not required_templates.issubset(self.meta_templates.columns):
            raise MetadataNotAvailableError("meta_templates schema mismatch")

        if not required_reports.issubset(self.meta_reports.columns):
            raise MetadataNotAvailableError("meta_reports schema mismatch")

    # 🔥 moved here
    def get_metadata(
        self,
        school: str,
        audience: str,
        ub: bool,
        gt: bool,
        data_avail: Optional[Iterable[str]] = None,
    ) -> Dict[str, Any]:

        tmpl_mask = (
            (self.meta_templates["stype"] == school)
            & (self.meta_templates["type"] == audience)
            & (self.meta_templates["ubb"] == ub)
            & (self.meta_templates["ganztag"] == gt)
        )

        report_templates = (
            self.meta_templates.loc[tmpl_mask, "report_tmpl"]
            .unique()
        )

        if len(report_templates) > 1:
            raise ValueError(
                "Error in get_metadata(): More than 1 report template found."
            )

        if len(report_templates) == 0:
            raise ValueError(
                "Error in get_metadata(): No report template found."
            )

        report_template = report_templates[0]

        report_meta_df = self.meta_reports[
            self.meta_reports["report"] == report_template
        ]

        if audience == "all":
            if data_avail is None:
                raise ValueError(
                    "data_avail must be provided for audience='all'"
                )
            report_meta_df = report_meta_df[
                report_meta_df["type"].isin(data_avail)
            ]

        report_meta = (
            report_meta_df
            .sort_values("plot")
            ["plot"]
            .unique()
            .tolist()
        )

        if not report_meta:
            raise ValueError(
                "Error in get_metadata(): Plot(s) not found in meta data."
            )

        return {
            "report": report_template,
            "meta": report_meta,
        }
