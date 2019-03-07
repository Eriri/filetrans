import socketserver
import pandas
import random
import string
from socketserver import *
user_info = {}
problem_info = set()
conf_path = "conf"


def load_conf():
    try:
        f = open(conf_path, "r")
    except FileNotFoundError:
        return
    global user_info
    global problem_info
    conf = eval(f.read())
    user_info = conf["user_info"]
    problem_info = conf["problem_info"]
    f.close()


def save_conf():
    f = open(conf_path, "w")
    f.write(str({"user_info": user_info, "problem_info": problem_info}))
    f.close()


def gen_pwd():
    return ''.join(random.sample(
        string.ascii_letters + string.digits, 8))


class requst_(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024)
        print(data)
        data = "fuck u"
        data = data.encode()
        self.request.send(data)


server_ = socketserver.ThreadingTCPServer(('127.0.0.1', 8080), requst_)
server_.serve_forever()
