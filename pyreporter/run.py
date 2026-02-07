import pandas as pd

from pyreporter.utils import get_metadata, get_sname
from pyreporter.meta_repository import MetaRepository

from pyreporter.limer import limer_connect, limer_list_surveys, limer_responses, limer_release, limer_n, limer_SIDs


def main():

    # --- Manually define values (like your R example) ---
    snr = "0001"
    stype = "gy"
    audience = "sus"      
    ubb = False                   
    ganztag = False
    has_N = ["sus", "elt"]  


    limer_connect()
    sids_df = limer_SIDs(snr=snr, ubb=ubb)
    sid = sids_df["sid"]
    print("\nReport template:", sid[0])
    
    
    df = limer_responses(
    iSurveyID= sid[0],
    sCompletionStatus="complete"
    )
    
    limer_release()


    print(df.head())



    meta_repo = MetaRepository()
    meta_templates = meta_repo.meta_templates
    meta_reports = meta_repo.meta_reports
    meta_snames = meta_repo.meta_snames


    sname_meta = get_sname(
        meta_snames=meta_snames,
        snr = snr
    )

    print(sname_meta)




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

    #plots = report_meta['plot'] 
    print(report_meta)


if __name__ == "__main__":
    main()
