"""
Data checks.
"""

from typing import List

import pandas as pd

from modules.models.exceptions import UnexpectedSchemaError


class DataChecker:
    """
    Class for data checks.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def check_schema(self, schema: List[str]) -> None:
        """
        Check whether data schema is consistent.

        :param schema: list of columns for comparison
        :raises UnexpectedSchemaError: if schema is not what is expected
        """
        if not list(self.df.columns) == list(schema):
            raise UnexpectedSchemaError(expected_schema=schema)
