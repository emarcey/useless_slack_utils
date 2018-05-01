import string

def find_element_in_string(s, e):
    """
    Returns -1 instead of ValueError for index()

    :Args:
        - s (str): string to search
        - e (str): element to search for
    :Returns:
        - either index of first location of e in string, or -1 if not found
    """
    try:
        return s.index(e)
    except ValueError:
        return -1


def strip_punctuation(s):
    """
    Removes all punctuation marks from the ends of a string

    :param s: (str) string to be stripped
    :return: string with all punctuation marks stripped off the sides
    """

    for ch in string.punctuation:
        s = s.strip(ch)

    return s
