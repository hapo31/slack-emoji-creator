import os
from slackclient import SlackClient


class SlackBot():
    def __init__(self, token):
        self._client = SlackClient(token)

    def post_image(self):
        self._client
