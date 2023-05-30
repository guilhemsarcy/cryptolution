"""
Code for streamlit app.
"""

import json
from os import getenv

import pandas as pd
import streamlit as st
from view import CryptolutionView

AWS_ACCESS_KEY_ID = getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = getenv('AWS_SECRET_ACCESS_KEY')

st.set_page_config()
st.title('Cryptolution')


@st.cache
def get_historical_market_data() -> pd.DataFrame:
    """
    Get hitorical market data from previous collections.

    :return: historical market data
    """
    df = pd.read_csv("s3://cryptolution/data.csv")
    return df


data = get_historical_market_data()
with open('modules/assets_mapping/mapping.json') as json_mapping_file:
    asset_name_mapping = json.load(json_mapping_file)
with open('modules/data/pairs.json') as json_pairs:
    pairs = json.load(json_pairs)
    pairs = {
        p: pairs[p]
        for p in pairs
        if pairs[p]['asset'] in asset_name_mapping
    }

cryptolution_view = CryptolutionView(
    title='Cryptolution',
    data=data,
    pairs=pairs,
    asset_name_mapping=asset_name_mapping
)
cryptolution_view.overview()

sidebar = cryptolution_view.sidebar()
currency_options = sidebar["currency_options"]
asset_options = sidebar["asset_options"]
asset_disabled = sidebar["asset_disabled"]
metric_options = sidebar["metric_options"]

cryptolution_view.explorer(
    asset_disabled=asset_disabled,
    currency=currency_options,
    metric=metric_options,
    asset_name=asset_options
)
