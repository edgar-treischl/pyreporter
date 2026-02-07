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
        self.meta_snames = pd.read_csv(data_dir / "meta_snames.csv",  dtype={"SNR": str})


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