import tkinter
import os
import sys
import pandas
import random
import string
import socketserver
from tkinter import *
from tkinter.filedialog import *
from tkinter import ttk


def init_():
    work_dir = sys.path[0]
    work_port = 8080
    tk = tkinter.Tk()
    tk.geometry("500x40")
    tk.resizable(False, False)
    path = StringVar(value=work_dir)
    port = StringVar(value=work_port)

    def change_path(path):
        path.set(askdirectory())
    Label(master=tk, text="工作目录").grid(row=0, column=0)
    Entry(master=tk, textvariable=path).grid(row=0, column=1)
    Button(master=tk, text="选择路径",
           command=lambda: change_path(path)).grid(row=0, column=2)
    Label(master=tk, text="登录端口").grid(row=0, column=3)
    Entry(master=tk, textvariable=port).grid(row=0, column=4)
    Button(master=tk, text="确认", command=tk.destroy).grid(row=0, column=5)
    tk.mainloop()
    work_dir, work_port = path.get(), int(port.get())
    return work_dir, work_port


user_info = {}
problem_info = set()
addr_info = {}
conf_path = ""


def gen_pwd():
    return ''.join(random.sample(
        string.ascii_letters + string.digits, 8))


def load_conf():
    try:
        f = open(conf_path, "r")
    except FileNotFoundError:
        return
    global user_info
    global problem_info
    global addr_info
    conf = eval(f.read())
    user_info, problem_info, addr_info = conf["user_info"], conf["problem_info"], conf["addr_info"]
    f.close()


def save_conf():
    f = open(conf_path, "w")
    f.write(str({"user_info": user_info,
                 "problem_info": problem_info,
                 "addr_info": addr_info}))
    f.close()


def add_user_(user_no, user_na):
    if user_no not in user_info:
        pwd = gen_pwd()
        user_info[user_no] = [user_na, pwd]


def add_user_from_xls_(xls_path):
    xls_data = pandas.read_excel(open(xls_path), names=[
                                 "学号", "姓名", "密码"], dtype=str)
    for idx, rd in xls_data.iterrows():
        if rd[0] not in user_info:
            user_no, user_na = rd[0], rd[1]
            if type(rd[2]) == float:
                pwd = gen_pwd
            else:
                pwd = rd[2]
            user_info[user_no] = [user_na, pwd]
    save_conf()


def update_user_info_(tv):
    tv.insert("", "end", values=["1", "2", "3"])


class logging_requst(socketserver.BaseRequestHandler):
    def handle(self):
        info = self.request.recv(1024)
        info = info.decode().split()
        if info[0] in user_info and info[1] == user_info[info[0]][1]:
            addr_info[info[0]] = self.request.client.address
            self.request.sendall("succeed".encode())
            save_conf()
        self.request.sendall("error".encode())


def prepare_(work_dir, work_port):
    load_conf()
    tk = tkinter.Tk()
    tk.geometry('600x400')
    tk.resizable(False, False)
    status = LabelFrame(master=tk, text="状态", height=300, width=600)
    status.pack_propagate(0)
    status.pack(side="top", padx=10, pady=10)
    tv = ttk.Treeview(master=status, show='headings',
                      columns=("id", "name", "logged"))
    tv.column("id", width=80, anchor="center")
    tv.column("name", width=80, anchor="center")
    tv.column("logged", width=40, anchor="center")
    tv.heading("id", text="学号")
    tv.heading("name", text="姓名")
    tv.heading("logged", text="登陆状态")
    tv.pack(padx=5, pady=5, side="top")
    vsb = ttk.Scrollbar(
        master=status, orient=tkinter.VERTICAL, command=tv.yview)
    tv.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="both")

    update_user_info_(tv)
    add_button = ttk.Button(master=status, text="添加学生",
                            command=lambda: update_user_info_(tv))
    add_button.pack(anchor="sw")
    logging_server = socketserver.ThreadingTCPServer(
        ('127.0.0.1', work_port), logging_requst)
    return logging_server, tk


if __name__ == "__main__":
    work_dir, work_port = init_()
    conf_path = work_dir+"\\conf"
    save_conf()
    logging_server, tk = prepare_(work_dir, work_port)
    tk.mainloop()
