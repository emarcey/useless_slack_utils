class InvalidFlagNameException(Exception):
    """
    Use if the user tries to update with a bad flag
    """

    def __init__(self, message, *args):
        self.message = message


class TypeNotHandledException(Exception):
    """
    Use if the data type for a field is not accepted by the method
    """

    def __init__(self, message, *args):
        self.message = message


class BadStatusCodeException(Exception):
    """
    Use if a request does not return a 200 status code
    """

    def __init__(self, url, status_code, *args):
        self.message = "Status Code {s} received trying to reach {u}".format(s=status_code, u=url)


class NoArgumentsPassedException(Exception):
    """
    Use if a method does not have any of the expected arguments
    """

    def __init__(self,message):
        self.message = message