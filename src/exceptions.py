class InvalidFlagNameException(Exception):
    """
    Use if the user tries to update with a bad flag
    """

    def __init__(self, message, *args):
        self.message = message;


class TypeNotHandledException(Exception):
    """
    Use if the data type for a field is not accepted by the method
    """

    def __init__(self, message, *args):
        self.message = message;