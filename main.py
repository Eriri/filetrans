import sqlite3
import sys
import random
import string
import xlwt
import xlrd
import socket
import socketserver
import wx
from wx import *
from ObjectListView import ObjectListView, ColumnDefn
import time

work_dir = sys.path[0]
db_name = work_dir+'/'+'conf.db'


def gen_pwd_():
    return ''.join(random.sample(
        string.ascii_letters + string.digits, 8))


def add_user_info_from_xls_(xls_path):
    db_conn = sqlite3.connect(db_name)
    db_cursor = db_conn.cursor()
    with xlrd.open_workbook(xls_path) as xls_data:
        xls_sheet = xls_data.sheets()[0]
        xls_attr = xls_sheet.row_values(0)
        try:
            id_c = [i for i, x in enumerate(xls_attr) if x == "学号"][0]
            name_c = [i for i, x in enumerate(xls_attr) if x == "姓名"][0]
        except IndexError:
            print("make sure intended column existed")
            return "failed"
        for i in range(1, xls_sheet.nrows):
            id_ = xls_sheet.row_values(i)[id_c]
            name_ = xls_sheet.row_values(i)[name_c]
            db_cursor.execute(
                "insert or ignore into user_info (id,name,pwd) values ('" +
                id_+"','"+name_+"','"+gen_pwd_()+"')")
    db_conn.commit()
    db_cursor.close()
    db_conn.close()
    return "succeed"


def add_user_info_(id_, name_):
    db_conn = sqlite3.connect(db_name)
    db_cursor = db_conn.cursor()
    db_cursor.execute("insert or ignore into user_info (id,name,pwd) values('" +
                      id_+"','", name_+"','"+gen_pwd_()+"')")
    db_conn.commit()
    db_cursor.close()
    db_conn.close()


def export_user_info_to_xls_():
    f = xlwt.Workbook()
    sh = f.add_sheet('Sheet1')
    sh.write(0, 0, '学号')
    sh.write(0, 1, '姓名')
    sh.write(0, 2, '密码')
    db_conn = sqlite3.connect(db_name)
    db_cursor = db_conn.cursor()
    row_id = 1
    items = db_cursor.execute(
        "select * from user_info order by id asc").fetchall()
    for item in items:
        for i in range(3):
            sh.write(row_id, i, item[i])
        row_id += 1
    f.save('user_info.xls')
    db_cursor.close()
    db_conn.close()


def init_db_():
    try:
        f = open(db_name)
    except FileNotFoundError:
        db_conn = sqlite3.connect(db_name)
        db_cursor = db_conn.cursor()
        db_cursor.execute(
            'create table user_info(id text primary key,name text,pwd text)')
        db_cursor.execute(
            'create table problem_info(id text primary key)')
        db_cursor.execute(
            'create table ip_info(ip text primary key,id text,time real)')
        db_conn.commit()
        db_cursor.close()
        db_conn.close()
    else:
        f.close()


class ss_req(socketserver.BaseRequestHandler):
    def handle(self):
        info = self.request.recv(1024)
        info = info.decode().split()
        db_conn = sqlite3.connect(db_name)
        db_cursor = db_conn.cursor()
        item = db_cursor.execute(
            "select * from user_info where id ='"+info[0]+"'").fetchall()
        if len(item) == 0:
            self.request.sendall("no such user".encode())
        elif item[0][2] != info[1]:
            self.request.sendall("wrong password".encode())
        else:
            self.request.sendall("succeed".encode())
            db_cursor.execute("insert or ignore into ip_info (ip) values ('" +
                              self.request.client.address+"')")
            db_cursor.execute("update ip_info set id='" + info[0] +
                              "time='" + str(time.time()) +
                              "' where ip='" +
                              self.request.client.address+"')")
        db_conn.commit()
        db_cursor.close()
        db_conn.close()


class hb_req(socketserver.BaseRequestHandler):
    def handle(self):
        info = self.request.recv(1024)
        info = info.decode()
        db_conn = sqlite3.connect(db_name)
        db_cursor = db_conn.cursor()
        db_cursor.execute("update ip_info set time='" + str(time.time()) +
                          "' where ip="+self.request.client.address+"')")
        db_conn.commit()
        db_cursor.close()
        db_conn.close()


def init_ss_():
    ss = socketserver.ThreadingTCPServer(('127.0.0.1', 8080), ss_req)
    return ss


def init_hb_():
    hb = socketserver.ThreadingTCPServer(('127.0.0.1', 9090), hb_req)
    return hb


def collect_work_():
    s = socket.socket()
    db_conn = sqlite3.connect(db_name)
    db_cursor = db_conn.cursor()
    items = db_cursor.execute("select * from ip_info").fetchall()
    probs = db_cursor.execute("select * from problem_info").fetchall()
    for item in items:
        if time.time() - item[3] >= 30.0:
            continue
        if os.path.exists(item[1]) == False:
            os.mkdir(item[1])
        try:
            s.connect((item[0], 8080))
            for prob in probs:
                s.send(prob.encode())
                info = s.recv(1024)
                info = info.decode()
                if info == "not exists":
                    continue
                f = open(item[1]+"/"+prob, "w")
                f.write(info)
                f.close()
            s.send("over".encode())
        finally:
            s.close()
    db_cursor.close()
    db_conn.close()
    return


def init_gui_():
    app = wx.App()
    rt = wx.Frame(None, title="filetrans", size=(
        640, 480), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
    rt.Show(True)
    global olv
    olv = ObjectListView(parent=rt, pos=(10, 20), size=(450, 400),
                         style=wx.LC_REPORT | wx.BORDER_SUNKEN, sortable=True)
    olv.SetColumns([
        ColumnDefn("学号", "left", 120, "id"),
        ColumnDefn("姓名", "left", 120, "name"),
        ColumnDefn("在线状态", "left", 120, "ip"),
        ColumnDefn("接收情况", "left", 120, "status")
    ])
    olv.Show(True)
    bt1 = wx.Button(parent=rt, pos=(480, 20), size=(120, 40), label="学生管理")
    bt1.Show(True)
    bt2 = wx.Button(parent=rt, pos=(480, 80), size=(120, 40), label="题目管理")
    bt2.Show(True)
    bt3 = wx.Button(parent=rt, pos=(480, 140), size=(120, 40), label="接收作业")
    return app


if __name__ == "__main__":
    init_db_()
    ss = init_ss_()
    hb = init_hb_()
    app = init_gui_()
    app.MainLoop()
