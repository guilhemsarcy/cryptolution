"""Script for data collection from Kraken."""

import logging
import json
import os
import time
from itertools import islice

import krakenex
import pandas as pd
from settings import COLLECTION_SETTINGS

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def collect_data(settings=COLLECTION_SETTINGS):
    """
    Get data related to the cryptocurrency market from Kraken API, and build dataset.

    :param settings: some parameters for data collection
    :type settings: Dict
    """

    try:
        kraken = krakenex.API()
        kraken.load_key('../auth/kraken.key')
    except FileNotFoundError:
        kraken = krakenex.API(key=f"{os.environ.get('KRAKEN_KEY', None)}")

    interval_in_minutes = settings['query_period_in_minutes']
    result_ohlc = pd.DataFrame(columns=['asset_pair', 'wsname', 'asset', 'currency',
                                        'time', 'open_price', 'close_price', 'volume'])

    logger.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} : starting to collect data from Kraken")

    ret = False
    while not ret:
        try:
            logger.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} : trying to collect the list of asset pairs")
            assetPairs = kraken.query_public('AssetPairs')
            ret = True
        except ValueError:
            logger.error(f"{time.strftime('%Y-%m-%d %H:%M:%S')} : Kraken not available - retry after 5 sec")
            time.sleep(5)
    pairs = assetPairs['result']
    logger.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} : list of asset pairs collected")
    pairs = {p: {'wsname': pairs[p]['wsname'],
                 'asset': pairs[p]['wsname'].split('/')[0],
                 'currency': pairs[p]['wsname'].split('/')[1]
                 } for p in pairs if p.endswith('EUR') or p.endswith('USD')
             }
    pairs = dict(islice(pairs.items(), min(settings['max_number_of_items'], len(pairs))))

    for k, items in enumerate(pairs.items()):
        asset_pair = items[0]
        wsname = items[1]['wsname']
        asset = items[1]['asset']
        currency = items[1]['currency']
        current_result_ohlc_asset = pd.DataFrame(columns=['asset_pair', 'wsname', 'asset', 'currency',
                                                          'time', 'open_price', 'close_price', 'volume'])
        ret = False
        while not ret:
            try:
                current_query_ohlc = kraken.query_public(
                    'OHLC', {'pair': asset_pair, 'interval': interval_in_minutes})
                ret = True
            except ValueError:
                logger.error(f"{time.strftime('%Y-%m-%d %H:%M:%S')} : Kraken not available - retry after 5 sec")
                time.sleep(5)
        logger.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} : trying to collect data for asset pair {asset_pair}")

        try:
            error = current_query_ohlc['error'][0]
        except IndexError:
            error = 'No error'

        if error == 'No error':
            current_data_ohlc_asset = current_query_ohlc['result'][asset_pair]
            for i in range(0, len(current_data_ohlc_asset)):
                temp_time = time.strftime(
                    '%Y-%m-%d %H:%M:%S', time.localtime(current_data_ohlc_asset[i][0]))  # period
                # price at the beginning of the period
                temp_open_price = current_data_ohlc_asset[i][1]
                # price at the end of the period
                temp_close_price = current_data_ohlc_asset[i][4]
                # number of shares traded
                temp_volume = current_data_ohlc_asset[i][6]
                current_result_ohlc_asset.loc[i] = [asset_pair, wsname, asset, currency, temp_time,
                                                    temp_open_price, temp_close_price, temp_volume]
            logger.info(f"""{time.strftime('%Y-%m-%d %H:%M:%S')} : data collected for asset pair {asset_pair}
                - current progress is {str(int(float(k + 1) / float(len(pairs)) * 100))}% """)
            result_ohlc = pd.concat([result_ohlc, current_result_ohlc_asset])

        else:
            logger.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} : data not collected for asset pair {asset_pair}")

    logger.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} : No more data to collect from Kraken")

    result_ohlc.to_csv('data.csv', index=False)

    with open('pairs.json', 'w') as jsn:
        json.dump(pairs, jsn, sort_keys=True, indent=4)


if __name__ == '__main__':
    collect_data()
