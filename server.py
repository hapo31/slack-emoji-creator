from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import os
import json
import traceback

from emoji import check_login
from slack import Slack
from message_parser import CommandParser
from login import login, create_cookie_from_session, create_session_from_cookie

from db_service import PostgresService


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

    def _create_db_service(self):
        db_host = os.environ["DB_HOST"]
        db_name = os.environ["DB_NAME"]
        db_user = os.environ["DB_USER"]
        db_pass = os.environ["DB_PASSWORD"]

        db_service = PostgresService(db_host, db_name, db_user, db_pass)

        return db_service

    def _get_login_session(self, db_service):
        """
        取得済みセッションを取得する
        """
        user = os.environ["SESSION_USER"]
        session_str = db_service.get_login_session(user)

        if session_str:
            return create_session_from_cookie(session_str)
        else:
            return None

    def _set_login_session(self, db_service, cookie):
        """
        セッションを保存する
        """
        user = os.environ["SESSION_USER"]
        db_service.update_login_session(user, cookie)

    def _in_event_callback(self, response: dict):
        """
        event_callbackを受信したときの処理
        """
        event = response["event"]
        if event["type"] == "message":

            channel_id = os.environ["CHANNEL_ID"]
            bot_user_id = os.environ["BOT_USER_ID"]
            workspace_name = os.environ["WORKSPACE"]
            slack_hook_url = os.environ["SLACK_HOOK_URL"]
            oauth_token = os.environ["OAUTH_TOKEN"]
            email = os.environ["EMOJI_ADD_EMAIL"]
            password = os.environ["EMOJI_PASSWORD"]

            if "user" in event and "channel" in event:
                if event["user"] != bot_user_id and event["channel"] == channel_id:

                    command = CommandParser(event["text"])

                    if command.target == "emoji":
                        # DBからログインセッションを取得する
                        db_service = self._create_db_service()
                        session = self._get_login_session(db_service)

                        # ログインしているかチェック
                        if session is None or not check_login(workspace_name, session):
                            # ログインしていなかったらセッションを作成するためにログインする
                            session = login(workspace_name, email, password)
                            cookie_str = create_cookie_from_session(session)
                            user = os.environ["SESSION_USER"]

                            db_service.update_login_session(
                                user, cookie_str)

                        # コマンドっぽい文字列が投稿されたら処理をする
                        slack = Slack(workspace_name=workspace_name,
                                      session=session,
                                      hook_url=slack_hook_url, oauth_token=oauth_token)

                        if command.type == "create":
                            # emoji create emoji_name というチャットを付けて投稿すると絵文字が作成される
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
                                    emoji_name = command.args[2]
                                    res = slack.add_emoji(
                                        emoji_name, emoji_file)

                                    # ok: True なら成功
                                    if res.status_code == 200 and "ok" in res.json() and res.json()["ok"]:
                                        slack.post_message(
                                            "絵文字が作成されました :%s:" % emoji_name)
                                    else:
                                        slack.post_message("絵文字の作成に失敗しました…。")
                            except Exception as e:
                                # slack.post_message("エラーが発生しました・・・ %s" % e)
                                err = traceback.format_exc()
                                print(err)
                        elif command.type == "remove":
                            # 削除コマンド
                            try:
                                if len(command.args) >= 3:
                                    emoji_name = command.args[2]
                                    res = slack.remove_emoji(emoji_name)

                                    if res.status_code == 200 and "ok" in res.json() and res.json()["ok"]:
                                        slack.post_message(
                                            "絵文字が消去されました :%s:" % emoji_name)
                                    else:
                                        slack.post_message(
                                            "絵文字の削除に失敗しました…。 誤字または存在しない絵文字ではないですか?")

                            except Exception as e:
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
