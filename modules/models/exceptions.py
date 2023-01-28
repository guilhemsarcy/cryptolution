

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
