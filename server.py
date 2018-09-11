from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer


def run(server=HTTPServer, port=5000):
    address = ("", port)
    httpd = server(address, BaseHTTPRequestHandler)
    httpd.serve_forever()


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 2:
        port = int(sys.argv[1])
        run(port=port)
    else:
        run()
