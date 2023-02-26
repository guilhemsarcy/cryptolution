if __name__ == '__main__':
    from modules.models.collect_data import KrakenDataCollector
    from modules.models.utils import read_csv_as_df
    from modules.models.exceptions import FileTypeNotHandled, NoExistingFile, UnexpectedSchemaError
    from modules.models.check_data import DataChecker

    import logging
    import time
    import pandas as pd

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)


    kdc = KrakenDataCollector()
    raw_assets = kdc.get_assets()
    kdc.clean_assets(raw_assets)

    try:
        existing_data_df = read_csv_as_df(path=kdc.collection_settings['storage_path'])
    except (FileTypeNotHandled, NoExistingFile) as err:
        logger.error(
            f"{err}"
        )
        existing_data_df = pd.DataFrame(
            columns=kdc.ohlc_data_settings['schema']
        )

    data_checker = DataChecker(df=existing_data_df)
    try:
        data_checker.check_schema(schema=kdc.ohlc_data_settings['schema'])
    except UnexpectedSchemaError as err:
        logger.error(
            f"{err}"
        )
        existing_data_df = pd.DataFrame(
            columns=kdc.ohlc_data_settings['schema']
        )

    data = kdc.get_differential_ohlc_data(existing_data_df=existing_data_df)
    logger.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} : Pushing data to s3")
    data.to_csv(kdc.collection_settings["storage_path"], index=False)
    logger.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} : Data available in s3")

    kdc.perform_asset_pairs_file_update('data/pairs.json')
