from pyreporter.meta_repository import MetaRepository



def main():
    meta_repo = MetaRepository()

    meta_sets = meta_repo.meta_sets

    print("=== META Data ===")
    print(meta_sets)


if __name__ == "__main__":
    main()
