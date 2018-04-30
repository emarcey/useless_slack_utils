import logging
import time
import random
from slackclient import SlackClient
from src.str_utils import find_element_in_string

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
            if sc.rtm_connect():
                start_time = time.time()
                while sc.server.connected and (time.time() <= start_time+length or length ==-1):
                    event = sc.rtm_read()

                    try:
                        if event:
                            logger.debug(event)

                            msg_type = self.get_msg_type(sc, event)
                            logger.debug(msg_type)
                            if (self.run_level == 'DM Only' and msg_type == 'IM') or \
                                (self.run_level == 'Private' and msg_type != 'Public') or\
                                    self.run_level == 'All':

                                #if message is in correct scope, perform designated tasks
                                if self.random_reply_flg:
                                    self.random_reply(sc, event, msg_type)
                                if self.mark_read_flg:
                                    self.mark_read(sc, event, msg_type)
                            else:
                                logger.debug("Message not in scope.")
                        time.sleep(1)

                    except KeyError:
                        logger.debug(event)
                        logger.debug("Ignore this event")

                if time.time() > start_time + length:
                    logger.debug("Event handling completed.\nStopping Slack monitor.")
        except KeyboardInterrupt:
            logger.debug("Stopping Slack monitor.")
            raise

    def get_msg_type(self, sc, event):
        """
        :param sc: SlackClient used to connect to server
        :param event: event to be handled by the random_reply
        :return: type of message (Public, Private or IM)
        """
        im_info = sc.api_call("im.info", channel=event[0]['channel'])
        if 'ok' in im_info.keys() and im_info['ok'] is False:
            dm_info = sc.api_call("groups.info", channel=event[0]['channel'])
            if 'ok' in dm_info.keys() and dm_info['ok'] is False:
                return 'Public'
            else:
                return 'Private'
        else:
            return 'IM'

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
                sc.rtm_send_message(event[0]['channel'], self.responses[randint])

        except KeyError:
            print(event)
            print(event[0].keys())
            if 'type' not in event[0].keys():
                logger.debug("Don't worry about this one.")
                logger.debug(event)

    def mark_read(self, sc, event, msg_type):
        """
        :param sc: SlackClient used to connect to server
        :param event: event to be handled by the mark_read
        :param msg_type: type of message
        :return:
        """
        try:
            if event[0]['type'] == 'message':

                text = event[0]['text']

                if find_element_in_string(text, '<') != -1 and \
                        find_element_in_string(text, '>') != -1 and \
                        find_element_in_string(text, sc.server.username) == -1:
                    if msg_type == 'IM':
                        sc.api_call("im.mark", channel=event[0]['channel'], ts=event[0]['ts'])
                    elif msg_type == 'Private':
                        sc.api_call("groups.mark", channel=event[0]['channel'], ts=event[0]['ts'])
                    else:
                        sc.api_call("channels.mark", channel=event[0]['channel'], ts=event[0]['ts'])
                else:
                    logger.debug('Don\'t change')

        except KeyError:
            print(event)
            print(event[0].keys())
            if 'type' not in event[0].keys():
                logger.debug("Don't worry about this one.")
                logger.debug(event)
