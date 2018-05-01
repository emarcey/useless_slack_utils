class InvalidFlagNameException(Exception):
    """
    Use if the user tries to update with a bad flag
    """

    def __init__(self, message, *args):
        self.message = message;
