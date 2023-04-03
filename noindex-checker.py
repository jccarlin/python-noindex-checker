import http.server
import socketserver
import os

def check_noindex():
    # do something here

PORT = int(os.environ.get('PORT', 80))

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("Server started at localhost:" + str(PORT))
    httpd.serve_forever()
