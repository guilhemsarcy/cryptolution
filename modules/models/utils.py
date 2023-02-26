"""
Module for python utils.
"""


from typing import Any, List, Union

import pandas as pd

from modules.models.exceptions import (AccessDataframeFieldFailure,
                                       FileTypeNotHandled, NoExistingFile,
                                       NotConsistentDataForDataframe)


def read_csv_as_df(path: str) -> pd.DataFrame:
    """
    Read csv as dataframe. Path can be anything : local, s3 url etc.

    :param path: path of the file
    :return: dataframe
    :raises NoExistingFile: if file does not exist
    """

    if '.csv' not in path:
        raise FileTypeNotHandled(path)

    try:
        return pd.read_csv(filepath_or_buffer=path)
    except FileNotFoundError:
        raise NoExistingFile(path=path)


def build_df_from_schema_and_data(schema: List[str], data: List[List]) -> pd.DataFrame:
    """
    Build dataframe using a list of data.

    Example: \
    data = [[1, 2], ["A", "B"]], the corresponding schema has to be something like ["field_1", "field_2"]

    :param schema: data schema
    :param data: list of data to be mapped with schema
    :return: the dataframe built from schema and data
    """

    if len(schema) != len(data) or len(set([len(lst) for lst in data])) != 1:
        raise NotConsistentDataForDataframe(schema=schema)
    data_dict = dict(zip(schema, data))
    df = pd.DataFrame.from_dict(data_dict)

    return df


def compute_max_for_given_filter(
        df: pd.DataFrame,
        maxed_field: str,
        filter_field: str,
        filter_value: Any,
) -> Union[int, float]:
    """
    Compute the max value of a given field in a df after filtering.

    :param df: the provided df
    :param maxed_field: name of the df field we base the max on
    :param filter_field: name of the df field we want to apply filter on
    :param filter_value: value for the filter applied

    :return: the max value
    """

    if list({maxed_field, filter_field} - set(df.columns)):
        raise AccessDataframeFieldFailure(field_candidates=[maxed_field, filter_field])
    max_value = df[df[filter_field] == filter_value][maxed_field].max()
    return max_value
