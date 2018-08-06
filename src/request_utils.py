import requests
from src import exceptions
import logging
from lxml import html

logger = logging.getLogger()
logging.basicConfig()
logger.setLevel(logging.DEBUG)


def get_request(url):
    """
    Passes a url to a get request. Just a little error handling

    :param url: URL to request
    :return: Request object returned from get method
    """
    try:
        r = requests.get(url)
        if r.status_code != 200:
            raise exceptions.BadStatusCodeException(url, r.status_code)

        return r
    except exceptions.BadStatusCodeException as e:
        logger.error(e.message)
