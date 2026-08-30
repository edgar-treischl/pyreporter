

from pyreporter.meta_repository import MetaRepository

meta_repo = MetaRepository()
meta_snames = meta_repo.meta_snames

tmp_name = meta_snames[meta_snames['SNR'] == "0002"]

    # Check if more than one name is found
if len(tmp_name) > 1:
    raise ValueError("Error in get_sname(): More than one school name found.")

    # If no name is found
if len(tmp_name) == 0:
    print("School name not available.")

# Return the school name (as a string)
sname = tmp_name.iloc[0]['SNAME']
print(sname)