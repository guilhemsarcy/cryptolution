"""Views for the streamlit app."""

from typing import Dict

import pandas as pd
import streamlit as st
from components import column_metrics


class CryptolutionView:
    """
    Class for the streamlit app view.
    """

    def __init__(self, title: str, data: pd.DataFrame, pairs: Dict[str, Dict[str, str]], asset_name_mapping: Dict[str, str]):
        self.title = title
        self.data = data
        self.asset_list_raw = [pairs[asset_pair]['asset'] for asset_pair in pairs]
        self.asset_list_business = [asset_name_mapping[a] for a in self.asset_list_raw]

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
