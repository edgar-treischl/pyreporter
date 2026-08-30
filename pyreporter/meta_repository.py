import pandas as pd
from importlib.resources import files
from typing import Optional, Iterable, Dict, Any


class MetadataNotAvailableError(RuntimeError):
    """Raised when metadata is not available."""
    pass


class MetaRepository:
    """Repository for loading and accessing metadata.

    The repository loads metadata definitions from the package's
    ``pyreporter.data`` directory.

    Attributes
    ----------
    meta_templates : pandas.DataFrame
        Metadata templates.
    meta_reports : pandas.DataFrame
        Metadata reports.
    meta_sets : pandas.DataFrame
        Metadata sets.
    meta_headers : pandas.DataFrame
        Metadata headers.
    meta_mastertotemplate : pandas.DataFrame
        Mapping between metadata masters and templates.
    """
    def __init__(self):
        """Initialize the metadata repository.

        Loads the metadata CSV files bundled with the ``pyreporter``
        package.
        """
        data_dir = files("pyreporter.data")

        self.meta_templates = pd.read_csv(data_dir / "meta_templates.csv")
        self.meta_reports = pd.read_csv(data_dir / "meta_reports.csv")
        self.meta_sets = pd.read_csv(data_dir / "meta_sets.csv")
        self.meta_headers = pd.read_csv(data_dir / "meta_headers.csv")
        self.meta_mastertotemplate = pd.read_csv(data_dir / "meta_mastertotemplate.csv")



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