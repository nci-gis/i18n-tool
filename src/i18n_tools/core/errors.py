class InvalidLocaleStyle(Exception):
    """
    Exception raised for errors related to locale style configuration or parsing.
    """

    def __init__(self, locale_style: str):
        message = f"Invalid or unsupported locale style encountered: {locale_style}"
        super().__init__(message)


class InvalidJsonStructure(Exception):
    """
    Exception raised for errors related to JSON structure configuration or parsing.
    """

    def __init__(self, message: str = None):
        if message is None:
            message = "Invalid or unsupported JSON structure encountered."
        super().__init__(message)


class InvalidExcelStructure(Exception):
    """
    Exception raised for errors related to Excel structure configuration or parsing.
    """

    def __init__(self):
        message = "Invalid Excel structure encountered, e.g.: project/<name>.xlsx"
        super().__init__(message)
