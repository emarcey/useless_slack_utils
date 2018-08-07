import requests
from src import exceptions
import logging
from lxml import html
import re

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


def get_top_songs():
    songs = []
    r = get_request('https://genius.com/')
    h = html.fromstring(r.text)
    table = h.find_class('column_layout-column_span column_layout-column_span--full')[0]
    for x in table.iter('a'):
        songs.append(x.get('href'))

    return songs


def get_artist_song(r):
    """
    Get the name of an artist and song from a Genius lyrics URL
    :param r: Request object for Genius URL
    :return: two fields: artist, song
    """
    h = html.fromstring(r.text)
    song = h.find_class('header_with_cover_art-primary_info-title')[0].text.title()
    artist = h.find_class('header_with_cover_art-primary_info-primary_artist')[0].text.title()
    return artist, song


def get_lyrics(r):
    """
    Get the lyrics for a song from a Genius lyrics URL
    :param r: Request object for Genius URL
    :return: list object containing lines of song
    """
    o_lyrics = []
    h = html.fromstring(r.text)
    lyrics = h.find_class('lyrics')[0]
    add_line = True
    for x in lyrics.iter('p'):
        for y in x.itertext():
            line = y.strip()
            if len(line) == 0:
                pass
            elif line[0] == '[' and line[len(line)-1] == ']':
                o_lyrics.append('\n')
            elif line[0] == '[' and line[len(line)-1] != ']':
                add_line = False
            elif not add_line and line[len(line)-1] == ']':
                add_line = True
                o_lyrics.append('\n')
            elif line[0] != '[' and add_line:
                o_lyrics.append(line)
    return o_lyrics


def get_bad_words():
    """
    Gets the list of bad words from http://www.bannedwordlist.com/lists/swearWords.xml
    :return: set of words (improves runtime lookup)
    """
    r = get_request('http://www.bannedwordlist.com/lists/swearWords.xml')
    return set([re.sub(r'<(\/)?word>', '', line.strip())
            for line in r.text.split('\n')
            if line.strip().startswith('<word>')])
