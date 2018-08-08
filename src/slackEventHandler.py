import logging
import time
import random
from slackclient import SlackClient
import giphypop
import re

from src.str_utils import find_element_in_string, strip_punctuation
from src.misc_utils import load_homophones
from src import web_utils
from src import exceptions

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
                 homophone_suggest_flg=False,
                 reading_level_flg=False,
                 sing_to_me_flg=False,
                 clean_your_mouth_with_soap_flg=False,
                 handler_flags=None,
                 run_level="DM Only",
                 users=None,
                 responses=None,
                 stay_channel=None,
                 init_homophones=None,
                 min_words=10,
                 bad_words=None):
        """
        :param slack_token: (str) API token to connect to Slack
        :param random_reply_flg: (Bool) True if you want the handler to perform the random_reply handling
        :param random_gif_flg: (Bool) True if you want the handler to turn your random replies into gifs
        :param set_typing_flg: (Bool) True if you want the handler to perform the set_typing handling
        :param mark_read_flg: (Bool) True if you want the handler to perform the mark_read handling
        :param someones_talking_about_you_flg: (Bool) True if you want the handler to perform someones_talking_about_you
            handling
        :param magic_eight_flg: (Bool) True if you want the handler to perform magic_eight handling
        :param homophone_suggest_flg: (Bool) True if you want the handler to perform homophone_suggest
        :param reading_level_flg: (Bool) True if you want the handler to perform reading_level
        :param sing_to_me_flg: (Bool) True if you want the handler to perform sing_to_me
        :param clean_your_mouth_with_soap_flg: (Bool) True if you want the handler to perform clean_your_mouth_with_soap
        :param handler_flags: (Dict) Dictionary of handler flags; alternative to passing each flag
        :param run_level: (str) Works on 3 levels: DM Only (only direct messages), Private (dms and private channels),
            and all
        :param users: ([str]) List of users for whom events should be handled, or 'All'; defaults to None
        :param responses: ([str]) If using the random_reply, this is the list of custom responses
        :param stay_channel: (str) channel to use if you're doing someones_talking_about_you
        :param init_homophones: (dict) override dictionary of homophones to use
        :param min_words: (int) minimum number of words allows for a reading_level check
        :param bad_words: (list) override of bad words for clean_your_mouth_with_soap
        """

        self.slack_token = None
        self.update_slack_token(slack_token)

        # handle flags for handling methods
        self.handler_flags = {
            'random_reply_flg': False,
            'random_gif_flg': False,
            'set_typing_flg': False,
            'mark_read_flg': False,
            'someones_talking_about_you_flg': False,
            'magic_eight_flg': False,
            'homophone_suggest_flg': False,
            'reading_level_flg': False,
            'sing_to_me_flg': False,
            'clean_your_mouth_with_soap_flg': False
        }

        if handler_flags:
            for flg in handler_flags:
                try:
                    if flg in self.handler_flags.keys():
                        self.update_flag(flg, handler_flags[flg])
                    else:
                        raise KeyError
                except KeyError:
                    logging.debug("Flag {f} is not a valid handling method.".format(f=flg) +
                                  " It will not be included in the event handler.")
        else:
            self.update_flag('random_reply_flg', random_reply_flg)
            self.update_flag('random_gif_flg', random_gif_flg)
            self.update_flag('set_typing_flg', set_typing_flg)
            self.update_flag('mark_read_flg', mark_read_flg)
            self.update_flag('someones_talking_about_you_flg', someones_talking_about_you_flg)
            self.update_flag('magic_eight_flg', magic_eight_flg)
            self.update_flag('homophone_suggest_flg', homophone_suggest_flg)
            self.update_flag('reading_level_flg', reading_level_flg)
            self.update_flag('sing_to_me_flg', sing_to_me_flg)
            self.update_flag('clean_your_mouth_with_soap_flg', clean_your_mouth_with_soap_flg)

        # handle bad_words
        if self.handler_flags['clean_your_mouth_with_soap_flg']:
            if bad_words:
                try:
                    if type(bad_words) in (list, set):
                        self.bad_words = set(bad_words)
                    else:
                        raise TypeError
                except TypeError:
                    logger.error("Your input bad words are an incorrect type, {t}. Expected list or set.".
                                 format(t=type(bad_words)))
                    raise
            else:
                self.bad_words = web_utils.get_bad_words()

        # handle run_level
        self.run_level = None
        self.update_run_level(run_level)

        # handle users
        try:
            if users == 'All':
                sc = SlackClient(self.slack_token)
                sc.rtm_connect()
                self.users = [user['id'] for user in sc.api_call("users.list")['members']]
            elif type(users) == list:
                self.users = users
            else:
                msg = "Passed data type {dt} to method 'add_users.' Only str or list allowed.". \
                    format(dt=type(users))
                raise exceptions.TypeNotHandledException(msg)
        except exceptions.TypeNotHandledException as e:
            logger.error(e.message)
            raise

        # handle responses
        try:
            if responses and type(responses) == list:
                self.responses = responses
            elif responses:
                msg = "Passed data type {dt} to method 'add_responses.' Only str or list allowed.". \
                    format(dt=type(responses))
                raise exceptions.TypeNotHandledException(msg)
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
        except exceptions.TypeNotHandledException as e:
            logger.error(e.message)
            raise

        # handle stay channel
        self.stay_channel = None
        self.update_stay_channel(stay_channel)

        self.homophones = load_homophones(init_homophones)

        try:
            if isinstance(min_words, int):
                self.min_words = min_words
        except TypeError:
            logger.error("Invalid type {t} for min_words; expected int".format(t=type(min_words)))
            raise

    def update_run_level(self, new_run_level):
        """
        Update the run_level for the handler

        :param new_run_level: (str) new value for run level
        :return: None
        """
        try:
            if new_run_level not in ("DM Only", "Private", "All"):
                msg = "Invalid Value for new run_level, {v}.\nAccepted values are ('DM Only','Private','All')".\
                    format(v=new_run_level)
                logger.error(msg)
                raise ValueError()
            else:
                self.run_level = new_run_level

        except ValueError:
            raise

    def update_stay_channel(self, new_stay_channel):
        """
        Update the stay_channel for the handler

        :param new_stay_channel: (str) new value for stay channel
        :return: None
        """

        try:

            if type(new_stay_channel) != str:
                msg = "Passed data type {dt} to method 'update_stay_channel.' Only str allowed.". \
                    format(dt=type(new_stay_channel))
                raise exceptions.TypeNotHandledException(msg)
            else:
                self.stay_channel = new_stay_channel

        except exceptions.TypeNotHandledException as e:
            logger.error(e.message)
            raise

    def update_slack_token(self, new_slack_token):
        """
        Update the new_slack_token for the handler

        :param new_slack_token: (str) new value for slack token
        :return: None
        """

        try:
            if type(new_slack_token) != str:
                msg = "Passed data type {dt} to method 'update_slack_token.' Only str allowed.". \
                    format(dt=type(new_slack_token))
                raise exceptions.TypeNotHandledException(msg)
            else:
                self.slack_token = new_slack_token

        except exceptions.TypeNotHandledException as e:
            logger.error(e.message)
            raise

    def update_flag(self, flag_name, flag_value):
        """
        Updates the value for the given flag

        :param flag_name: (str) name of flag to update
        :param flag_value: (str) new value for flag
        :return:
        """

        try:
            if type(flag_value) != bool:
                msg = "\nInvalid data entered for flag_name, {fn}, in method 'update_flag'.".format(fn=flag_name)
                msg += "\nReceived data type, {dt}, with value {v}.".format(dt=type(flag_value), v=str(flag_value))
                msg += "\nOnly Boolean value accepted"
                raise exceptions.TypeNotHandledException(msg)
            elif flag_name not in self.handler_flags.keys():
                message = "\n{f} is not in list of flags.\nAcceptable flag names are: {n}.".\
                    format(f=flag_name,
                           n=', '.join(self.handler_flags.keys()))
                raise exceptions.InvalidFlagNameException(message=message)
            self.handler_flags[flag_name] = flag_value

        except exceptions.InvalidFlagNameException as e:
            logger.error(e.message)
            raise

    def add_responses(self, new_responses):
        """
        Add 1+ responses for the random_reply method

        :param new_responses: 2 possible types:
            - str: single response to add
            - list: multiple responses to add
        :return: None
        """
        try:
            if type(new_responses) == str and new_responses not in self.responses:
                self.responses.append(new_responses)
            elif type(new_responses) == list:
                self.responses += new_responses
                self.responses = list(set(self.responses))
            else:
                msg = "Passed data type {dt} to method 'add_responses.' Only str or list allowed.".\
                    format(dt=type(new_responses))
                raise exceptions.TypeNotHandledException(msg)
        except exceptions.TypeNotHandledException as e:
            logger.error(e.message)
            raise

    def add_homophones(self, new_homophones, override_flg=True):
        """
        add_homophones adds additional homophones to the existing dictionary
        :param new_homophones: (dict) new homophones to add
        :param override_flg: (Bool) if True, then if there is a conflict between new and old dicts, replace old.
            If false, keep old.
        :return: None
        """

        try:
            if type(new_homophones) == dict:
                new_homophones = load_homophones(new_homophones)
                for nh in new_homophones:
                    nh_exists = nh in self.homophones.keys()
                    if override_flg or not nh_exists:
                        tmp = None
                        if nh_exists:
                            tmp = self.homophones[nh]
                        self.homophones[nh] = new_homophones[nh]

                        # remove old match if overriding
                        if override_flg and nh_exists:
                            del self.homophones[tmp]

            else:
                msg = "Passed data type {dt} to method 'add_homophones.' Only dict allowed.". \
                    format(dt=type(new_homophones))
                raise exceptions.TypeNotHandledException(msg)

        except exceptions.TypeNotHandledException as e:
            logger.error(e.message)
            raise

    def add_users(self, new_users):
        """
        Adds one or more users to the approved user list

        :param new_users: 2 types:
            - (str): single new user to add, or 'All', denoting that all users should be added
            - (list): list of new users to add
        :return: None
        """

        try:
            if type(new_users) == str and new_users == 'All':
                sc = SlackClient(self.slack_token)
                sc.rtm_connect()
                self.users = [user['id'] for user in sc.api_call("users.list")['members']]
            if type(new_users) == str and new_users not in self.users:
                self.users.append(new_users)
            elif type(new_users) == list:
                self.users += new_users
                self.users = list(set(self.users))
            else:
                msg = "Passed data type {dt} to method 'add_users.' Only str or list allowed.".\
                    format(dt=type(new_users))
                raise exceptions.TypeNotHandledException(msg)
        except exceptions.TypeNotHandledException as e:
            logger.error(e.message)
            raise

    def get_util_flag_choices(self):
        """
        Returns list of possible utility flags to choose from
        :return: Keys for handler_flags dict as a list
        """
        return list(self.handler_flags.keys())

    def begin(self, length=-1):
        """
        Begin kicks of the event handling process.
        Uses eval() to call handling method. Currently passes sc, event, msg_type and all_users to method.
        If you add a utility that uses any other arguments, you will need to update this line

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
                                for flg in self.handler_flags:
                                    if self.handler_flags[flg] and flg != 'random_gif_flg':
                                        eval_line = 'self.{f}(sc, event, msg_type, all_users)'.\
                                            format(f=flg.replace('_flg', ''))
                                        eval(eval_line)
                                # Old non-parameterized code for calling utilities
                                '''
                                if self.handler_flags['random_reply_flg']:
                                    self.random_reply(sc, event)
                                if self.handler_flags['mark_read_flg']:
                                    self.mark_read(sc, event, msg_type)
                                if self.handler_flags['someones_talking_about_you_flg']:
                                    self.someones_talking_about_you(sc, event, msg_type, all_users)
                                if self.handler_flags['magic_eight_flg']:
                                    self.magic_eight(sc, event)
                                if self.handler_flags['homophone_flg']:
                                    self.homophone_suggest(sc, event)
                                if self.handler_flags['reading_level_flg']:
                                    self.reading_level(sc, event)
                                if self.handler_flags['sing_to_me_flg']:
                                    self.sing_to_me(sc, event)
                                if self.handler_flags['clean_your_mouth_with_soap_flg']:
                                    self.clean_your_mouth_with_soap(sc, event)
                                    '''
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
        get_msg_type determines if a message event if private, public or an IM

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

    def random_reply(self, sc, event, *args):
        """
        For a given message event,
        random_reply sends a random message from the list if responses.
        If gif is enabled, sends the top result for that response from giphy

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
                if self.handler_flags['random_gif_flg']:
                    g = giphypop.Giphy()
                    message = "{m}\n{v}".format(
                        v=[x for x in g.search(message)][0],
                        m=message)

                sc.rtm_send_message(event[0]['channel'], message)

        except KeyError:
            if 'type' not in event[0].keys():
                logger.debug("Don't worry about this one.")
                logger.debug(event)
            else:
                raise

    def mark_read(self, sc, event, msg_type, *args):
        """
        For a given message event, if the event has a user notification tag, but it does not contain the user's name
        mark_read marks the channel as read up to that point

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

    def someones_talking_about_you(self, sc, event, msg_type, all_users, *args):
        """
        For a given message event, if a user's full name is found in the message text
        someones_talking_about_you sends a message to a notify channel which tags the person talked about,
        the people in the private channel, and tells the full body of the message

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
                                              user['first_name'].lower() + ' ' + user['last_name'].lower()) != -1:
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
                        
                        Here's what <@{s}> said:
                        
                        {t}
                        """.format(u="> <@".join(user_ids),
                                   c="> <@".join([cv for cv in convo_members['members']]),
                                   s=event[0]['user'],
                                   t=text)

                        sc.rtm_send_message(self.stay_channel, message)

        except KeyError:
            if 'type' not in event[0].keys():
                logger.debug("Don't worry about this one.")
                logger.debug(event)
            else:
                raise

    def magic_eight(self, sc, event, *args):
        """
        For a given message event, if a '?' is found in the message
        magic_eight sends one of the top 10 magic 8 ball gifs from giphy as a message

        :param sc: SlackClient used to connect to server
        :param event: event to be handled by the random_reply
        :return:
        """
        try:
            if event and \
                event[0]['type'] == 'message' and \
                    (event[0]['user'] in self.users):
                randint = random.randint(0, 10)
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

    def homophone_suggest(self, sc, event, *args):
        """
        For a given message event and for every homophone found in the message,
        homophone_suggest sends a message suggesting the opposite homophone

        :param sc: SlackClient used to connect to server
        :param event: event to be handled by the random_reply
        :return: None
        """
        try:
            text_words = [strip_punctuation(word) for word in
                          event[0]['text'].lower().split(' ')
                          if strip_punctuation(word) in self.homophones.keys()]

            for word in text_words:
                message = "Hey <@{u}>!\n\tYou typed {k}, but you probably meant {v}.".\
                    format(u=event[0]['user'],
                           k=word,
                           v=self.homophones[word])
                sc.rtm_send_message(event[0]['channel'], message)

        except KeyError:
            if 'type' not in event[0].keys():
                logger.debug("Don't worry about this one.")
                logger.debug(event)
            else:
                raise

    def reading_level(self, sc, event, *args):
        """
        Calculate the reading level of a given comment
        :param sc: SlackClient used to connect to server
        :param event: event to be handled by the method
        :return:
        """
        try:
            text = event[0]['text'].lower()
            sentences = len(re.findall(r'[!?\.]', text))
            if sentences == 0:
                sentences = 1
            words = text.split()

            if len(words) < self.min_words:
                logger.debug("Message too short for reading_level calculation.")
                return

            syllables = sum([len(re.findall(r'[aeiouy]+', x.rstrip('e'))) for x in words])
            reading_level = 0.39*(len(words)/sentences) + 11.8*(syllables/len(words)) - 15.59

            message = "Your comment has an estimated Flesch-Kincaid grade level of {x}.".\
                format(x=int(round(reading_level)))
            sc.rtm_send_message(event[0]['channel'], message)

        except KeyError:
            if 'type' not in event[0].keys():
                logger.debug("Don't worry about this one.")
                logger.debug(event)
            else:
                raise

    def sing_to_me(self, sc, event, *args):
        """
        Replies with song lyrics for a popular song on Genius
        :param sc: SlackClient used to connect to server
        :param event: event to be handled by the method
        :return:
        """
        try:
            text = event[0]['text'].lower()
            if text == 'sing to me':
                songs = web_utils.get_top_songs()
                n = random.randint(0, len(songs)-1)
                r = web_utils.get_request(songs[n])
                artist, song = web_utils.get_artist_song(r)
                lyrics = web_utils.get_lyrics(r)
                message = "How about {s} by {a}?".format(s=song, a=artist)
                sc.rtm_send_message(event[0]['channel'], message)
                time.sleep(1)
                for i in range(3):
                    sc.rtm_send_message(event[0]['channel'], '{n}'.format(n=i+1))
                    time.sleep(1)
                sc.rtm_send_message(event[0]['channel'], 'Go!')
                time.sleep(1)
                sc.rtm_send_message(event[0]['channel'], '')

                for line in lyrics:
                    time.sleep(1)
                    sc.rtm_send_message(event[0]['channel'], line)

        except KeyError:
            if 'type' not in event[0].keys():
                logger.debug("Don't worry about this one.")
                logger.debug(event)
            else:
                raise

    def clean_your_mouth_with_soap(self, sc, event, *args):
        """
        If it finds any of the stored bad words, reprimands user who sent message
        :param sc: SlackClient used to connect to server
        :param event: event to be handled by the method
        :return:
        """
        try:
            text = event[0]['text'].lower().split()
            clean = False
            for word in text:
                if word in self.bad_words:
                    clean = True
                    break
            if clean:
                message = "You kiss your mother with that mouth?\nClean it with soap!"
                sc.rtm_send_message(event[0]['channel'], message)

                gif_url = 'https://giphy.com/gifs/Rs05vfoiXpIOc/html5'
                sc.rtm_send_message(event[0]['channel'], '{v}\n'.format(v=gif_url))

        except KeyError:
            if 'type' not in event[0].keys():
                logger.debug("Don't worry about this one.")
                logger.debug(event)
            else:
                raise
