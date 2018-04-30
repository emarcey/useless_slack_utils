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
]

seh = SlackEventHandler(os.environ["SLACK_API_TOKEN"],
                        True,
                        True,
                        True,
                        users)

#runs the handler for 20 seconds
seh.begin(20)
