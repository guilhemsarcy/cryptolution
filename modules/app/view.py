"""Views for the streamlit app."""

from typing import Dict, List

import streamlit as st
from components import column_metrics


class CryptolutionView:
    """
    Class for the streamlit app view.
    """

    def __init__(self, title: str):
        self.title = title

    @staticmethod
    def overview(header_title: str, metrics=List[Dict]):
        """
        Generate overview section for the app.

        :param header_title: title of the section
        :param metrics: the metrics we want to be displayed
        """
        st.header(header_title)
        column_metrics(metrics=metrics)
