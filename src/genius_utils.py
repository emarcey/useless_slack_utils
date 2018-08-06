import requests
from src import request_utils
import logging
from lxml import html

logger = logging.getLogger()
logging.basicConfig()
logger.setLevel(logging.DEBUG)

def get_top_songs():
    songs = []
    r = request_utils.get_request('https://genius.com/')
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

if __name__ == '__main__':
    songs = get_top_songs()
    r = requests.get(songs[0])
    print(get_artist_song(r))