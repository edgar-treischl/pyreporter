from pyreporter.meta_repository import MetaRepository



def main():
    meta_repo = MetaRepository()

    meta_templates = meta_repo.meta_templates
    meta_reports = meta_repo.meta_reports

    print("=== META TEMPLATES ===")
    print(meta_templates)
    print()

    print("=== META REPORTS ===")
    print(meta_reports)


if __name__ == "__main__":
    main()
