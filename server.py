import tkinter
import os
import sys
import pandas
import random
import string
import socketserver
from tkinter import *
from tkinter.filedialog import *


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
    work_dir, work_port = path.get(), port.get()
    return work_dir, work_port


user_info = {}
problem_info = set()
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
    conf = eval(f.read())
    user_info, problem_info = conf["user_info"], conf["problem_info"]
    f.close()


def save_conf():
    f = open(conf_path, "w")
    f.write(str({"user_info": user_info, "problem_info": problem_info}))
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


def prepare_(work_dir, work_port):
    load_conf()
    logging_server = socketserver.ForkingTCPServer()


def run_():
    return


if __name__ == "__main__":
    work_dir, work_port = init_()
    conf_path = work_dir+"\\conf"
    #sserver = prepare_(work_dir, work_port)
    #run_(sserver, work_dir, work_port)
