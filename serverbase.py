from socket import socket, AF_INET, SOCK_DGRAM, IPPROTO_UDP, SOL_SOCKET, SO_BROADCAST, SO_REUSEADDR
from socketserver import BaseRequestHandler, ThreadingTCPServer, ThreadingUDPServer
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from multiprocessing.dummy import Process, Pool
from struct import pack, unpack
from itertools import chain

from sqlbase import *
from utilities import *


def run_server_tcp(app):
    class Handler(BaseRequestHandler):
        def handle(self):
            packet, connection, nos = quick_recv(self.request), connect(app.database), []
            name = select_one(connection, "user", ["name"], ["no"], packet["no"])
            if name is None or name[0] != packet["name"]:
                quick_send(self.request, [CLIENT_KICK_OUT, app.prob])
            else:
                ip = select_one(connection, "user", ["ip"], ["no"], [packet["no"]])[0]
                if ip is not None and ip != self.client_address[0]:
                    Process(target=kick_out, args=(ip, app.client_port,)).start()
                no = select_one(connection, "user", ["no"], ["ip"], [self.client_address[0]])
                if no is not None and no[0] != packet["no"]:
                    update(connection, "user", ["ip"], ["NULL"], ["no"], [no[0]]), nos.append(no[0])
                update(connection, "user", ["ip"], [self.client_address[0]], ["no"], [packet["no"]])
                nos.append(packet["no"]), quick_send(self.request, [CLIENT_VERITY, app.prob])
            connection.commit(), connection.close(), app.update(nos)

    try:
        server = ThreadingTCPServer(('', app.server_tcp_port), Handler)
        p = Process(target=server.serve_forever)
        p.setDaemon(True), p.start()
        return server
    except Exception as e:
        MessageBox(str(e))


def run_server_udp(app):
    try:
        s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        bs = BackgroundScheduler()
        bs.add_job(func=s.sendto, args=("it's me".encode(), ('<broadcast>', app.udp_port),), trigger=IntervalTrigger(seconds=7))
        bs.start()
        return bs
    except Exception as e:
        MessageBox(str(e))


def run_server_ftp(app):
    try:
        authorizer, handler = DummyAuthorizer(), FTPHandler
        authorizer.add_anonymous(app.ftp_path)
        handler.authorizer = authorizer
        server = FTPServer(('0.0.0.0', app.ftp_port), handler)
        p = Process(target=server.serve_forever)
        p.setDaemon(True), p.start()
        return server
    except Exception as e:
        MessageBox(str(e))
        


def run_client_tcp(app):
    class Handler(BaseRequestHandler):
        def handle(self):
            info = quick_recv(self.request)
            if info == CLIENT_KICK_OUT:
                app.close("已被服务器踢出")
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
        MessageBox(str(e))


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
        MessageBox(str(e))

def run_client_verity(app):
    try:
        bs = BackgroundScheduler()
        bs.add_job(func=verity_packet,args=(app,), trigger=IntervalTrigger(seconds=7))
        bs.start()
        return bs
    except Exception as e:
        MessageBox(str(e))

def kick_out(address, port):
    try:
        with socket() as s:
            s.connect((address, port)), quick_send(s, [CLIENT_KICK_OUT])
    except Exception as e:
        pass


def verity_packet(app):
    try:
        if app.server_address is None:
            raise Exception("No address")
        with socket() as s:
            s.connect((app.server_address, app.server_tcp_port))
            quick_send(s, [CLIENT_VERITY, {"no": app.no, "name": app.name}])
            info, prob = quick_recv(s), eval(quick_recv(s))
        if info == CLIENT_VERITY_SUCCEED:
            app.fresh_prob(prob)
        elif info == CLIENT_VERITY_FAILED:
            app.close()
        app.fresh_verity_info(info, str(app.server_address))
    except Exception as e:
        info = CLIENT_VERITY_FAILED
        app.fresh_verity_info(CLIENT_SEARCH_SERVER, str(e)) 
    return info


def collect_work(address, port, path, no, prob, lang):
    count = []
    if address is None:
        raise Exception("No address")
    try:
        with socket() as s:
            s.connect((address, port))
            quick_send(s, [CLIENT_COLLECT_WORK, prob, lang])
            info, count, error = quick_recv_file(s, os.path.join(path, no))
            return no, count, [COLLECT_WORK_FAILED, COLLECT_WORK_SUCCEED][info == RECV_FILE_SUCCEED], error
    except Exception as e:
        print(str(e))
        return no, COLLECT_WORK_FAILED, count, 


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
        MessageBox(str(e))


def send_file(address, port, path, no):
    count = []
    try:
        with socket() as s:
            s.connect((address, port))
            quick_send(s, [CLIENT_RECV_FILE])
            for p in path:
                with open(p, "rb").read() as f:
                    quick_send(s, [SEND_FILE_NOW, os.path.basename(p), f])
                    count.append(os.path.basename(p))
            quick_send(s, [SEND_FILE_OVER])
        return no, count, SEND_FILE_SUCCEED, NO_ERROR, 
    except Exception as e:
        return no, count, SEND_FILE_FAILED, str(e)


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
        MessageBox(str(e))


def quick_send(s, d):
    for i in d:
        i = str(i).encode()
        s.sendall(pack("Q", len(i))), s.sendall(i)


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
        return RECV_FILE_SUCCEED, count, NO_ERROR
    except Exception as e:
        return RECV_FILE_FAILED, count, str(e)
