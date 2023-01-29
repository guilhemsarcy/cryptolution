if __name__ == '__main__':
    from modules.models.collect_data import KrakenDataCollector
    from modules.models.utils import read_csv_as_df
    from modules.models.exceptions import FileTypeNotHandled, NoExistingFile, UnexpectedSchemaError
    from modules.models.config import OHLC_DATA
    from modules.models.check_data import DataChecker

    import pandas as pd

    kdc = KrakenDataCollector()
    raw_assets = kdc.get_assets()
    kdc.clean_assets(raw_assets)

    print(kdc.assets)

    try:
        data = read_csv_as_df(kdc.settings['storage_path'])
    except (FileTypeNotHandled, NoExistingFile) as err:
        print(f"{err}")
        data = pd.DataFrame(
            columns=OHLC_DATA['schema']
        )

    data_checker = DataChecker(df=data)
    try:
        data_checker.check_schema(schema=OHLC_DATA['schema'])
    except UnexpectedSchemaError as err:
        print(f"{err}")
        data = pd.DataFrame(
            columns=OHLC_DATA['schema']
        )
