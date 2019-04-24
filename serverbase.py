from socket import socket,AF_INET,SOCK_DGRAM
from socketserver import BaseRequestHandler,ThreadingTCPServer,ThreadingUDPServer
from multiprocessing.dummy import Process
from sqlite3 import connect
from struct import pack,unpack
from sqlbase import select_one,update
from itertools import chain
from utilities import *


def run_server_tcp(app):
    class Handler(BaseRequestHandler):
        def handle(self):
            packet = eval(self.request.recv(unpack("Q",self.request.recv(8))[0]).decode())
            connection, nos = connect(app.database), []
            name = select_one(connection, "user", ["name"], ["no"], packet["no"])
            if name is None or name[0] != packet["name"]:
                self.request.sendall(pack("Q", len(CLIENT_KICK_OUT.encode())))
                self.request.sendall(CLIENT_KICK_OUT.encode())
            else:
                ip = select_one(connection, "user", ["ip"], ["no"], [packet["no"]])[0]
                if ip is not None and ip != self.client_address[0]:
                    Process(target=kick_out, args=(ip, app.client_port,)).start()
                no = select_one(connection, "user", ["no"], ["ip"], [self.client_address[0]])
                if no is not None and no[0] != packet["no"]:
                    update(connection, "user",["ip"],["NULL"],["no"],[no[0]]), nos.append(no[0])
                update(connection, "user", ["ip"], [self.client_address[0]], ["no"], [packet["no"]])
                nos.append(packet["no"])
                self.request.sendall(pack("Q",len(CLIENT_VERITY.encode())))
                self.request.sendall(CLIENT_VERITY.encode())
            connection.commit(), connection.close(), app.update(nos)
    server = ThreadingTCPServer((DEFAULT_LOCAL_ADDRESS, app.server_port), Handler)
    Process(target=server.serve_forever).start()
    return server


def run_client_tcp(app):
    class Handler(BaseRequestHandler):
        def handle(self):
            info = self.request.recv(unpack("Q", self.request.recv(8))[0]).decode()
            if info == CLIENT_KICK_OUT:
                app.kick_out()
            elif info == CLIENT_COLLECT_WORK:
                prob = eval(self.request.recv(unpack("Q", self.request.recv(8))[0]).decode())
                lang = eval(self.request.recv(unpack("Q", self.request.recv(8))[0]).decode())
                candi = list(chain.from_iterable([[no + su for su in lang] for no in prob]))
                for name in candi:
                    path = os.path.join(app.path, name)
                    if os.path.isfile(path):
                        f = open(path, "rb").read()
                        self.request.sendall(pack("Q", len(f)))
                        self.request.sendall(f)
                self.request.sendall(pack("Q",len(SEND_FILE_OVER.encode())))
                self.request.sendall(SEND_FILE_OVER.encode())
            elif info == CLIENT_RECV_FILE:
                while True:
                    name = self.request.recv(unpack("Q", self.request.recv(8))[0]).decode()
                    if name == RECV_FILE_OVER:
                        break
                    fs, rs = unpack("Q", self.request.recv(8))[0], 0
                    f = open(os.path.join(app.path, name), "wb")
                    while rs < fs:
                        data = self.request.recv(fs-rs)
                        rs += len(data)
                        f.write(data)
                    f.close()
    client = ThreadingTCPServer((DEFAULT_LOCAL_ADDRESS, app.client_port), Handler)
    Process(target=client.serve_forever).start()
    return client


def run_client_udp(app):
    class Handler(BaseRequestHandler):
        def handle(self):
            pass
    client = ThreadingUDPServer((DEFAULT_LOCAL_ADDRESS, app.udp_port),Handler)


def kick_out(address, port):
    s = socket()
    try:
        s.connect((address, port))
        s.sendall(pack("Q", len(CLIENT_KICK_OUT.encode())))
        s.sendall(CLIENT_KICK_OUT.encode())
    finally:
        s.close()


def broadcast_host(port):
    s = socket(AF_INET,SOCK_DGRAM)
    s.setsockopt()


def get_host(port):



def verity_packet(address, port, no, name):
    s, data = socket(), {"no": no, "name": name}
    try:
        s.connect((address, port))
        s.sendall(pack("Q", len(str(data).encode())))
        s.sendall(str(data).encode())
        info = s.recv(unpack("Q",s.recv(8))[0]).decode()
    except:
        info = LOG_INFO_SERVER_ERROR
    finally:
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
