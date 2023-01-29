
import pandas as pd

from typing import List
from modules.models.exceptions import UnexpectedSchemaError


class DataChecker:
    """

    """
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def check_schema(self, schema: List[str]) -> None:
        """Check whether data schema is consistent

        :raises UnexpectedSchemaError: if schema is not what is expected
        """
        if not list(self.df.columns) == list(schema):
            raise UnexpectedSchemaError(expected_schema=schema)
