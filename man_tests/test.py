from pyreporter.meta_repository import MetaRepository



def main():
    meta_repo = MetaRepository()

    meta_sets = meta_repo.meta_sets
    meta_headers = meta_repo.meta_headers

    print("=== META Sets ===")
    print(meta_sets)

    print("=== META Headers ===")
    print(meta_headers)



if __name__ == "__main__":
    main()
