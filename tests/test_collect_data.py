"""Tests for data collection from Kraken"""

from unittest.mock import MagicMock

import numpy as np
import pytest

from modules.models.collect_data import KrakenDataCollector


@pytest.fixture
def kraken_data_collector():
    return KrakenDataCollector(
        collection_settings=dict(query_period_in_minutes='60'),
        kraken_client=MagicMock()
    )


@pytest.fixture
def raw_asset_pairs():
    asset_pairs = {
        'XXRPXXBT': {
            'wsname': 'XRP/XBT',
            'foo': 'bar'
        },
        'XXBTZUSD': {
            'wsname': 'XBT/USD',
            'foo': 'bar'
        },
        'XXBTZJPY': {
            'wsname': 'XBT/JPY',
            'foo': 'bar'
        },
        'XXBTZEUR': {
            'wsname': 'XBT/EUR',
            'foo': 'bar'
        }
    }
    return asset_pairs


class TestCleanAssets:

    def test_clean_assets_default(self, kraken_data_collector, raw_asset_pairs):
        kraken_data_collector.clean_assets(raw_asset_pairs)
        assert kraken_data_collector.assets == {
            'XXBTZUSD': {
                'wsname': 'XBT/USD',
                'asset': 'XBT',
                'currency': 'USD'
            },
            'XXBTZEUR': {
                'wsname': 'XBT/EUR',
                'asset': 'XBT',
                'currency': 'EUR'
            }
        }

    def test_clean_assets_all_currencies(self, kraken_data_collector, raw_asset_pairs):
        kraken_data_collector.clean_assets(
            raw_api_assets_pairs=raw_asset_pairs,
            keep_common_currencies=False
        )
        assert kraken_data_collector.assets == {
            'XXRPXXBT': {
                'wsname': 'XRP/XBT',
                'asset': 'XRP',
                'currency': 'XBT'
            },
            'XXBTZUSD': {
                'wsname': 'XBT/USD',
                'asset': 'XBT',
                'currency': 'USD'
            },
            'XXBTZJPY': {
                'wsname': 'XBT/JPY',
                'asset': 'XBT',
                'currency': 'JPY'
            },
            'XXBTZEUR': {
                'wsname': 'XBT/EUR',
                'asset': 'XBT',
                'currency': 'EUR'
            }
        }


class TestGetData:

    def test_compute_starting_timestamp_nan(self, kraken_data_collector):
        assert kraken_data_collector.compute_starting_timestamp(np.nan) == 0

    def test_compute_starting_timestamp_not_nan(self, kraken_data_collector):
        assert kraken_data_collector.compute_starting_timestamp(40) == 100
