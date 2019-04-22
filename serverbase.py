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


def Run_Server(address, server_port, client_port, database):
    class Handler(socketserver.BaseRequestHandler):
        def handle(self):
            type_len = struct.unpack("Q",self.request.recv(8))[0]
            type_data = self.request.recv(type_len).decode()
            if type_data == CLIENT_VERITY:
                pass
            if type_data == CLIENT_LOG_IN:
                packet = eval(self.request.recv(1024).decode())
                connection, data = sqlite3.connect(database), LOG_INFO_FAILED
                try:
                    assert SelectOne(connection, "USER", ["NAME"], ["ID"], [packet["ID"]])[0] == packet["NAME"]
                    ip = SelectOne(connection,"IP",["IP"],["ID"],[packet["ID"]])
                    if ip is not None and ip != self.client_address[0]:
                        threading.Thread(target=Log_Out,args=(ip,client_port,)).start()
                    Insert(connection, "IP", ["IP", "ID", "NAME", "TIME"], [self.client_address[0], packet["ID"], packet["NAME"], time.time()])
                    connection.execute("update USER set TIME = "+str(time.time())+" where ID = "+packet["ID"])
                    data = LOG_INFO_SUCCEED
                finally:
                    connection.commit(), connection.close(), self.request.sendall(data.encode())
    server = socketserver.ThreadingTCPServer((address, server_port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def run_client(app, address, port, path):
    class Handler(socketserver.BaseRequestHandler):
        def handle(self):
            info_len = struct.unpack("Q",self.request.recv(8))[0]
            info_data = self.request.recv(info_len).decode()
            if info_data == CLIENT_ONLINE_CHECK:
                id_len = struct.unpack("Q",self.request.recv(8))[0]
                id_data = self.request.recv(id_len).decode()
                self.request.sendall(CLIENT_ONLINE_NOW.encode())
            if info_data == CLIENT_OFFLINE:
                print(str(app))
            if info_data == CLIENT_COLLECT_WORK:
                prob_conf_len = struct.unpack("Q",self.request.recv(8))[0]
                prob_conf_data = eval(self.request.recv(prob_conf_len).decode())
                lang_conf_len = struct.unpack("Q",self.request.recv(8))[0]
                lang_conf_data = eval(self.request.recv(lang_conf_len).decode())
                data, candidate = {}, list(itertools.chain.from_iterable(
                    [[ID + suffix for suffix in lang_conf_data] for ID in prob_conf_data]))
                for filename in candidate:
                    filepath = os.path.join(path, filename)
                    if os.path.isfile(filepath):
                        f = open(filepath,"rb").read()
                        self.request.send(struct.pack("Q",len(f)))
                        self.request.sendall(f)
            if info_data == CLIENT_RECV_FILE:
                while True:
                    filename_len = struct.unpack("Q",self.request.recv(8))[0]
                    filename_data = self.request.recv(filename_len).decode()
                    if filename_data == RECV_FILE_OVER:
                        break
                    fs, rs = struct.unpack("Q",self.request.recv(8))[0], 0
                    f = open(os.path.join(path,filename_data),"wb")
                    while rs < fs:
                        data = self.request.recv(fs-rs)
                        rs += len(data)
                        f.write(data)
                    f.close()
    client = socketserver.ThreadingTCPServer((address, port), Handler)
    threading.Thread(target=client.serve_forever, daemon=True).start()
    return client


def Log_Out(address, port):
    s = socket.socket()
    s.connect((address,port))
    s.send(struct.pack("Q",len(CLIENT_OFFLINE.encode())))
    s.sendall(CLIENT_OFFLINE.encode())
    s.close()


def Log_In(address, port, ID, NAME):
    s, data, info = socket.socket(), {"ID": ID, "NAME": NAME}, LOG_INFO_FAILED
    try:
        s.connect((address, port))
        s.send(struct.pack("Q",len(str(data).encode())))
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
