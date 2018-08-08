# useless_slack_utils
Very important Slack utilities for people who want to drive their co-workers crazy.

Uses the Slack client for Python to handle incoming events in a series of pretty useless ways.

A SlackEventHandler checks all of your incoming messages and handles them according to the utilities. This is based off the [Python-SlackClient](https://slackapi.github.io/python-slackclient/index.html).

## Methods

### Implemented:
  - **Random_Reply:** send a random reply to a user from a list any time they message you
    - Gif flag sends random reply as giphy search result
  - **Mark_Read:** For all those pesky notifications where your coworkers hit @channel on meaningless stuff. Mark those as read and ignore them.
  - **Someones_Talking_About_You:** if client user's messages contain the name of another user on the slack environment, post a message in a selected channel with the contents of the message and the parties involved all tagged
    - the user who sent the message is now identified
  - **Magic_8_Ball:** whenever someone asks you a question, send a magic 8 ball giphy
  - **Homophone_Suggest:** whenever a homophone is found, suggest the opposite
  - **Reading_Level:** Calculates the estimated reading level of a comment based on the [Flesch-Kincaid Grade Level Score](https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests#Flesch%E2%80%93Kincaid_grade_level) and responds in that channel.
  - **Sing_to_Me:** Chooses a random song from the list of popular songs on [Genius](https://genius.com) and messages each line.
  - **Clean_Your_Mouth_With_Soap:** Reprimands a user who uses a bad word from this site: http://www.bannedwordlist.com/lists/swearWords.xml

### Planned:
  - **Set_Typing:** whenever someone starts typing in a channel, set yourself to typing as well. Stop typing when they stop.


## Installation

1. Get Slack (obviously).
2. Clone the repo.
3. Set up a test token using [Python-SlackClient](https://slackapi.github.io/python-slackclient/auth.html#test-tokens).
4. Most of the packages are base Python packages, but you will need to install:
   - [giphypop](https://github.com/shaunduncan/giphypop) to send Gifs
   - [requests](http://docs.python-requests.org/en/master/) to scrape websites
   - [lxml](https://lxml.de/) to process the HTML
5. Use run_handler.py to test.

## Adding a utility

If you want to add your own utility, there's a few steps.

1. Add the method as a body of the slackEventHandler. This is the obvious one.
    - This method should have, at minimum, the parameters sc (the slack client) and event (the message event), as well as a *args
2. Check the parameters passed in the slackEventHandler.begin() method.
    - Currently, it passes sc (the slack client), event (the message event), msg_type (the type of message, i.e. DM, Public), and all_users (a list of dict objects containing information about every user except the one running the client)
    - It uses an eval() statement to pass the functions as parameters, so if you use other parameters, update the statement there.
3. Update the slackEventHandler __init__() method as follows:
    - Include the flag as an argument. The flag should follow the format {method_name}+'_flg'.
        - i.e. mark_read() should have the corresponding flag: mark_read_flg.
    - Update the self.handler_flgs dict to include your flag.
    - Update the code that sets the flags in self.handler_flgs to include your flag.