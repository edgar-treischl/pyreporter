import pandas as pd

from pyreporter.utils import get_metadata, get_sname, get_data, match_meta_reports
from pyreporter.meta_repository import MetaRepository
from pyreporter.limer import limer_connect, limer_list_surveys, limer_responses, limer_release, limer_n, limer_SIDs
from pyreporter.plot import create_plotlist
from pyreporter.render_pdf import render_pdf


def main():

    # --- Manually define values ---
    snr = "0001"
    stype = "gy"
    audience = "sus"
    ubb = False
    ganztag = False
    has_N = ["sus", "elt"]
    syear = "2025"

    meta_repo = MetaRepository()
    meta_templates = meta_repo.meta_templates
    meta_reports = meta_repo.meta_reports
    meta_snames = meta_repo.meta_snames

    sname_meta = get_sname(
        meta_snames=meta_snames,
        snr=snr
    )

    print("\nReport for:", sname_meta)

    limer_connect()
    sids_df = limer_SIDs(snr=snr, ubb=ubb)
    sid = sids_df["sid"]
    print("\nSurvey ID:", sid[0])

    # --- Get long-format response data ---
    realdf = get_data(id=str(sid[0]), surveyls_title=sname_meta, ubb=ubb)
    print("\nData downloaded:", realdf.head())

    # --- Resolve report template and plot list ---
    report_meta = get_metadata(
        meta_templates=meta_templates,
        meta_reports=meta_reports,
        school=stype,
        audience=audience,
        ub=ubb,
        gt=ganztag,
        data_avail=has_N
    )
    print("\nReport meta:", report_meta)

    # --- Export all plots ---
    create_plotlist(
        meta_list=report_meta['meta'],
        snr=snr,
        year=syear,
        audience=audience,
        report=report_meta['report'],
        data=realdf,
        ubb=ubb,
        export=True
    )

    # --- Build header report ---
    header_report = match_meta_reports(
        survey_report=report_meta['report'],
        survey_plots=report_meta['meta']
    )
    print("\nHeader report:", header_report.head())

    # --- Render final PDF ---
    render_pdf(
        audience=audience,
        snr=snr,
        year=syear,
        sname=sname_meta,
        survey_n=str(int(sids_df["completed_responses"].sum())),
        duration="2",
        header_report=header_report
    )


if __name__ == "__main__":
    main()
