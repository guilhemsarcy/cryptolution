"""Script for data collection from Kraken."""

import json
import logging
import math
import os
import time
from itertools import islice

import krakenex
import pandas as pd
from settings import COLLECTION_SETTINGS

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def collect_data(settings=COLLECTION_SETTINGS, update_pairs=False):
    """
    Get data related to the cryptocurrency market from Kraken API, and build dataset.

    :param settings: some parameters for data collection
    :type settings: Dict
    :param update_pairs: whether we need to update the dictionnary
    :type update_pairs: bool
    """

    try:
        kraken = krakenex.API()
        kraken.load_key('../auth/kraken.key')
    except FileNotFoundError:
        kraken = krakenex.API(key=f"{os.environ.get('KRAKEN_KEY', None)}")

    interval_in_minutes = settings['query_period_in_minutes']
    result_ohlc = pd.DataFrame(columns=['asset_pair', 'wsname', 'asset', 'currency',
                                        'time', 'tmsp', 'open_price', 'close_price', 'volume'])

    logger.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} : starting to collect data from Kraken")

    ret = False
    while not ret:
        try:
            logger.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} : trying to collect the list of asset pairs")
            asset_pairs = kraken.query_public('AssetPairs')
            ret = True
        except ValueError:
            logger.error(f"{time.strftime('%Y-%m-%d %H:%M:%S')} : Kraken not available - retry after 5 sec")
            time.sleep(5)
            continue
    pairs = asset_pairs['result']
    logger.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} : list of asset pairs collected")
    pairs = {p: {'wsname': pairs[p]['wsname'],
                 'asset': pairs[p]['wsname'].split('/')[0],
                 'currency': pairs[p]['wsname'].split('/')[1]
                 } for p in pairs if p.endswith('EUR') or p.endswith('USD')
             }
    pairs = dict(islice(pairs.items(), min(settings['max_number_of_items'], len(pairs))))

    # read last data to query only diff
    try:
        data = pd.read_csv("s3://cryptolution/data.csv")
    except FileNotFoundError:
        logger.warning("Data does not exist yet")
    for k, items in enumerate(pairs.items()):
        asset_pair = items[0]
        wsname = items[1]['wsname']
        asset = items[1]['asset']
        currency = items[1]['currency']
        current_result_ohlc_asset = pd.DataFrame(columns=['asset_pair', 'wsname', 'asset', 'currency',
                                                          'time', 'tmsp', 'open_price', 'close_price', 'volume'])
        try:
            last_tmsp = data[data.asset_pair == asset_pair]['tmsp'].max()
        except UnboundLocalError:
            last_tmsp = math.nan
        if not math.isnan(last_tmsp):
            since = last_tmsp + int(interval_in_minutes) * 60
        else:
            since = 0
        ret = False
        while not ret:
            try:
                logger.info(
                    f"{time.strftime('%Y-%m-%d %H:%M:%S')} : trying to collect data for asset pair {asset_pair}")
                current_query_ohlc = kraken.query_public(
                    'OHLC', {'pair': asset_pair, 'interval': interval_in_minutes, 'since': since})
                ret = True
            except ValueError:
                logger.error(f"{time.strftime('%Y-%m-%d %H:%M:%S')} : Kraken not available - retry after 5 sec")
                time.sleep(5)
                continue

        current_data_ohlc_asset = current_query_ohlc['result'][asset_pair]
        for i in range(0, len(current_data_ohlc_asset)):
            temp_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_data_ohlc_asset[i][0]))  # period
            temp_tmsp = current_data_ohlc_asset[i][0]  # raw period
            if temp_tmsp == last_tmsp:
                continue
            temp_open_price = current_data_ohlc_asset[i][1]  # price at the beginning of the period
            temp_close_price = current_data_ohlc_asset[i][4]  # price at the end of the period
            temp_volume = current_data_ohlc_asset[i][6]  # number of shares traded
            current_result_ohlc_asset.loc[i] = [asset_pair, wsname, asset, currency, temp_time, temp_tmsp,
                                                temp_open_price, temp_close_price, temp_volume]
        logger.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} : data collected for asset pair {asset_pair}")
        logger.info(f"current progress is {str(int(float(k + 1) / float(len(pairs)) * 100))}%")

        result_ohlc = pd.concat([result_ohlc, current_result_ohlc_asset])

    logger.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} : No more data to collect from Kraken")

    try:
        data = pd.concat([data, result_ohlc])
    except UnboundLocalError:
        data = result_ohlc.copy()
    logger.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} : Pushing data to s3")
    data.to_csv("s3://cryptolution/data.csv", index=False)
    logger.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} : Data available in s3")

    if update_pairs:
        with open('data/pairs.json', 'w') as jsn:
            json.dump(pairs, jsn, sort_keys=True, indent=4)


if __name__ == '__main__':
    collect_data()
    # collect_data(update_pairs=True)
