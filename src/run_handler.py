import logging
import os

from slackclient import SlackClient
from src.slackEventHandler import SlackEventHandler
logger = logging.getLogger()
logging.basicConfig()
logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    slack_token = os.environ["SLACK_API_TOKEN"]
    logger.debug(slack_token)
    sc = SlackClient(slack_token)

    users = [
        'USLACKBOT',
        'U9V5Q6886',
        'U9UHKFV9R'
    ]

    # definitely not things a real person has said
    # what
    # no
    # why i never
    responses = [
        "YOU LOOK THIRSTY",
        "WATCH YOUR ELBOWS",
        "SURPRISE MOTHERFUCKER",
        "HELLO MONEY",
        "NASTYASS COFFEE",
        "HEY MAMI",
        "ASHY ELBOWS",
        "YOUR SHIRT IS WRINKLED",
        "YOUR PANTS ARE WRINKLED",
        "WRINKLED-ASS MOTHERFUCKER",
        "I'LL SLEEP WHEN I'M DEAD",
        "I STILL LOOK SEXY",
        "I'M A 28 YEAR OLD HEDGE FUND MANAGER",
        "BELT, SHOES, WATCH",
        "FAHAD'S GOT A SMALL DICK"
    ]
    handler_flags = {
        'random_reply_flg': False,
        'random_gif_flg': False,
        'set_typing_flg': False,
        'mark_read_flg': False,
        'someones_talking_about_you_flg': False,
        'magic_eight_flg': False,
        'homophone_suggest_flg': False,
        'reading_level_flg': False,
        'sing_to_me_flg': False,
        'clean_your_mouth_with_soap_flg': True
    }

    seh = SlackEventHandler(os.environ["SLACK_API_TOKEN"],
                            handler_flags=handler_flags,
                            run_level="Private",
                            #users=users,
                            users='All',
                            responses=responses,
                            stay_channel='slack_py_test')
    print(seh.get_util_flag_choices())

    seh.begin()
