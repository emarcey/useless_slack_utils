import logging
import os

from slackclient import SlackClient
from src.slackEventHandler import SlackEventHandler

logger = logging.getLogger()
logging.basicConfig()
logger.setLevel(logging.DEBUG)

slack_token = os.environ["SLACK_API_TOKEN"]
logger.debug(slack_token)
sc = SlackClient(slack_token)

users = [
    'USLACKBOT',
    'U9V5Q6886'
]

responses = [
    'Wow! That\'s so interesting!',
    'What hilarious hijinx you\'ve been getting up to!',
    'Where has the time gone?',
    'Curious',
    'I\'ve never thought of it that way.',
    'I\'ll keep that in mind.',
    'Thanks for letting me know.',
    'I\'ll be sure to follow up on that.'
]

seh = SlackEventHandler(os.environ["SLACK_API_TOKEN"],
                        True,
                        True,
                        True,
                        "DM Only",
                        users)

seh.begin(20)
