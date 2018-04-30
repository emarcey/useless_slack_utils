# useless_slack_utils
Very important Slack utilities for the otherwise lazy among you

Uses the Slack client for Python to handle incoming events in a series of pretty useless ways.

A SlackEventHandler checks all of your incoming messages and handles them according to the utilities. This is based off the [Python-SlackClient](https://slackapi.github.io/python-slackclient/index.html).

Implemented:
  - Random_Reply: send a random reply to a user from a list any time they message you
    - Gif flag sends random reply as giphy search result
  - Mark_Read: For all those pesky notifications where your coworkers hit @channel on meaningless stuff. Mark those as read and ignore them.
    - Someones_Talking_About_You: if client user's messages contain the name of another user on the slack environment, post a message in a selected channel with the contents of the message and the parties involved all tagged
  
Planned:
  - Set_Typing: whenever someone starts typing in a channel, set yourself to typing as well. Stop typing when they stop.
  - Magic_8_Ball: whenever someone asks you a question, send a magic 8 ball giphy


## Installation

1. Get Slack (obviously).
2. Clone the repo.
3. Set up a test token using [Python-SlackClient](https://slackapi.github.io/python-slackclient/auth.html#test-tokens).
4. Most of the packages are base Python packages, but you will need to install:
  - [giphypop](https://github.com/shaunduncan/giphypop)
5. Use run_random_reply to test.
