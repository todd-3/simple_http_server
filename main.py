from http.server import BaseHTTPRequestHandler, HTTPServer
from json import loads as jloads
from urllib.parse import parse_qs as parser
from os import popen, system
from os.path import join

ip = popen("hostname -I").read()[:-2]  # gets device IP address
host:str = ""  # host name for server (if blank defaults to all available network interfaces)
port = 8080  # port to host server on

with open("main_page.html", "rb") as file:
    main_page = file.read()  # load in main_page.html as a byte object

with open("404_page.html", "rb") as file:
    not_found_page = file.read()  # load in 404_page.html as a byte object

with open("post_accepted.html", "rb") as file:
    accepted_page = file.read()

class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(main_page)  # send contents of main_page.html

        elif self.path == "/file_accepted":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(accepted_page)

        else:  # if request is not to {host}:{port}/ do not return a page
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(not_found_page)

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

            try:
                with open(join("server_writes", parse_contents["name"]), "w") as new_file:
                    print(f"Creating file {parse_contents['name']}")

                    file_body = parse_contents["body"]
                    if parse_contents["author"]:
                        file_body += "\n\nAuthored By: " + parse_contents["author"]

                    new_file.write(file_body)

                self.send_response(301)
                self.send_header("Location", "/file_accepted")
                self.end_headers()
            except Exception as e:
                print("Ran into Issue while creating file:", e)
                self.send_response(500)


        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(not_found_page)

if __name__ == "__main__":
    system("mkdir server_writes")

    webserver = HTTPServer((host, port), Server)
    print(f"{ip} IS USING PORT {port}")

    try:
        webserver.serve_forever()  # launch server
    except KeyboardInterrupt:
        print("Stopping server")
        webserver.server_close()