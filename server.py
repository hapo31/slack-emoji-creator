from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import os
import json
import traceback

from slack import Slack
from message_parser import CommandParser
from login import login

SLACK_URL = "https://{workspace}.slack.com"


def is_url(maybe_url):
    r = urlparse(maybe_url)
    return len(r) > 0


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):

        content_len = int(self.headers.get('content-length'))
        requestBody = json.loads(self.rfile.read(content_len).decode('utf-8'))

        res = {}
        if requestBody["type"] == "url_verification":
            # チャレンジレスポンスを返すためにそのままBodyを渡す
            res = requestBody

        # 自分自身の発言と#emoji-creatorチャンネル以外の発言は無視
        elif requestBody["type"] == "event_callback":
            self._in_event_callback(requestBody)

        res_str = json.dumps(res).encode("utf-8")
        self.send_response(200)
        self._set_content_length(res_str)
        self.end_headers()

        self.wfile.write(res_str)

    def do_GET(self):
        text = "Work!"

        self.send_response(200)
        self.send_header('Content-Length', len(text))
        self.end_headers()

        self.wfile.write(text.encode("utf-8"))

    def _set_content_length(self, text: str):
        self.send_header("Content-Length", len(text))

    def _in_event_callback(self, response: dict):
        """
        event_callbackを受信したときの処理
        """
        event = response["event"]
        if event["type"] == "message":

            channel_id = os.environ["CHANNEL_ID"]
            bot_user_id = os.environ["BOT_USER_ID"]
            workspace_name = os.environ["WORKSPACE"]
            slack_base_url = SLACK_URL.format(
                workspace=workspace_name)
            slack_hook_url = os.environ["SLACK_HOOK_URL"]
            oauth_token = os.environ["OAUTH_TOKEN"]
            email = os.environ["EMOJI_ADD_EMAIL"]
            password = os.environ["EMOJI_PASSWORD"]

            if "user" in event and "channel" in event:
                if event["user"] != bot_user_id and event["channel"] == channel_id:
                    slack = Slack(base_url=slack_base_url,
                                  hook_url=slack_hook_url, oauth_token=oauth_token)
                    # テストでオウム返し
                    # slack.post_message(response["event"]["text"])

                    command = CommandParser(event["text"])

                    if command.target == "emoji":
                        # emoji create emoji_name というチャットを付けて投稿すると絵文字が作成される
                        if command.type == "create":
                            try:
                                emoji_file = bytes()
                                file_fetch_success = False
                                # コマンド列が4つ以上の場合、4つ目をURLとして解釈する
                                if len(command.args) >= 4 and is_url(command.args[3][1:-1]):
                                    emoji_file = slack.fetch_image_from_url(
                                        command.args[3][1:-1])
                                    file_fetch_success = True
                                elif "files" in event:
                                    files = slack.fetch_events_files(
                                        event["files"])
                                    if len(files) > 0:
                                        file_fetch_success = True
                                if file_fetch_success:
                                    session, _ = login(
                                        workspace_name, email, password)
                                    emoji_name = command.args[2]
                                    res = slack.add_emoji(
                                        workspace_name, session, emoji_name, emoji_file)

                                    if res.status_code == 200:
                                        slack.post_message(
                                            "絵文字が作成されました :%s:" % emoji_name)
                            except Exception as e:
                                # slack.post_message("エラーが発生しました・・・ %s" % e)
                                err = traceback.format_exc()
                                print(err)


def run(server=HTTPServer, port=5000):
    address = ("", port)
    httpd = server(address, HttpHandler)
    httpd.serve_forever()


if __name__ == '__main__':
    port = int(os.environ["PORT"]) if os.environ["PORT"] is not None else 5000
    print("server start :{}".format(port))
    run(port=port)
