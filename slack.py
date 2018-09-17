import requests

from emojigen import fetch_emoji, create_emoji_url
from emoji import post_emoji, remove_emoji

from post_tool import post_json

SHARE_PUBLIC_URL = "/api/files.sharedPublicURL"
URL_SLACK = "https://{workspace}.slack.com"


class Slack():
    def __init__(self, workspace_name: str, session, hook_url: str, oauth_token: str):
        self._workspace_name = workspace_name
        self._session = session
        self._hook_url = hook_url
        self._base_url = URL_SLACK.format(workspace=workspace_name)
        self._oauth_token = oauth_token

    def post_message(self, text):
        param = {
            "text": text
        }
        res = post_json(self._hook_url, data=param)
        res.raise_for_status()
        return res

    def fetch_events_files(self, events_files: list):
        files = []
        if len(events_files) > 0:
            for file in events_files:
                if "id" in file and "permalink_public" in file and "mimetype" in file:
                    # 画像以外のファイルは飛ばす
                    if file["mimetype"].find("image") == -1:
                        continue
                    print(file)
                    # まずファイルをpublic状態にする
                    res = post_json("{}{}".format(self._base_url, SHARE_PUBLIC_URL), {
                                    "token": self._oauth_token, "file": file["id"]})
                    res.raise_for_status()
                    res_dict = res.json()
                    print(res_dict)
                    # シェアされたファイルを取得する
                    res = requests.get(res_dict["file"]["permalink_public"])
                    res.raise_for_status()
                    files.append(res.content)
        return files

    def fetch_image_from_url(self, url):
        res = requests.get(url)
        res.raise_for_status()
        return res.content

    def add_emoji(self, name: str, file: bytes):
        res = post_emoji(self._workspace_name, self._session, name, file)
        res.raise_for_status()
        return res

    def remove_emoji(self, name: str):
        res = remove_emoji(self._workspace_name, self._session, name)
        res.raise_for_status()
        return res
