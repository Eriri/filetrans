import socketserver
import socket
from sql import open_db, close_db
import time
import os
import threading


def run_ss(address, port, db_name):
    class req(socketserver.BaseRequestHandler):
        def handle(self):
            info = self.request.recv(1024).decode().split()
            db_con, db_cur = open_db(db_name)
            item = db_cur.execute("select * from user_info where id ='" +
                                  info[0]+"'").fetchall()
            if len(item) == 0:
                self.request.sendall("No such user".encode())
            elif item[0][2] != info[1]:
                print(item[0][2]+" "+info[1])
                self.request.sendall("Wrong password".encode())
            else:
                self.request.sendall("Succeed".encode())
                db_cur.execute("insert or replace into ip_info (ip,id,time) values ('" +
                               self.client_address[0]+"','" +
                               info[0]+"','" +
                               str(time.time())+"')")
            close_db(db_con, db_cur)
    ser = socketserver.ThreadingTCPServer((address, port), req)
    threading.Thread(target=ser.serve_forever).start()
    return ser


def run_cs(address, port, path):
    class req(socketserver.BaseRequestHandler):
        def handle(self):
            info = self.request.recv(1024).decode().split()
            data = {}
            lang = [".c", ".cpp"]
            for i in info:
                for s in lang:
                    if os.path.isfile(os.path.join(path, i+s)):
                        data[i +
                             s] = ''.join(open(os.path.join(path, i+s)).readlines())
            self.request.sendall(str(data).encode())
    ser = socketserver.ThreadingTCPServer((address, port), req)
    threading.Thread(target=ser.serve_forever).start()
    return ser


def log_in(address, port, user, password):
    ss = socket.socket()
    ss.settimeout(0.5)
    ss.connect((address, port))
    info = user + " " + password
    ss.sendall(info.encode())
    info = ss.recv(1024).decode()
    ss.close()
    return info


def collect_work(address, port, probs):
    ss = socket.socket()
    ss.settimeout(0.5)
    ss.connect((address, port))
    ss.sendall(probs.encode())
    info = eval(ss.recv(1024).decode())
    ss.close()
    return info


def collect_works(db_name, path, port):
    db_con, db_cur = open_db(db_name)
    probs = db_cur.execute("select id from problem_info").fetchall()
    probs = [x[0] for x in probs]
    items = db_cur.execute("select * from ip_info").fetchall()
    for item in items:
        if time.time() - item[2] <= 86400:
            info = collect_work(item[0], port, " ".join(probs))
            if os.path.isdir(os.path.join(path, item[1])) == False:
                os.mkdir(os.path.join(path, item[1]))
            for k, v in info.items():
                f = open(os.path.join(path, item[1], k), "w")
                f.write(v)
                f.close()
    close_db(db_con, db_cur)
