from http.server import BaseHTTPRequestHandler, HTTPServer
import SocketServer


class HttpHandler(BaseHTTPRequestHandler):
    def __init__(self):
        super.__init__()


def run(token, server=HTTPServer, port=5000):
    address = ("", port)
    httpd = server(address, BaseHTTPRequestHandler)
    httpd.serve_forever()


if __name__ == '__main__':

    import os

    port = int(os.environ["SERVE_PORT"])
    token = os.environ["HOOK_URL"]
    run(token=token, port=port)
