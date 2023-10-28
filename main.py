from http.server import BaseHTTPRequestHandler, HTTPServer
from json import loads as jloads
from urllib.parse import parse_qs as parser
from os import popen

ip = popen("hostname -I").read()[:-2]
host:str = ""
port = 8080

with open("index.html", "rb") as file:
    contents = file.read()

class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":  # or self.path == "/submit":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(contents)
        else:
            self.send_response(404)

    def do_POST(self):
        if self.path == "/submit":
            print(self.headers)

            length = int(self.headers["Content-Length"])
            contents = self.rfile.read(length).decode("utf8")
            print(contents)

            if self.headers["Content-Type"] == "application/x-www-form-urlencoded":
                parse_contents = {key: value[0] for key, value in parser(contents).items()}
            elif self.headers["Content-Type"] == "application/json":
                parse_contents = jloads(contents)
            else:
                self.send_response(400)
                return

            print(parse_contents)

            self.send_response(301)
            self.send_header("Location", "/")  # self.headers["Referer"])
            self.end_headers()
        else:
            self.send_response(404)

if __name__ == "__main__":
    webserver = HTTPServer((host, port), Server)
    print(f"{ip} IS USING PORT {port}")

    try:
        webserver.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server")
        webserver.server_close()