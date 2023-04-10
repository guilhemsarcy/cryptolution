"""Views for the streamlit app."""

from typing import Dict

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

    def sidebar(self, header_title: str = 'Settings'):
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
