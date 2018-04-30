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
    'U9V5Q6886',
    'U9UHKFV9R'
]
seh = SlackEventHandler(os.environ["SLACK_API_TOKEN"],
                        random_reply_flg=False,
                        random_gif_flg=False,
                        set_typing_flg=False,
                        mark_read_flg=False,
                        someones_talking_about_you_flg=False,
                        magic_eight_flg=True,
                        run_level="DM Only",
                        users=users,
                        stay_channel='slack_py_test'
                        )

seh.begin()

