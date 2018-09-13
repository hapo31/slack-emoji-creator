from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import json

from slack import Slack


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):

        content_len = int(self.headers.get('content-length'))
        requestBody = json.loads(self.rfile.read(content_len).decode('utf-8'))

        bot_user_id = os.environ["BOT_USER_ID"]
        channel_id = os.environ["CHANNEL_ID"]

        res = {}
        if requestBody["type"] == "url_verification":
            # チャレンジレスポンスを返すためにそのままBodyを渡す
            res = requestBody

        # 自分自身の発言と#emoji-creatorチャンネル以外の発言は無視
        elif requestBody["type"] == "event_callback" and requestBody["event"]["user"] != bot_user_id and requestBody["event"]["channel"] == channel_id:
            self._in_event_callback(requestBody)

        self.send_response(200)
        self._set_content_length(res)
        self.end_headers()

        self.wfile.write(json.dumps(res).encode("utf-8"))

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
        slack_url = os.environ["SLACK_HOOK_URL"]

        slack = Slack(slack_url)
        # テストでオウム返し
        slack.post_message(response["event"]["text"])


def run(server=HTTPServer, port=5000):
    address = ("", port)
    httpd = server(address, HttpHandler)
    httpd.serve_forever()


if __name__ == '__main__':
    port = int(os.environ["PORT"]) if os.environ["PORT"] is not None else 5000
    run(port=port)
