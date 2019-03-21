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
            'create table user_info(id varchar(20) primary key,name varchar(10),pwd varchar(8),ip varchar(20))')
        db_cursor.execute(
            'create table problem_info(id varchar(20) primary key)')
        db_cursor.execute(
            'create table ip_info(ip vachar(20) primary key,id varchar(20)')
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
            db_cursor.execute("update user_info set ip='" +
                              self.request.client.address +
                              "' where id='"+info[0]+"'")
            db_cursor.execute("insert or ignore into ip_info (ip) values ('" +
                              self.request.client.address+"')")
            db_cursor.execute("update ip_info set id='" +
                              info[0]+"' where ip='" +
                              self.request.client.address+"')")
        db_conn.commit()
        db_cursor.close()
        db_conn.close()


def init_ss_():
    ss = socketserver.ThreadingTCPServer(('127.0.0.1', 8080), ss_req)
    return ss


def collect_work_():
    s = socket.socket()
    db_conn = sqlite3.connect(db_name)
    db_cursor = db_conn.cursor()
    items = db_cursor.execute("select * from ip_info").fetchall()
    probs = db_cursor.execute("select * from problem_info").fetchall()
    for item in items:
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
    lc = wx.ListCtrl(parent=rt, pos=(10, 20), size=(450, 400),
                     style=wx.LC_REPORT | wx.BORDER_SUNKEN)
    lc.InsertColumn(0, "学号", format=wx.LIST_FORMAT_LEFT, width=100)
    lc.InsertColumn(1, "姓名", format=wx.LIST_FORMAT_LEFT, width=100)
    lc.InsertColumn(2, "ip登记状态", format=wx.LIST_FORMAT_LEFT, width=80)
    lc.InsertColumn(3, "题目接收状态", format=wx.LIST_FORMAT_LEFT, width=100)
    lc.Show(True)
    bt1 = wx.Button(parent=rt, pos=(480, 20), size=(120, 40), label="学生管理")
    bt1.Show(True)
    bt2 = wx.Button(parent=rt, pos=(480, 80), size=(120, 40), label="题目管理")
    bt2.Show(True)
    return app


if __name__ == "__main__":
    init_db_()
    ss = init_ss_()
    app = init_gui_()
    # ss.serve_forever()
    app.MainLoop()
