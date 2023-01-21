from __future__ import annotations
from typing import Dict, Optional
from modules.models.config import COLLECTION_SETTINGS
import os
import krakenex

from modules.models.config import Currency


class KrakenDataCollector:
    """

    """
    def __init__(
            self,
            settings: Dict[str, str] = COLLECTION_SETTINGS,
            kraken_client: krakenex.api.API = krakenex.API(key=os.environ.get('KRAKEN_KEY'))
    ):
        self.settings = settings,
        self.kraken_client = kraken_client
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
