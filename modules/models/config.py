"""
Config for models
"""

from enum import Enum


class Currency(Enum):
    EURO = 'EUR'
    DOLLAR = 'USD'


COLLECTION_SETTINGS = {
    'query_period_in_minutes': '1440',
    'storage_path': 's3://cryptolution/data.csv'  # here you have to specify your own storage path
}

OHLC_DATA = {
    'schema': [
        'asset_pair', 'wsname', 'asset', 'currency',
        'time', 'tmsp', 'open_price', 'close_price', 'volume'
    ]
}