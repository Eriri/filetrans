import socketserver
import socket
from sql import *
import time
import os
import threading
import CD
import itertools
import multiprocessing


def run_ss(address, port, db_name):
    class req(socketserver.BaseRequestHandler):
        def handle(self):
            info = self.request.recv(1024).decode().split()
            db_con, db_cur = open_db(db_name)
            item = select_all_where(db_cur, "user_info", [
                                    "*"], ["id"], [info[0]])
            if len(item) == 0:
                self.request.sendall(CD._LOG_INFO_NO_USER_.encode())
            elif item[0][2] != info[1]:
                self.request.sendall(CD._LOG_INFO_WRONG_PWD_.encode())
            else:
                self.request.sendall(CD._LOG_INFO_SUCCEED_.encode())
                insert_or_replace(db_cur, "ip_info", ["ip", "id", "time"],
                                  [self.client_address[0], info[0], time.time()])
            close_db(db_con, db_cur)
    ss = socketserver.ThreadingTCPServer((address, port), req)
    threading.Thread(target=ss.serve_forever).start()
    return ss


def run_cs(address, port, path):
    class req(socketserver.BaseRequestHandler):
        def handle(self):
            info = self.request.recv(1024).decode().split()
            if info[0] == CD._CLIENT_ONLINE_CHECK_:
                self.request.sendall(CD._CLIENT_ONLINE_NOW_.encode())
                return
            data, lang = {}, CD._LANGUAGE_CONFIG_
            candidate = list(itertools.chain.from_iterable(
                [[x+y for y in lang] for x in info]))
            for fn in candidate:
                if os.path.isfile(os.path.join(path, fn)):
                    data[fn] = ''.join(
                        open(os.path.join(path, fn), "r").readlines())
            self.request.sendall(str(data).encode())
    cs = socketserver.ThreadingTCPServer((address, port), req)
    threading.Thread(target=cs.serve_forever).start()
    return cs


def log_in(address, port, user, password):
    ss = socket.socket()
    ss.settimeout(0.5)
    ss.connect((address, port))
    ss.sendall((user + " " + password).encode())
    info = ss.recv(1024).decode()
    ss.close()
    return info


def online_user(item, port):
    ss = socket.socket()
    ss.settimeout(0.5)
    try:
        ss.connect((item[0], port))
        ss.sendall(CD._CLIENT_ONLINE_CHECK_.encode())
        if ss.recv(1024).decode() != CD._CLIENT_ONLINE_NOW_:
            item = None
    except:
        item = None
    finally:
        ss.close()
    return item


def online_users(items, port):
    online_items = []
    pool = multiprocessing.Pool()
    for item in items:
        pool.apply_async(online_user, (item,),
                         callback=lambda item: online_items.append(item))
    pool.close(), pool.join()
    return [x for x in online_items if x != None]


def collect_work(address, port, probs):
    ss = socket.socket()
    ss.settimeout(0.5)
    try:
        ss.connect((address, port))
        ss.sendall(probs.encode())
        info = eval(ss.recv(1024).decode())
    except:
        info = CD._COLLECT_WORK_ERROR_
    finally:
        ss.close()
    return info


def collect_works(db_name, path, port):
    db_con, db_cur = open_db(db_name)
    probs = [x[0] for x in select_all(db_cur, "problem_info", ["id"])]
    items = online_users(select_all(db_cur, "ip_info", ["*"]), port)
    for item in items:
        info = collect_work(item[0], port, " ".join(probs))
        if info == CD._COLLECT_WORK_ERROR_:
            continue
        if os.path.isdir(os.path.join(path, item[1])) == False:
            os.mkdir(os.path.join(path, item[1]))
        for k, v in info.items():
            f = open(os.path.join(path, item[1], k), "w")
            f.write(v)
            f.close()
    close_db(db_con, db_cur)
