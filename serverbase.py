import socketserver
import socket
import time
import os
import threading
import itertools
import multiprocessing
import sqlite3
import struct
from sqlbase import *
from utilities import *
from _winapi import

def run_server(app):
    class Handler(socketserver.BaseRequestHandler):
        def handle(self):
            TYPE = self.request.recv(struct.unpack("Q",self.request.recv(8))[0]).decode()
            packet, connection, IDs = eval(self.request.recv(1024).decode()), sqlite3.connect(app.database), []
            NAME = SelectOne(connection, "USER", ["NAME"], ["ID"], packet["ID"])
            if TYPE == CLIENT_SEARCH_SERVER:
                self.request.sendall(app.server_address.encode())
            elif TYPE == CLIENT_LOG_IN:
                if NAME is None or NAME[0] != packet["NAME"]:
                    self.request.sendall(LOG_INFO_FAILED.encode())
                else:
                    IP = SelectOne(connection, "USER", ["IP"], ["ID"], [packet["ID"]])[0]
                    if IP is not None and IP != self.client_address[0]:
                        threading.Thread(target=kick_out, args=(IP, app.client_port,)).start()
                    ID = SelectOne(connection, "USER", ["ID"], ["IP"], [self.client_address[0]])
                    if ID is not None and ID[0] != packet["ID"]:
                        Update(connection, "USER",["IP", "TIME"],["NULL", "NULL"],["ID"],[ID[0]]), IDs.append(ID[0])
                    Update(connection, "USER", ["IP", "TIME"], [self.client_address[0], time.time()], ["ID"], [packet["ID"]])
                    IDs.append(packet["ID"]), self.request.sendall(LOG_INFO_SUCCEED.encode())
            elif TYPE == CLIENT_LOG_OUT:
                if NAME is not None and NAME[0] == packet["NAME"]:
                    Update(connection,["IP","TIME"],["NULL", "NULL"],["ID"],[packet["ID"]]), IDs.append(packet["ID"])
            elif TYPE == CLIENT_VERITY:
                if NAME is None or NAME[0] != packet["NAME"] or SelectOne(connection, "USER", ["IP"], ["ID"], [packet["ID"]])[0] != self.client_address[0]:
                    threading.Thread(target=kick_out, args=(self.client_address[0], app.client_port,)).start()
            connection.commit(), connection.close(), app.update(IDs)

    server = socketserver.ThreadingTCPServer((DEFAULT_LOCAL_ADDRESS, app.server_port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def run_client(app):
    class Handler(socketserver.BaseRequestHandler):
        def handle(self):
            TYPE = self.request.recv(struct.unpack("Q", self.request.recv(8))[0]).decode()
            if TYPE == CLIENT_SEARCH_SERVER:
                self.request.sendall(app.server_address.encode())
            elif TYPE == CLIENT_ONLINE_CHECK:
                self.request.sendall(CLIENT_ONLINE_NOW.encode())
            elif TYPE == CLIENT_OFFLINE:
                app.log_out()
            elif TYPE == CLIENT_COLLECT_WORK:
                prob = eval(self.request.recv(struct.unpack("Q", self.request.recv(8))[0]).decode())
                lang = eval(self.request.recv(struct.unpack("Q", self.request.recv(8))[0]).decode())
                candidate = list(itertools.chain.from_iterable([[ID + suffix for suffix in lang] for ID in prob]))
                for filename in candidate:
                    filepath = os.path.join(app.path, filename)
                    if os.path.isfile(filepath):
                        f = open(filepath, "rb").read()
                        self.request.sendall(struct.pack("Q", len(f)))
                        self.request.sendall(f)
                self.request.sendall(struct.pack("Q",len(SEND_FILE_OVER.encode())))
                self.request.sendall(SEND_FILE_OVER.encode())
            elif TYPE == CLIENT_RECV_FILE:
                while True:
                    filename = self.request.recv(struct.unpack("Q", self.request.recv(8))[0]).decode()
                    if filename == RECV_FILE_OVER:
                        break
                    fs, rs = struct.unpack("Q", self.request.recv(8))[0], 0
                    f = open(os.path.join(app.path, filename), "wb")
                    while rs < fs:
                        data = self.request.recv(fs-rs)
                        rs += len(data)
                        f.write(data)
                    f.close()

    client = socketserver.ThreadingTCPServer((DEFAULT_LOCAL_ADDRESS, app.client_port), Handler)
    threading.Thread(target=client.serve_forever, daemon=True).start()
    return client


def kick_out(address, port):
    s = socket.socket()
    s.connect((address, port))
    s.send(struct.pack("Q", len(CLIENT_OFFLINE.encode())))
    s.sendall(CLIENT_OFFLINE.encode())
    s.close()

def search_server():
    ip = socket.gethostbyname(socket.getfqdn())


def Log_In(address, port, ID, NAME):
    s, data, info = socket.socket(), {"ID": ID, "NAME": NAME}, LOG_INFO_FAILED
    try:
        s.connect((address, port))
        s.send(struct.pack("Q", len(str(data).encode())))
        s.sendall(str(data).encode())
        info = s.recv(1024).decode()
    except:
        info = LOG_INFO_SERVER_ERROR
    finally:
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
