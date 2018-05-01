import logging
import time
import random
from slackclient import SlackClient
from src.str_utils import find_element_in_string
import giphypop

logger = logging.getLogger()
logging.basicConfig()
logger.setLevel(logging.DEBUG)


class SlackEventHandler:

    def __init__(self,
                 slack_token,
                 random_reply_flg=False,
                 random_gif_flg=False,
                 set_typing_flg=False,
                 mark_read_flg=False,
                 someones_talking_about_you_flg=False,
                 magic_eight_flg=False,
                 run_level="DM Only",
                 users=None,
                 responses=None,
                 stay_channel=None
                 ):
        """
        :param slack_token: (str) API token to connect to Slack
        :param random_reply_flg: (Bool) True if you want the handler to perform the random_reply handling
        :param random_gif_flg: (Bool) True if you want the handler to turn your random replies into gifs
        :param set_typing_flg: (Bool) True if you want the handler to perform the set_typing handling
        :param mark_read_flg: (Bool) True if you want the handler to perform the mark_read handling
        :param someones_talking_about_you_flg: (Bool) True if you want the handler to perform someones_talking_about_you
            handling
        :param magic_eight_flg: (Bool) True if you want the handler to perform magic_eight handling
        :param run_level: (str) Works on 3 levels: DM Only (only direct messages), Private (dms and private channels),
            and all
        :param users: ([str]) List of users for whom events should be handled, or 'All'; defaults to None
        :param responses: ([str]) If using the random_reply, this is the list of custom responses
        :param stay_channel: (str) channel to use if you're doing someones_talking_about_you
        """
        self.slack_token = slack_token
        self.random_reply_flg = random_reply_flg
        self.random_gif_flg = random_gif_flg
        self.set_typing_flg = set_typing_flg
        self.mark_read_flg = mark_read_flg
        self.someones_talking_about_you_flg = someones_talking_about_you_flg
        self.magic_eight_flg = magic_eight_flg
        self.run_level = run_level
        if users == 'All':
            sc = SlackClient(self.slack_token)
            sc.rtm_connect()
            self.users = [user['id'] for user in sc.api_call("users.list")['members']]
        else:
            self.users = users
        if responses:
            self.responses = responses
        else:
            # default responses if none provided
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
        self.stay_channel = stay_channel

    def begin(self, length=-1):
        """
        Begin handling events
        :param length: (int) Number of seconds to continue loop; -1 if should not end
        :return: None
        """

        sc = SlackClient(self.slack_token)
        try:
            if sc.rtm_connect():
                # get list of all users
                all_users = [
                    {
                        'name': user['name'],
                        'id': user['id'],
                        'first_name': user['profile']['first_name'],
                        'last_name': user['profile']['last_name']
                    }
                    for user in sc.api_call("users.list")['members']
                    if 'first_name' in user['profile'].keys() and 'last_name' in user['profile'].keys()]

                start_time = time.time()

                # connect to server and start monitoring
                while sc.server.connected and (time.time() <= start_time+length or length == -1):
                    event = sc.rtm_read()

                    try:
                        if event:
                            logger.debug(event)

                            # check event type and determine if action should be taken
                            msg_type = self.get_msg_type(sc, event)
                            logger.debug(msg_type)
                            if (self.run_level == 'DM Only' and msg_type == 'IM') or \
                                (self.run_level == 'Private' and msg_type != 'Public') or\
                                    self.run_level == 'All':

                                # if message is in correct scope, perform designated tasks
                                if self.random_reply_flg:
                                    self.random_reply(sc, event)
                                if self.mark_read_flg:
                                    self.mark_read(sc, event, msg_type)
                                if self.someones_talking_about_you_flg:
                                    self.someones_talking_about_you(sc, event, msg_type, all_users)
                                if self.magic_eight_flg:
                                    self.magic_eight(sc, event)
                            else:
                                logger.debug("Message not in scope.")
                        time.sleep(1)

                    except KeyError:
                        logger.debug("Ignore this event: " + str(event))

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
                    (event[0]['user'] in self.users):
                randint = random.randint(0, len(self.responses) - 1)

                message = self.responses[randint]
                if self.random_gif_flg:
                    g = giphypop.Giphy()
                    message = "{m}\n{v}".format(
                        v=[x for x in g.search(message)][0],
                        m=message)
                    print(message)
                sc.rtm_send_message(event[0]['channel'], message)

        except KeyError:
            if 'type' not in event[0].keys():
                logger.debug("Don't worry about this one.")
                logger.debug(event)
            else:
                raise

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
            if 'type' not in event[0].keys():
                logger.debug("Don't worry about this one.")
                logger.debug(event)
            else:
                raise

    def someones_talking_about_you(self, sc, event, msg_type, all_users):
        """
        :param sc: SlackClient used to connect to server
        :param event: event to be handled by the mark_read
        :param msg_type: type of message
        :param all_users: all users in slack environment
        :return:
        """

        try:
            users_to_notify = []

            if event[0]['type'] == 'message' and msg_type != 'Public':
                text = event[0]['text']
                for user in all_users:
                    if find_element_in_string(text.lower(),
                                              user['first_name'].lower() + ' ' + user['last_name'].lower()) != -1 :
                        users_to_notify.append(user)

                if len(users_to_notify) > 0:
                    user_ids = [user['id'] for user in users_to_notify]

                    not_all_users_in_convo = False
                    convo_members = sc.api_call("conversations.members", channel=event[0]['channel'])
                    for user in user_ids:
                        if user not in [cv for cv in convo_members['members']]:
                            not_all_users_in_convo = True

                    if not_all_users_in_convo:
                        message = """Hey <@{u}> 
                        
                        <@{c}> were talking about you in a private message!
                        
                        Here's what they said:
                        
                        {t}
                        """.format(u="> <@".join(user_ids),
                                   c="> <@".join([cv for cv in convo_members['members']]),
                                   t=text)

                        sc.rtm_send_message(self.stay_channel, message)

        except KeyError:
            if 'type' not in event[0].keys():
                logger.debug("Don't worry about this one.")
                logger.debug(event)
            else:
                raise

    def magic_eight(self, sc, event):
        """
        :param sc: SlackClient used to connect to server
        :param event: event to be handled by the random_reply
        :return:
        """
        try:
            if event and \
                event[0]['type'] == 'message' and \
                    (event[0]['user'] in self.users):
                randint = random.randint(0, 10)
                print(find_element_in_string(event[0]['text'], '?'))
                if find_element_in_string(event[0]['text'], '?') >= 0:
                    g = giphypop.Giphy()
                    message = "{v}\n".format(v=[x for x in g.search('magic eight ball')][randint])
                    logger.debug("TEXT: "+event[0]['text'])
                    sc.rtm_send_message(event[0]['channel'], message)
                else:
                    logger.debug("No question mark found")

        except KeyError:
            if 'type' not in event[0].keys():
                logger.debug("Don't worry about this one.")
                logger.debug(event)
            else:
                raise
