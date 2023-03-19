"""
Code for streamlit app.
"""

import json
from os import getenv

import altair as alt
import pandas as pd
import streamlit as st
from view import CryptolutionView

AWS_ACCESS_KEY_ID = getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = getenv('AWS_SECRET_ACCESS_KEY')

st.set_page_config()
st.title('Cryptolution')


CURRENCY_DISPLAY = {
    'EUR': '€',
    'USD': '$'
}


cryptolution_view = CryptolutionView(title='Cryptolution')


@st.cache
def get_historical_market_data() -> pd.DataFrame:
    """
    Get hitorical market data from previous collections.

    :return: historical market data
    """
    df = pd.read_csv("s3://cryptolution/data.csv")
    return df


data = get_historical_market_data()
with open('modules/data/pairs.json') as json_pairs:
    pairs = json.load(json_pairs)
    pairs.pop("AUDUSD", None)
    pairs.pop("ZEURZUSD", None)
    pairs.pop("ZGBPZUSD", None)
    pairs.pop("KEEPEUR", None)
    pairs.pop("KEEPUSD", None)
    pairs.pop("XREPZEUR", None)
    pairs.pop("XREPZUSD", None)

with open('modules/assets_mapping/mapping.json') as json_mapping_file:
    mapping = json.load(json_mapping_file)

asset_list_raw = [pairs[asset_pair]['asset'] for asset_pair in pairs]
asset_list_business = [mapping[a] for a in asset_list_raw]

cryptolution_view.overview(
    header_title='Overview',
    metrics=[
        {"Number of cryptocurrencies": f"#{len(set(data.asset.values).intersection(asset_list_raw))}"},
        {"Date min handled": data.time.min()[:10]},
        {"Date max handled": data.time.max()[:10]}
    ]
)

# Sidebar
st.sidebar.title("Settings")
st.sidebar.markdown('###')
currency_options = st.sidebar.selectbox(
    'Select the currency',
    ('EUR', 'USD')
)

asset_options = st.sidebar.selectbox(
    'Select the asset',
    sorted(tuple(set(asset_list_business)))
)
asset_disabled = st.sidebar.text_input(
    'Selected asset (technical)',
    [k for k, v in mapping.items() if v == asset_options][0],
    disabled=True
)

metric_options = st.sidebar.selectbox(
    'Select the metric',
    ('open_price', 'close_price', 'volume')
)


st.header('Explore historical data')

displayed_data = data[
    (data.asset == asset_disabled) &
    (data.currency == currency_options)
].copy()

displayed_data['date'] = pd.to_datetime(displayed_data['time'])

brush = alt.selection(type='interval', encodings=['x'])
line_chart = (
    alt.Chart(
        data=displayed_data,
        title=f"Evolution of {metric_options} for asset {asset_options}",
    )
    .mark_line()
    .encode(
        x=alt.X("date:T", axis=alt.Axis(title="date", titleColor='#57A44C')),
        y=alt.Y(metric_options, axis=alt.Axis(title=f'{metric_options} ({CURRENCY_DISPLAY[currency_options]})', titleColor='#57A44C'))
    )
).add_selection(
    brush
)

line = alt.Chart().mark_rule(color='firebrick').encode(
    y=f'mean({metric_options}):Q',
    size=alt.SizeValue(3)
).transform_filter(brush)
chart = alt.layer(line_chart, line, data=displayed_data)

zoomed_chart = (
    alt.Chart(
        data=displayed_data,
        title="Zoomed",
    )
    .mark_line()
    .encode(
        x=alt.X("date:T", axis=alt.Axis(title="date", titleColor='#57A44C')),
        y=alt.Y(metric_options, axis=alt.Axis(title=f'{metric_options} ({CURRENCY_DISPLAY[currency_options]})', titleColor='#57A44C'))
    )
).transform_filter(
    brush
)
st.altair_chart(chart & zoomed_chart, theme="streamlit", use_container_width=True)
