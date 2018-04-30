import logging
import os
import time
import random
from slackclient import SlackClient

logger = logging.getLogger()
logging.basicConfig()
logger.setLevel(logging.DEBUG)


class SlackEventHandler:

    def __init__(self,
                 slack_token,
                 random_reply_flg=False,
                 set_typing_flg=False,
                 mark_read_flg=False,
                 run_level="DM Only",
                 users=None,
                 responses=None
                 ):
        """
        :param slack_token: (str) API token to connect to Slack
        :param random_reply_flg: (Bool) True if you want the handler to perform the random_reply handling
        :param set_typing_flg: (Bool) True if you want the handler to perform the set_typing handling
        :param mark_read_flg: (Bool) True if you want the handler to perform the mark_read handling
        :param run_level: (str) Works on 3 levels: DM Only (only direct messages), Private (dms and private channels), and all
        :param users: ([str]) List of users for whom events should be handled
        :param responses: ([str]) If using the random_reply, this is the list of custom responses
        """
        self.slack_token = slack_token
        self.random_reply_flg = random_reply_flg
        self.set_typing_flg = set_typing_flg
        self.mark_read_flg = mark_read_flg
        self.run_level = run_level
        self.users = users
        if responses:
            self.responses = responses
        else:
            #default responses if none provided
            self.responses = [
                'Wow! That\'s so interesting!',
                'What hilarious hijinx you\'ve been getting up to!',
                'Where has the time gone?',
                'Curious',
                'I\'ve never thought of it that way.',
                'I\'ll keep that in mind.',
                'Thanks for letting me know.',
                'I\'ll be sure to follow up on that.'
            ]

    def begin(self, length=-1):
        """
        Begin handling events
        :param length: (int) Number of seconds to continue loop; -1 if should not end
        :return: None
        """

        sc = SlackClient(self.slack_token)
        try:
            channel_list = sc.api_call("channels.list")['channels']

            if sc.rtm_connect():
                start_time = time.time()
                while sc.server.connected and (time.time() <= start_time+length or length ==-1):
                    event = sc.rtm_read()
                    try:
                        if event:
                            if (self.run_level == 'DM Only' and
                                        event[0]['channel'] not in [ch['name'] for ch in channel_list]) or \
                                    (self.run_level == 'Private' and
                                             (event[0]['channel'] not in [ch['name'] for ch in channel_list] or
                                                event[0]['channel'] in [ch['name'] for ch in channel_list if ch['is_private'] is True])) or \
                                    (self.run_level == 'All'):
                                if self.random_reply_flg:
                                    self.random_reply(sc, event)

                        time.sleep(1)

                        if time.time() > start_time+length:
                            logger.debug("Event handling completed.\nStopping Slack monitor.")

                    except KeyError:
                        logger.debug(event)
                        logger.debug("Ignore this event")
        except KeyboardInterrupt:
            logger.debug("Stopping Slack monitor.")
            raise

    def random_reply(self, sc, event):
        """
        :param sc: SlackClient used to connect to server
        :param event: event to be handled by the random_reply
        :return:
        """

        try:
            if event and \
                            event[0]['type'] == 'message' and \
                            event[0]['user'] in self.users:
                randint = random.randint(0, len(self.responses) - 1)
                sc.rtm_send_message(event[0]['channel'],
                                    self.responses[randint])
        except KeyError:
            print(event)
            print(event[0].keys())
            if 'type' not in event[0].keys():
                logger.debug("Don't worry about this one.")
                logger.debug(event)
