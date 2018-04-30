def find_element_in_string(string,e):
    """
    Returns -1 instead of ValueError for index()

    :Args:
        - string (str): string to search
        - e (str): element to search for
    :Returns:
        - either index of first location of e in string, or -1 if not found
    """
    try:
        return string.index(e)
    except ValueError:
        return -1
