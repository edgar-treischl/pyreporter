import pandas as pd

from pyreporter.utils import get_metadata
from pyreporter.meta_repository import MetaRepository





def main():

    meta_repo = MetaRepository()

    meta_templates = meta_repo.meta_templates
    meta_reports = meta_repo.meta_reports

    # --- Manually define values (like your R example) ---
    stype = "gy"     # school
    audience = "sus"              # audience
    ubb = False                     # UBB flag
    ganztag = False                # Ganztag flag
    has_N = ["sus", "elt"]  # subgroup with data available

    # --- Call your metadata helper ---
    report_meta = get_metadata(
        meta_templates=meta_templates,
        meta_reports=meta_reports,
        school=stype,
        audience=audience,
        ub=ubb,
        gt=ganztag,
        data_avail=has_N
    )

    print("=== RESULT ===")
    print("Report template:", report_meta["report"])
    print("Plots:")
    for plot in report_meta["meta"]:
        print("-", plot)


if __name__ == "__main__":
    main()
