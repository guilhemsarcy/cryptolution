"""
Custom exceptions.
"""


from typing import List


class NoExistingFile(Exception):
    """
    Exception raised when no file is found for a given path.
    """

    def __init__(self, path: str):
        self.message = f"The file {path} does not exist!"

    def __str__(self):
        return self.message


class FileTypeNotHandled(Exception):
    """
    Exception raised when the file cannot be handled.
    """

    def __init__(self, path: str):
        self.message = f"A csv file is expected! You provided {path}"

    def __str__(self):
        return self.message


class UnexpectedSchemaError(Exception):
    """
    Exception raised when the df schema is unexpected.
    """

    def __init__(self, expected_schema: List[str]):
        self.message = f"An unexpected schema was found, expected schema is {expected_schema}"

    def __str__(self):
        return self.message


class NotConsistentDataForDataframe(Exception):
    """
    Exception raised when trying to build a dataframe regarding a schema with inconsistent data.

    The inconsistency can come from:
    - the number of data (for each field in the schema, it has to be the same)
    - the length of data regarding the schema (for each field in the schema, we have to provide some data)
    """

    def __init__(self, schema: List[str]):
        self.message = f"The data you provided is not consistent with {schema}"

    def __str__(self):
        return self.message


class AccessDataframeFieldFailure(Exception):
    """
    Exception raised when trying to access a dataframe field that does not exist.
    """

    def __init__(self, field_candidates: List[str]):
        self.message = f'Error trying to access the dataframe. ' \
                       f'The following fields {" or ".join(field_candidates)} may not exist'

    def __str__(self):
        return self.message


class UnknownURLError(Exception):
    """
    Exception raised when trying to access an unknown URL.
    """

    def __init__(self, url: str):
        self.message = f'Error trying to access the URL: {url}'

    def __str__(self):
        return self.message


class WrongFormatForHTML(Exception):
    """
    Exception raised when trying to soupify bad formatted html code.
    """

    def __init__(self):
        self.message = 'Error trying to soupify html code.'

    def __str__(self):
        return self.message


class NotExistingHTMLClass(Exception):
    """
    Exception raised when trying to find element from not existing class.
    """

    def __init__(self, elem_class: str):
        self.message = f'Error trying to get element from {elem_class} class.'

    def __str__(self):
        return self.message
