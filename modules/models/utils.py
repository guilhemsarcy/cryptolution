import pandas as pd

from modules.models.exceptions import NoExistingFile, FileTypeNotHandled


def read_csv_as_df(path: str) -> pd.DataFrame:
    """Read csv as dataframe. Path can be anything : local, s3 url ...

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


def load_df_to_csv(df: pd.DataFrame, path: str) -> None:
    """Load dataframe to csv

    :param df: dataframe to load
    :param path: path of the file
    """
    pass


