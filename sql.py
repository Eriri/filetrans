import sqlite3
import os
import xlrd
import xlwt
from uuid import uuid4


def open_db(db_name):
    db_con = sqlite3.connect(db_name)
    db_cur = db_con.cursor()
    return db_con, db_cur


def close_db(db_con, db_cur):
    db_con.commit()
    db_cur.close()
    db_con.close()


def init_db(proj_path, db_name="conf.db"):
    db_name = os.path.join(proj_path, db_name)
    if os.path.isfile(db_name) == False:
        db_con, db_cur = open_db(db_name)
        db_cur.execute(
            'create table user_info(id text primary key,name text,pwd text)')
        db_cur.execute(
            'create table ip_info(ip text primary key,id text,time real)')
        db_cur.execute(
            'create table problem_info(id text primary key,time real,memory int)')
        close_db(db_con, db_cur)
    return db_name


def import_problem(Id, time, memory, db_name):
    db_con, db_cur = open_db(db_name)
    db_cur.execute("insert or replace into problem_info (id,time,memory) values('" +
                   Id+"','"+str(float(time))+"','"+str(int(memory))+"')")
    close_db(db_con, db_cur)


def import_user(Id, name, db_name):
    db_con, db_cur = open_db(db_name)
    db_cur.execute("insert or replace into user_info (id,name,pwd) values('" +
                   Id+"','", name+"','"+str(uuid4())[:8]+"')")
    close_db(db_con, db_cur)


def import_user_from_xls(xls_path, db_name):
    db_con, db_cur = open_db(db_name)
    with xlrd.open_workbook(xls_path) as xls_data:
        xls_sheet = xls_data.sheets()[0]
        xls_attr = xls_sheet.row_values(0)
        try:
            i_c = [i for i, x in enumerate(xls_attr) if x == "学号"][0]
            n_c = [i for i, x in enumerate(xls_attr) if x == "姓名"][0]
        except IndexError:
            return "IndexError"
        try:
            p_c = [i for i, x in enumerate(xls_attr) if x == "密码"][0]
            for i in range(1, xls_sheet.nrows):
                db_cur.execute(
                    "insert or replace into user_info (id,name,pwd) values ('" +
                    xls_sheet.row_values(i)[i_c]+"','" +
                    xls_sheet.row_values(i)[n_c]+"','" +
                    xls_sheet.row_values(i)[p_c]+"')")
        except IndexError:
            for i in range(1, xls_sheet.nrows):
                db_cur.execute(
                    "insert or replace into user_info (id,name,pwd) values ('" +
                    xls_sheet.row_values(i)[i_c]+"','" +
                    xls_sheet.row_values(i)[n_c]+"','" +
                    str(uuid4())[:8]+"')")
    close_db(db_con, db_cur)
    return "OK"


def export_user_to_xls(xls_path, db_name):
    db_con, db_cur = open_db(db_name)
    f = xlwt.Workbook()
    sh = f.add_sheet('user_sheet')
    for i, a in enumerate(["学号", "姓名", "密码"]):
        sh.write(0, i, a)
    items = db_cur.execute(
        "select * from user_info order by id asc").fetchall()
    for i, item in enumerate(items):
        for j in range(3):
            sh.write(i+1, j, item[j])
    f.save(xls_path)
    close_db(db_con, db_cur)
