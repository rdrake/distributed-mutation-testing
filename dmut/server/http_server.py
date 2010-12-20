from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

httpd = TCPServer(("", 8001), SimpleHTTPRequestHandler)
httpd.serve_forever()
