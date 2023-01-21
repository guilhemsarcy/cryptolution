if __name__ == '__main__':
    from modules.models.collect_data import KrakenDataCollector
    import pandas as pd

    kdc = KrakenDataCollector()
    raw_assets = kdc.get_assets()
    kdc.clean_assets(raw_assets)

    print(kdc.assets)

    try:
        data = pd.read_csv(kdc.settings["storage_path"])
    except FileNotFoundError:
        print("Data does not exist yet")
