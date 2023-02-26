"""Tests for utils"""

import math

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from modules.models.exceptions import (AccessDataframeFieldFailure,
                                       FileTypeNotHandled,
                                       NotConsistentDataForDataframe)
from modules.models.utils import (build_df_from_schema_and_data,
                                  compute_max_for_given_filter, read_csv_as_df)


class TestReadCsv:

    def test_path_does_not_relate_to_a_csv(self):
        path = 's3://foo/bar/data.cmd'

        with pytest.raises(FileTypeNotHandled):
            read_csv_as_df(path=path)


class TestBuildDf:

    def test_build_df_from_schema_and_data_success(self):
        schema = ["foo", "bar"]
        data = [[1, 2], ["A", "B"]]
        expected_df = pd.DataFrame({"foo": [1, 2], "bar": ["A", "B"]})
        built_df = build_df_from_schema_and_data(schema=schema, data=data)
        assert_frame_equal(built_df, expected_df)

    def test_build_df_from_schema_and_data_fail_mapping_first_case(self):
        schema = ["foo", "bar"]
        data = [[1, 2]]
        with pytest.raises(NotConsistentDataForDataframe):
            build_df_from_schema_and_data(schema=schema, data=data)

    def test_build_df_from_schema_and_data_fail_mapping_second_case(self):
        schema = ["foo"]
        data = [[1, 2], ["A", "B"]]
        with pytest.raises(NotConsistentDataForDataframe):
            build_df_from_schema_and_data(schema=schema, data=data)

    def test_build_df_from_schema_and_data_fail_length(self):
        schema = ["foo", "bar"]
        data = [[1, 2], ["A", "B", "C"]]
        with pytest.raises(NotConsistentDataForDataframe):
            build_df_from_schema_and_data(schema=schema, data=data)


@pytest.fixture
def dataframe():
    return pd.DataFrame(
        {
            "foo": [100, 101],
            "bar": ["baz", "baz"]
        }
    )


class TestMaxComputationWithFilter:

    def test_compute_max_for_given_filter_field_found(self, dataframe):
        assert compute_max_for_given_filter(
            df=dataframe,
            maxed_field="foo",
            filter_field="bar",
            filter_value="baz"
        ) == 101

    def test_compute_max_for_given_filter_field_not_found(self, dataframe):
        assert math.isnan(
            compute_max_for_given_filter(
                df=dataframe,
                maxed_field="foo",
                filter_field="bar",
                filter_value="qux"
            )
        )

    def test_compute_max_for_given_filter_field_fail(self, dataframe):
        with pytest.raises(AccessDataframeFieldFailure):
            compute_max_for_given_filter(
                df=dataframe,
                maxed_field="foo",
                filter_field="bars",
                filter_value="baz"
            )
