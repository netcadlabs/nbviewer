class NotebookRunError(Exception):
    """Exception raised for errors while notebook run."""

    def __init__(self, *args, **kwargs):  # real signature unknown
        pass


class NotebookOutputError(Exception):
    """Exception raised for errors about notebooks outputs"""

    def __init__(self, *args, **kwargs):  # real signature unknown
        pass


class NotebookNotFoundError(Exception):
    """ Notebook not found. """

    def __init__(self, *args, **kwargs):  # real signature unknown
        pass


class NotebookOutputNotFoundError(NotebookOutputError):
    """ Notebook output not found. """

    def __init__(self, *args, **kwargs):  # real signature unknown
        pass
