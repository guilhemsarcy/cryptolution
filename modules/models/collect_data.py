from __future__ import annotations
from typing import Dict, Optional, Union
from modules.models.config import COLLECTION_SETTINGS, OHLC_DATA
import os
import krakenex
import pandas as pd
import time
import json
import logging
from math import isnan
from modules.models.config import Currency
from modules.models.utils import build_df_from_schema_and_data, compute_max_for_given_filter

logger = logging.getLogger('collect data')
logging.basicConfig(level=logging.INFO)


class KrakenDataCollector:
    """
    Class for data ingestion from Kraken API
    """
    def __init__(
            self,
            collection_settings: Dict[str, str] = COLLECTION_SETTINGS,
            ohlc_data_settings: Dict = OHLC_DATA,
            update_asset_pairs_file: bool = False,
            kraken_client: krakenex.api.API = krakenex.API(key=os.environ.get('KRAKEN_KEY'))
    ):
        self.collection_settings = collection_settings
        self.ohlc_data_settings = ohlc_data_settings
        self.kraken_client = kraken_client
        self.update_asset_pairs_file = update_asset_pairs_file
        self.assets = {}

    def get_assets(self) -> Dict:
        """Collect asset pairs from Kraken API.
        The API returns an object with this pattern:
        {
            "1INCHEUR": {
                "wsname":" 1INCH/EUR",
                "<key_2>": "...",
                ...
                "<key_N>": "..."
            },
            ...
        }

        :return: assets pairs
        :raises: ValueError: if Kraken API not available
        """

        asset_pairs = self.kraken_client.query_public('AssetPairs')
        return asset_pairs['result']

    def clean_assets(
            self,
            raw_api_assets_pairs: Dict,
            keep_common_currencies: Optional[bool] = True
    ) -> None:
        """Prepare asset pairs & apply some filters.

        :param raw_api_assets_pairs: payload provided by Kraken API when asking for asset pairs
        :param keep_common_currencies: whether we should only keep most common currencies.
        This also removes the pairs that would compare anything to something that is not a common currency

        :return: cleaned asset pairs
        """
        cleaned_asset_pairs = {
            p: {
                'wsname': raw_api_assets_pairs[p]['wsname'],
                'asset': raw_api_assets_pairs[p]['wsname'].split('/')[0],
                'currency': raw_api_assets_pairs[p]['wsname'].split('/')[1]
            }
            for p in raw_api_assets_pairs
        }

        if keep_common_currencies:
            cleaned_asset_pairs = {
                k: v for k, v in cleaned_asset_pairs.items()
                if k.endswith(tuple([e.value for e in Currency]))
            }

        self.assets = cleaned_asset_pairs

    def get_ohlc_data(
            self,
            asset_pair: str,
            interval_in_minutes: str,
            starting_timestamp: int
    ) -> Dict:
        """Collect OHLC (movement of prices) data from Kraken API.
        The API returns an object with this pattern:
        {
            'error': [],
            'result': {
                'PONDEUR': [
                    [
                        1672531200,
                        '0.006972',
                        '0.007227',
                        '0.006972',
                        '0.007227',
                        '0.007131',
                        '53305.80189461',
                        2
                    ],
                    [
                        1672617600,
                        '0.007291',
                        '0.007473',
                        '0.007135',
                        '0.007439',
                        '0.007346',
                        '5178835.49719057',
                        91
                    ],
                    ...
                ]
            }
        }

        :param asset_pair: name of the asset pair
        :param interval_in_minutes: range of the time interval for the research
        :param starting_timestamp: from when the research should start
        :return: OHLC data for the given asset pair
        """
        ohlc_data = self.kraken_client.query_public(
            'OHLC',
            {
                'pair': asset_pair,
                'interval': interval_in_minutes,
                'since': starting_timestamp
            }
        )
        return ohlc_data['result'][asset_pair]

    def compute_starting_timestamp(self, last_tmsp: Union[int, float]) -> int:
        """
        Compute the next starting timestamp based of provided timestamp and config

        :param last_tmsp: last timestamp registered
        :return: next starting timestamp
        """
        if not isnan(last_tmsp):
            since = last_tmsp + int(self.collection_settings['query_period_in_minutes'])
        else:
            since = 0
        return since

    def get_differential_ohlc_asset_data(
            self,
            asset_pair: str,
            existing_data_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Collect data from Kraken API, starting from last ingested data for each asset pair.

        :param asset_pair: targeted asset pair
        :param existing_data_df: existing data (already ingested)
        :return: augmented data (existing data + new data)
        """

        max_timestamp = compute_max_for_given_filter(
            df=existing_data_df,
            maxed_field='tmsp',
            filter_field='asset_pair',
            filter_value=asset_pair,
        )
        starting_timestamp = self.compute_starting_timestamp(last_tmsp=max_timestamp)

        ohlc_asset_data = self.get_ohlc_data(
            asset_pair=asset_pair,
            interval_in_minutes=self.collection_settings['query_period_in_minutes'],
            starting_timestamp=starting_timestamp
        )

        nbr_of_points = len(ohlc_asset_data)
        asset_time_list = [
            time.strftime(
                '%Y-%m-%d %H:%M:%S',
                time.localtime(ohlc_asset_data[i][self.ohlc_data_settings['data_index']['timestamp']])
            )
            for i in range(nbr_of_points)
        ]  # raw period
        asset_tmsp_list = [
            ohlc_asset_data[i][self.ohlc_data_settings['data_index']['timestamp']]
            for i in range(nbr_of_points)
        ]
        asset_open_prices = [
            ohlc_asset_data[i][self.ohlc_data_settings['data_index']['opening_price']]
            for i in range(nbr_of_points)
        ]  # price at the beginning of the period
        asset_close_prices = [
            ohlc_asset_data[i][self.ohlc_data_settings['data_index']['ending_price']]
            for i in range(nbr_of_points)
        ]  # price at the end of the period
        asset_volumes = [
            ohlc_asset_data[i][self.ohlc_data_settings['data_index']['volume']]
            for i in range(nbr_of_points)
        ]  # number of shares traded

        asset_pairs = [asset_pair] * nbr_of_points
        wsnames = [self.assets[asset_pair]['wsname']] * nbr_of_points
        assets = [self.assets[asset_pair]['asset']] * nbr_of_points
        currencies = [self.assets[asset_pair]['currency']] * nbr_of_points

        new_data_df = build_df_from_schema_and_data(
            schema=self.ohlc_data_settings['schema'],
            data=[
                asset_pairs, wsnames, assets, currencies, asset_time_list,
                asset_tmsp_list, asset_open_prices, asset_close_prices, asset_volumes
            ]
        )
        data = pd.concat([existing_data_df, new_data_df])
        return data

    def get_differential_ohlc_data(self, existing_data_df: pd.DataFrame) -> pd.DataFrame:
        """Merge data collected from Kraken API, for all the assets targeted.

        :param existing_data_df: existing data (already ingested)
        :return: the concatened data
        """
        data = pd.DataFrame()
        for asset in self.assets:
            logger.info(
                f"{time.strftime('%Y-%m-%d %H:%M:%S')} : trying to collect data for asset pair {asset}"
            )
            asset_data = self.get_differential_ohlc_asset_data(
                asset_pair=asset, existing_data_df=existing_data_df
            )
            data = pd.concat([data, asset_data]).copy()

        return data

    def perform_asset_pairs_file_update(self, file_path: str) -> None:
        """
        Update asset pairs file if required

        :param file_path: full path of the file we want to overwrite
        """
        if self.update_asset_pairs_file:
            with open(file_path, 'w') as jsn:
                json.dump(self.assets, jsn, sort_keys=True, indent=4)
