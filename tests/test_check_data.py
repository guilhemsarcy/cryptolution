"""Tests for data checks"""

import pandas as pd
import pytest

from modules.models.check_data import DataChecker
from modules.models.exceptions import UnexpectedSchemaError


@pytest.fixture
def data_checker():
    return DataChecker(
        df=pd.DataFrame.from_dict(
            {
                'foo': [1],
                'bar': [2],
                'baz': [3]
            }
        )
    )


class TestCheckData:

    def test_consistent_schema(self, data_checker):
        schema = [
            'foo', 'bar', 'baz'
        ]
        assert data_checker.check_schema(schema=schema) is None

    def test_not_consistent_schema(self, data_checker):
        schema = [
            'foo', 'bar', 'qux'
        ]
        with pytest.raises(UnexpectedSchemaError):
            data_checker.check_schema(schema=schema)
