import socketserver
import socket
import time
import os
import threading
import itertools
import multiprocessing
import sqlite3
from sqlbase import *
from utilities import *


def Run_Server(address, port, database):
    class request(socketserver.BaseRequestHandler):
        def handle(self):
            packet = eval(self.request.recv(1024).decode())
            connection, data = sqlite3.connect(database), LOG_INFO_FAILED
            try:
                assert Select(connection, "USER", "PASSWORD", ["ID"], [packet["ID"]])[0] == packet["PASSWORD"]
                Insert(connection, "IP", ["IP", "ID", "TIME"], [self.client_address[0], packet["ID"], time.time()])
                connection.execute("update USER set TIME = "+str(time.time())+" where ID = "+packet["ID"])
                data = LOG_INFO_SUCCEED
            finally:
                connection.commit(), connection.close(), self.request.sendall(data.encode())
    server = socketserver.ThreadingTCPServer((address, port), request)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def Run_Client(address, port, path):
    class request(socketserver.BaseRequestHandler):
        def handle(self):
            packet = eval(self.request.recv(1024).decode())
            if packet["TYPE"] == CLIENT_ONLINE_CHECK:
                self.request.sendall(CLIENT_ONLINE_NOW.encode())
            if packet["TYPE"] == CLIENT_COLLECT_WORK:
                data, candidate = {}, list(itertools.chain.from_iterable(
                    [[ID + suffix for suffix in LANGUAGE_CONFIG] for ID in packet["PROBLEM"]]))
                for filename in candidate:
                    filepath = os.path.join(path, filename)
                    if os.path.isfile(filepath):
                        data[filename] = ''.join(open(filepath, "r").readlines())
                self.request.sendall(str(data).encode())
    client = socketserver.ThreadingTCPServer((address, port), request)
    threading.Thread(target=client.serve_forever, daemon=True).start()
    return client


def Log_In(address, port, ID, PASSWORD):
    s, data = socket.socket(), {"ID": ID, "PASSWORD": PASSWORD}
    try:
        s.connect((address, port)), s.sendall(str(data).encode())
        info = s.recv(1024).decode()
    except:
        info = LOG_INFO_SERVER_ERROR
    s.close()
    return info


def Online_Check(address, port, ID):
    s, data = socket.socket(), {"TYPE": CLIENT_ONLINE_CHECK}
    s.settimeout(0.5)
    try:
        s.connect((address, port))
        s.sendall(str(data).encode())
        assert s.recv(1024).decode() == CLIENT_ONLINE_NOW
        info = ID, address
    except:
        info = CLIENT_OFFLINE
    s.close()
    return info


def Online_User(database, port):
    connection, pool, user = sqlite3.connect(database), multiprocessing.Pool(), []
    for address, ID in Select(connection, "IP", ["IP", "ID"]):
        pool.apply_async(Online_Check, (address, port, ID), callback=lambda x: user.append(x))
    pool.close(), pool.join(), connection.close()
    return [x for x in user if x != CLIENT_OFFLINE]


def User_Work(address, port, ID, PROBLEM):
    s, data = socket.socket(), {"TYPE": CLIENT_COLLECT_WORK, "PROBLEM": PROBLEM}
    try:
        s.connect((address, port))
        s.sendall(str(data).encode())

        info = ID, eval(s.recv(1024).decode())

    except:
        info = COLLECT_WORK_ERROR
    s.close()
    return info


def Collect_Work(database, path, port):
    user, pool, connection = Online_User(database, port), multiprocessing.Pool(), sqlite3.connect(database)
    PROBLEM, work = [x[0] for x in Select(connection, "PROBLEM", ["ID"])], []
    for ID, address in user:
        pool.apply_async(User_Work, (address, port, ID, PROBLEM), callback=lambda x: work.append(x))
    connection.close(), pool.close(), pool.join()
    work = [x for x in work if x != COLLECT_WORK_ERROR]
    for ID, data in work:
        if not os.path.isdir(os.path.join(path, ID)):
            os.mkdir(os.path.join(path, DEFAULT_WORK_DIR, ID))
        for k, v in data.items():
            f = open(os.path.join(path, ID, k), "w")
            f.write(v), f.close()


def User_File(address, port, file):
    s, data = socket.socket(), {"TYPE": CLIENT_SEND_FILE}


def Send_File(database, file, port):
    pass
