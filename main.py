from http.server import BaseHTTPRequestHandler, HTTPServer
from json import loads as jloads
from urllib.parse import parse_qs as parser
from os import popen

ip = popen("hostname -I").read()[:-2]  # gets device IP address
host:str = ""  # host name for server (if blank defaults to all available network interfaces)
port = 8080  # port to host server on

with open("index.html", "rb") as file:
    contents = file.read()  # load in index.html as a byte object

class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(contents)  # send contents of index.html
        else:  # if request is not to {host}:{port}/ do not return a page
            self.send_response(404)

    def do_POST(self):
        if self.path == "/submit":  # only accept requests to {host}:{port}/submit
            print(self.headers)

            length = int(self.headers["Content-Length"])
            contents = self.rfile.read(length).decode("utf8")  # read incoming contents and encode as utf8
            print(contents)

            if self.headers["Content-Type"] == "application/x-www-form-urlencoded":  # html form type
                # user urllib.parse.parse_qs to parse returned parameter string to json
                # parse_qs returns {key: [param]} convert to {key: param}
                parse_contents = {key: value[0] for key, value in parser(contents).items()}

            elif self.headers["Content-Type"] == "application/json":  # json type, cURL etc
                parse_contents = jloads(contents)  # load request contents as json

            else:  # return error if not allowed type
                self.send_response(400)
                return

            print(parse_contents)

            # redirect request to {host}:{port}/
            self.send_response(301)
            self.send_header("Location", "/")  # self.headers["Referer"])
            self.end_headers()
        else:
            self.send_response(404)

if __name__ == "__main__":
    webserver = HTTPServer((host, port), Server)
    print(f"{ip} IS USING PORT {port}")

    try:
        webserver.serve_forever()  # launch server
    except KeyboardInterrupt:
        print("Stopping server")
        webserver.server_close()