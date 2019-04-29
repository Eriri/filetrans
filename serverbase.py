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
            info = quick_recv(self.request)
            if info == CLIENT_ONLINE_CHECK:
                quick_send(self.request, [app.prob, app.lang])
            elif info == CLIENT_VERITY:
                packet, connection = eval(quick_recv(self.request)), connect(app.database)
                name = select_one(connection, "user", ["name"], ["no"], [packet["no"]])
                if name is None or name[0] != packet["name"]:
                    quick_send(self.request, [CLIENT_VERITY_FAILED]), connection.close()
                else:
                    ip = select_one(connection, "user", ["ip"], ["no"], [packet["no"]])[0]
                    if ip is not None and ip != self.client_address[0]:
                        Process(target=kick_out, args=(ip, app.client_tcp_port,)).start()
                    update(connection, "user", ["ip"], [self.client_address[0]], ["no"], [packet["no"]])
                    connection.commit(), connection.close(), app.update([packet["no"]])
                    quick_send(self.request, [CLIENT_VERITY_SUCCEED])


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
        bs.add_job(func=s.sendto, args=("it's me".encode(), ('<broadcast>', app.udp_port),), trigger=IntervalTrigger(seconds=3))
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
            print(info)
            if info == CLIENT_KICK_OUT:
                app.status = PROJECT_STATUS_OFF
            elif info == CLIENT_COLLECT_WORK:
                no, prob, lang = quick_recv(self.request), eval(quick_recv(self.request)), eval(quick_recv(self.request))
                if app.no != no:
                    quick_send(self.request, [CLIENT_VERITY_FAILED])
                    return
                quick_send(self.request, [CLIENT_VERITY_SUCCEED])
                cand = list(chain.from_iterable([[no + su for su in lang] for no in prob]))
                for name in cand:
                    if os.path.isfile(os.path.join(app.path, name)):
                        with open(os.path.join(app.path, name), "rb") as f:
                            quick_send(self.request, [SEND_FILE_NOW, name])
                            data = f.read()
                            self.request.sendall(pack("Q", len(data)))
                            self.request.sendall(data)
                quick_send(self.request, [SEND_FILE_OVER])
                app.show_info("已成功发送作业", quick_recv(self.request))
            elif info == CLIENT_RECV_FILE:
                no = quick_recv(self.request)
                if app.no != no:
                    quick_send(self.request, [CLIENT_VERITY_FAILED])
                    return
                quick_send(self.request, [CLIENT_VERITY_SUCCEED])
                info, count, error = quick_recv_file(self.request, app.path)
                if info == RECV_FILE_SUCCEED:
                    app.show_info("已成功接收文件", count)
                else:
                    app.show_info("接收文件发生错误，已接收", count, error)

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
            app.fresh_server_info(CLIENT_DISCOVER_SERVER)

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
        bs.add_job(func=verity_server, args=(app,), trigger=IntervalTrigger(seconds=3))
        bs.add_job(func=verity_client, args=(app,), trigger=IntervalTrigger(seconds=3))
        bs.start()
        return bs
    except Exception as e:
        MessageBox(str(e))


def kick_out(address, port):
    try:
        s = socket()
        s.settimeout(1.5), s.connect((address, port))
        quick_send(s, [CLIENT_KICK_OUT])
    except Exception as e:
        print(str(e))
    finally:
        s.close()

def verity_server(app):
    try:
        s = socket()
        s.settimeout(1.5), s.connect((app.server_address, app.server_tcp_port))
        quick_send(s, [CLIENT_ONLINE_CHECK])
        app.fresh_prob_lang(eval(quick_recv(s)), eval(quick_recv(s)))
        info = CLIENT_DISCOVER_SERVER
    except Exception as e:
        print(str(e))
        info = CLIENT_SEARCH_SERVER
    finally:
        s.close()
    app.fresh_server_info(info)

def verity_client(app):
    if app.tcp_server is not None and app.status == PROJECT_STATUS_OFF:
        app.close("已被服务器踢出")

def verity_user(app):
    try:
        s = socket()
        s.settimeout(1.5), s.connect((app.server_address, app.server_tcp_port))
        quick_send(s, [CLIENT_VERITY,{"no":app.no, "name":app.name}])
        info = quick_recv(s)
    except Exception as e:
        print(str(e))
        info = CLIENT_SEARCH_SERVER
    finally:
        s.close()
    return info


def collect_work(address, port, path, no, prob, lang):
    count = []
    try:
        s = socket()
        s.connect((address, port))
        quick_send(s, [CLIENT_COLLECT_WORK, no, prob, lang])
        if quick_recv(s) != CLIENT_VERITY_SUCCEED:
            raise Exception("wrong user")
        info, count, error = quick_recv_file(s, os.path.join(path, no))
        quick_send(s, [count])
    except Exception as e:
        error = e
        print(str(e))
        s.close()
    finally:
        s.close()
    return no, count, [COLLECT_WORK_FAILED, COLLECT_WORK_SUCCEED][info == RECV_FILE_SUCCEED], str(error)


def collect_works(app, dialog, aop):
    try:
        pool = Pool()
        objs = [dialog.OLV.GetObjects(), dialog.OLV.GetCheckedObjects()][aop]
        user = [(obj.no, obj.ip) for obj in objs]
        dialog.G.SetRange(len(user)), dialog.G.SetValue(0)
        for no, ip in user:
            pool.apply_async(func=collect_work,
                             args=(ip, app.client_tcp_port, app.work_dir, no, app.prob, app.lang,),
                             callback=lambda ic: dialog.update(ic[0], ic[1], ic[2], ic[3]))
        pool.close()
    except Exception as e:
        MessageBox(str(e))


def send_file(address, port, path, no):
    count, info, error = [], SEND_FILE_SUCCEED, NO_ERROR
    try:
        s = socket()
        s.connect((address, port))
        quick_send(s, [CLIENT_RECV_FILE, no])
        if quick_recv(s) != CLIENT_VERITY_SUCCEED:
            raise Exception("wrong user")
        for p in path:
            with open(p, "rb") as f:
                data = f.read()
                quick_send(s, [SEND_FILE_NOW, os.path.basename(p)])
                s.sendall(pack("Q", len(data))), s.sendall(data)
                count.append(os.path.basename(p))
        quick_send(s, [SEND_FILE_OVER])
    except Exception as e:
        info, error = SEND_FILE_FAILED, e
    finally:
        s.close()
    return no, count, info, str(error)


def send_files(app, dialog, aop):
    try:
        pool = Pool()
        objs = [dialog.U.GetObjects(), dialog.U.GetCheckedObjects()][aop - 2]
        user = [(obj.no, obj.ip) for obj in objs]
        dialog.G.SetRange(len(user)), dialog.G.SetValue(0)
        path = [x.path for x in dialog.F.GetObjects()]
        for no, ip in user:
            pool.apply_async(func=send_file,
                             args=(ip, app.client_tcp_port, path, no),
                             callback=lambda ic: dialog.update(ic[0], ic[1], ic[2], ic[3]))
        pool.close()
    except Exception as e:
        MessageBox(str(e))


def quick_send(s, d):
    for i in d:
        i = str(i).encode()
        s.sendall(pack("Q", len(i))), s.sendall(i)

def recv_exactly(s, n):
    m, d = 0, b''
    while m < n:
        t = s.recv(min(n-m,8192))
        m += len(t)
        d += t
    return d


def quick_recv(s):
    return recv_exactly(s, unpack("Q", recv_exactly(s, 8))[0]).decode()


def quick_recv_file(s, p):
    count = []
    try:
        if not os.path.isdir(p):
            os.mkdir(p)
        while quick_recv(s) != SEND_FILE_OVER:
            name = quick_recv(s)
            with open(os.path.join(p, name), "wb") as f:
                sz = unpack("Q", recv_exactly(s, 8))[0]
                f.write(recv_exactly(s, sz))
            count.append(name)
        return RECV_FILE_SUCCEED, count, NO_ERROR
    except Exception as e:
        print(str(e))
        return RECV_FILE_FAILED, count, e
