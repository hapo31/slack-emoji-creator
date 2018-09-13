import requests
from emojigen import fetch_emoji, create_emoji_url


class Slack():
    def __init__(self, hook_url: str):
        self._url = hook_url

    def post_image_url(self, text: str, back_color="FFFFFF00", color="EC71A1FF", font="notosans-mono-bold", size_fixed=False, stretch=True):
        emojigen_url = create_emoji_url(
            text, back_color, color, font, False, size_fixed, stretch)
        self.post_message(emojigen_url)

    def post_message(self, text):
        param = {
            "text": text
        }
        res = requests.post(self._url, data=param)
        res.raise_for_status()
