from socket import socket, AF_INET, SOCK_DGRAM, IPPROTO_UDP, SOL_SOCKET, SO_BROADCAST, SO_REUSEADDR
from socketserver import BaseRequestHandler, ThreadingTCPServer, ThreadingUDPServer
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from apscheduler.schedulers.blocking import BlockingScheduler
from multiprocessing.dummy import Process, Pool
from sqlite3 import connect
from struct import pack, unpack
from sqlbase import select, select_one, update
from itertools import chain
from utilities import *


def run_server_tcp(app):
    class Handler(BaseRequestHandler):
        def handle(self):
            packet, connection, nos = quick_recv(self.request), connect(app.database), []
            name = select_one(connection, "user", ["name"], ["no"], packet["no"])
            if name is None or name[0] != packet["name"]:
                quick_send(self.request, [CLIENT_KICK_OUT])
            else:
                ip = select_one(connection, "user", ["ip"], ["no"], [packet["no"]])[0]
                if ip is not None and ip != self.client_address[0]:
                    Process(target=kick_out, args=(ip, app.client_port,)).start()
                no = select_one(connection, "user", ["no"], ["ip"], [self.client_address[0]])
                if no is not None and no[0] != packet["no"]:
                    update(connection, "user", ["ip"], ["NULL"], ["no"], [no[0]]), nos.append(no[0])
                update(connection, "user", ["ip"], [self.client_address[0]], ["no"], [packet["no"]])
                nos.append(packet["no"]), quick_send(self.request, [CLIENT_VERITY])
            connection.commit(), connection.close(), app.update(nos)

    try:
        server = ThreadingTCPServer(('', app.server_tcp_port), Handler)
        p = Process(target=server.serve_forever)
        p.setDaemon(True), p.start()
        return server
    except Exception as e:
        print(e)


def run_server_udp(app):
    try:
        s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        bs = BlockingScheduler()
        bs.add_job(func=s.sendto, args=("it's me".encode(), ('<broadcast>', app.udp_port),), trigger='interval', seconds=10)
        p = Process(target=bs.start)
        p.setDaemon(True), p.start()
        return bs
    except Exception as e:
        print(e)


def run_server_ftp(app):
    try:
        authorizer, handler = DummyAuthorizer(), FTPHandler
        authorizer.add_anonymous(app.ftp_path)
        handler.authorizer = authorizer
        server = FTPServer((DEFAULT_LOCAL_ADDRESS, app.ftp_port), handler)
        p = Process(target=server.serve_forever)
        p.setDaemon(True), p.start()
        return server
    except Exception as e:
        print(e)


def run_client_tcp(app):
    class Handler(BaseRequestHandler):
        def handle(self):
            info = quick_recv(self.request)
            if info == CLIENT_KICK_OUT:
                app.kick_out()
            elif info == CLIENT_COLLECT_WORK:
                prob, lang = eval(quick_recv(self.request)), eval(quick_recv(self.request))
                cand = list(chain.from_iterable([[no + su for su in lang] for no in prob]))
                for name in cand:
                    with open(os.path.join(app.path, name), "rb").read() as f:
                        quick_send(self.request, [SEND_FILE_NOW, name, f])
                quick_send(self.request, [SEND_FILE_OVER])
            elif info == CLIENT_RECV_FILE:
                quick_recv_file(self.request, app.path)

    try:
        client = ThreadingTCPServer(('', app.client_tcp_port), Handler)
        p = Process(target=client.serve_forever)
        p.setDaemon(True), p.start()
        return client
    except Exception as e:
        print(e)


def run_client_udp(app):
    class Handler(BaseRequestHandler):
        def handle(self):
            app.server_address = self.client_address[0]

    try:
        client = ThreadingUDPServer(('', app.udp_port), Handler)
        p = Process(target=client.serve_forever)
        p.setDaemon(True), p.start()
        return client
    except Exception as e:
        print(e)


def kick_out(address, port):
    try:
        with socket() as s:
            s.connect((address, port)), quick_send(s, [CLIENT_KICK_OUT])
    except Exception as e:
        print(e)


def verity_packet(app):
    packet, info = {"no": app.no, "name": app.name}, CLIENT_KICK_OUT
    try:
        with socket() as s:
            s.connect((app.server_address, app.server_tcp_port))
            quick_send(s, [packet])
            info = quick_recv(s)
    except Exception as e:
        print(str(e))
    return info


def collect_work(address, port, path, no, prob, lang):
    if address is None or address == "":
        return no, COLLECT_WORK_FAILED, []
    try:
        with socket() as s:
            s.connect((address, port))
            quick_send(s, [CLIENT_COLLECT_WORK, prob, lang])
            info, count = quick_recv_file(s, os.path.join(path, no))
            return no, [COLLECT_WORK_ERROR, COLLECT_WORK_SUCCEED][info == RECV_FILE_SUCCEED], count
    except Exception as e:
        print(str(e))
        return no, COLLECT_WORK_FAILED, []


def collect_works(app, dialog):
    try:
        connection, pool = connect(app.database), Pool()
        user = select(connection, "user", ["no", "ip"])
        connection.close(), dialog.G.SetRange(len(user)), dialog.G.SetValue(0)
        for no, ip in user:
            pool.apply_async(func=collect_work,
                             args=(ip, app.client_tcp_port, app.work_dir, no, app.prob, app.lang,),
                             callback=lambda ic: dialog.update(ic[0], ic[1], ic[2]))
        pool.close()
    except Exception as e:
        print(e)


def send_file(address, port, path, no):
    if address is None or address == "":
        return no, SEND_FILE_FAILED, []
    count = []
    try:
        with socket() as s:
            s.connect((address, port))
            quick_send(s, CLIENT_RECV_FILE)
            for p in path:
                with open(p, "rb").read() as f:
                    quick_send(s, [SEND_FILE_NOW, os.path.basename(p), f])
                    count.append(os.path.basename(p))
            quick_send(s, [SEND_FILE_OVER])
            return no, SEND_FILE_SUCCEED, count
    except Exception as e:
        print(e)
        return no, SEND_FILE_ERROR, count


def send_files(app, dialog):
    try:
        connection, pool = connect(app.database), Pool()
        user = select(connection, "user", ["no", "ip"])
        connection.close(), dialog.G.SetRange(len(user)), dialog.G.SetValue(0)
        path = [x.path for x in dialog.F.GetObjects()]
        for no, ip in user:
            pool.apply_async(func=send_file,
                             args=(ip, app.client_tcp_port, path, no),
                             callback=lambda ic: dialog.update(ic[0], ic[1], ic[2]))
        pool.close()
    except Exception as e:
        print(e)


def quick_send(s, d):
    try:
        for i in d:
            i = str(i).encode()
            s.sendall(pack("Q", len(i))), s.sendall(i)
    except Exception as e:
        print(e)


def quick_recv(s):
    return s.recv(unpack("Q", s.recv(8))[0]).decode()


def quick_recv_file(s, p):
    count = []
    try:
        if not os.path.isdir(p):
            os.mkdir(p)
        while quick_recv(s) != SEND_FILE_OVER:
            name, fs, rs = quick_recv(s), unpack("Q", s.recv(8))[0], 0
            with open(os.path.join(p, name), "wb") as f:
                data = s.recv(fs - rs)
                rs += len(data)
                f.write(data)
            count.append(name)
        return RECV_FILE_SUCCEED, count
    except Exception as e:
        print(e)
        return RECV_FILE_FAILED, count
