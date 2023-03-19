"""Wrapped streamlit components."""

from typing import Dict, List

import streamlit as st


def column_metrics(metrics: List[Dict]):
    """
    Generate streamlit metrics.

    :param metrics: list of metrics
        ex. [{"metric_name": metric_value}, ...]
    """
    cols = st.columns(len(metrics))
    for idx, col in enumerate(cols):
        title = list(metrics[idx].keys())[0]
        value = metrics[idx][title]
        col.metric(title, value)
