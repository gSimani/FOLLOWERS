import http.server
import socketserver
import os

PORT = 8000

# Change directory to where the index.html is located
os.chdir('hello-world-app/hello-world-webpage')

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    print(f"Open http://localhost:{PORT} in your browser")
    httpd.serve_forever() 