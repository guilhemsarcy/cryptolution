
from typing import List


class NoExistingFile(Exception):
    """
    Exception raised when no file is found for a given path
    """
    def __init__(self, path: str):
        self.message = f"The file {path} does not exist!"

    def __str__(self):
        return self.message


class FileTypeNotHandled(Exception):
    """
    Exception raised when the file cannot be handled
    """

    def __init__(self, path: str):
        self.message = f"A csv file is expected! You provided {path}"

    def __str__(self):
        return self.message


class UnexpectedSchemaError(Exception):
    """
        Exception raised when the df schema is unexpected
        """

    def __init__(self, expected_schema: List[str]):
        self.message = f"An unexpected schema was found, expected schema is {expected_schema}"

    def __str__(self):
        return self.message
