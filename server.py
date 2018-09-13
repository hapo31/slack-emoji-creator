from http.server import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import os


class HttpHandler(BaseHTTPRequestHandler):
    def __init__(self):
        super.__init__(self)
        self._slack_hook_url = os.environ["SLACK_HOOK_URL"]

    def do_POST(self):
        self.send_response(200)
        text = "Work!"
        self.send_header('Content-Length', len(text))
        self.wfile.write(text.encode("utf-8"))

    def do_GET(self):
        self.send_response(200)
        text = "Work!"
        self.send_header('Content-Length', len(text))
        self.wfile.write(text.encode("utf-8"))


def run(server=HTTPServer, port=5000):
    address = ("", port)
    httpd = server(address, HttpHandler)
    httpd.serve_forever()


if __name__ == '__main__':
    port = int(os.environ["SERVE_PORT"])
    run(port=port)
