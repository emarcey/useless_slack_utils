# useless_slack_utils
Very important Slack utilities for the otherwise lazy among you

Uses the Slack client for Python to handle incoming events in a series of pretty useless ways.

A SlackEventHandler checks all of your incoming messages and handles them according to the utilities. This is based off the [Python-SlackClient](https://slackapi.github.io/python-slackclient/index.html).

Implemented:
  - Random_Reply: send a random reply to a user from a list any time they message you
  
Planned:
  - Set_Typing: whenever someone starts typing in a channel, set yourself to typing as well. Stop typing when they stop.
  - Mark_Read: For all those pesky notifications where your coworkers hit @channel on meaningless stuff. Mark those as read and ignore them.

## Installation

1. Get Slack (obviously).
2. Clone the repo.
3. Set up a test token using [Python-SlackClient](https://slackapi.github.io/python-slackclient/auth.html#test-tokens).
4. Use run_random_reply to test.
