"""Views for the streamlit app."""

from typing import Dict

import altair as alt
import pandas as pd
import streamlit as st
from components import column_metrics
from settings import Currencies, Metrics


class CryptolutionView:
    """
    Class for the streamlit app view.
    """

    def __init__(
            self,
            title: str,
            data: pd.DataFrame,
            pairs: Dict[str, Dict[str, str]],
            asset_name_mapping: Dict[str, str]
    ):
        self.title = title
        self.data = data
        self.asset_name_mapping = asset_name_mapping
        self.asset_list_raw = [pairs[asset_pair]['asset'] for asset_pair in pairs]
        self.asset_list_business = [self.asset_name_mapping[a] for a in self.asset_list_raw]

    def sidebar(self, header_title: str = 'Settings') -> Dict:
        """
        Generate sidebar section for the app.

        :param header_title: title of the section
        :return: streamlit components related to data & charts configuration
        """
        st.sidebar.title(header_title)
        st.sidebar.markdown('###')
        currency_options = st.sidebar.selectbox(
            'Select the currency',
            tuple([c.name for c in Currencies])
        )

        asset_options = st.sidebar.selectbox(
            'Select the asset',
            sorted(tuple(set(self.asset_list_business)))
        )
        asset_disabled = st.sidebar.text_input(
            'Selected asset (technical)',
            [k for k, v in self.asset_name_mapping.items() if v == asset_options][0],
            disabled=True
        )

        metric_options = st.sidebar.selectbox(
            'Select the metric',
            tuple([m.value for m in Metrics])
        )
        return {
            "currency_options": currency_options,
            "asset_options": asset_options,
            "asset_disabled": asset_disabled,
            "metric_options": metric_options
        }

    def overview(self, header_title: str = 'Overview'):
        """
        Generate overview section for the app.

        :param header_title: title of the section
        """
        st.header(header_title)
        column_metrics(
            metrics=[
                {"Number of cryptocurrencies": f"#{len(set(self.data.asset.values).intersection(self.asset_list_raw))}"},
                {"Date min handled": self.data.time.min()[:10]},
                {"Date max handled": self.data.time.max()[:10]}
            ]
        )

    def explorer(
            self,
            asset_disabled: str,
            currency: str,
            metric: str,
            asset_name: str,
            header_title: str = 'Explore historical data'
    ):
        """
        Generate exploration section for the app.

        :param asset_disabled: technical asset name
        :param currency: currency choice
        :param metric: metric choice
        :param asset_name: asset choice
        :param header_title: title of the section
        """
        st.header(header_title)

        displayed_data = self.data[
            (self.data.asset == asset_disabled) &
            (self.data.currency == currency)
        ].copy()

        displayed_data['date'] = pd.to_datetime(displayed_data['time'])

        brush = alt.selection(type='interval', encodings=['x'])
        line_chart = (
            alt.Chart(
                data=displayed_data,
                title=f"Evolution of {metric} for asset {asset_name}",
            )
            .mark_line()
            .encode(
                x=alt.X("date:T", axis=alt.Axis(title="date", titleColor='#57A44C')),
                y=alt.Y(metric, axis=alt.Axis(title=f'{metric} ({currency})', titleColor='#57A44C'))
            )
        ).add_selection(
            brush
        )

        line = alt.Chart().mark_rule(color='firebrick').encode(
            y=f'mean({metric}):Q',
            size=alt.SizeValue(3)
        ).transform_filter(brush)
        chart = alt.layer(line_chart, line, data=displayed_data)

        zoomed_chart = (
            alt.Chart(
                data=displayed_data,
                title="Focus on selected period",
            )
            .mark_line()
            .encode(
                x=alt.X("date:T", axis=alt.Axis(title="date", titleColor='#57A44C')),
                y=alt.Y(metric, axis=alt.Axis(title=f'{metric} ({currency})', titleColor='#57A44C'))
            )
        ).transform_filter(
            brush
        )
        st.altair_chart(chart & zoomed_chart, theme="streamlit", use_container_width=True)
