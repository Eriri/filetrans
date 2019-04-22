import sqlite3
import os
import xlrd
import xlwt
import xlsxwriter
from uuid import uuid4
from utilities import *


def Select(connection, table, attributes, areas=None, values=None):
    attributes = ",".join(attributes)
    conditions = "" if areas is None else " where "+" and ".join([str(a) + "='" + str(v) + "'" for a, v in zip(areas, values)])
    return connection.execute("select "+attributes+" from "+table+conditions).fetchall()

def SelectOne(connection, table, attributes, areas=None, values=None):
    attributes = ",".join(attributes)
    conditions = "" if areas is None else " where "+" and ".join([str(a) + "='" + str(v) + "'" for a, v in zip(areas, values)])
    return connection.execute("select "+attributes+" from "+table+conditions).fetchone()


def Insert(connection, table, areas, values):
    areas, values = ",".join(areas), ",".join(["'"+str(v)+"'" for v in values])
    connection.execute("insert or replace into "+table + "("+areas+")" + "values("+values+")")


def Delete(connection, table, areas, values):
    conditions = " where "+" and ".join([str(a) + "='"+str(v)+"'" for a, v in zip(areas, values)])
    connection.execute("delete from "+table+conditions)


def Initiate(path):
    database = os.path.join(path, DEFAULT_DATABASE)
    if not os.path.isfile(database):
        connection = sqlite3.connect(database)
        connection.execute(TABLE_USER)
        connection.execute(TABLE_IP)
        connection.execute(TABLE_PROBLEM)
        connection.execute(TABLE_TEST)
        connection.commit(), connection.close()
    return database


def Import_Problem(database, ID, TIME, MEMORY):
    connection = sqlite3.connect(database)
    Insert(connection, "PROBLEM", ["ID", "TIME", "MEMORY"], [ID, TIME, MEMORY])
    connection.commit(), connection.close()


def Delete_Problem(database, IDs):
    connection = sqlite3.connect(database)
    for ID in IDs:
        Delete(connection, "PROBLEM", ["ID"], [ID]), Delete(connection, "TEST", ["BELONG"], [ID])
    connection.commit(), connection.close()


def Import_Test(database, PATH, BELONG, POINT):
    connection = sqlite3.connect(database)
    Insert(connection,"TEST",["PATH","BELONG","POINT"],[PATH,BELONG,POINT])
    connection.commit(),connection.close()


def Delete_Test(databse, PATHs=None, BELONGs=None):
    connection = sqlite3.connect(databse)
    if PATHs is not None:
        for PATH in PATHs:
            Delete(connection,"TEST",["PATH"],[PATH])
    if BELONGs is not None:
        for BELONG in BELONGs:
            Delete(connection,"TEST",["BELONG"],[BELONG])
    connection.commit(), connection.close()


def Import_User(database, ID, NAME, PASSWORD):
    connection = sqlite3.connect(database)
    PASSWORD = [PASSWORD, str(uuid4())[:8]][PASSWORD == ""]
    Insert(connection, "USER", ["ID", "NAME", "PASSWORD"], [ID, NAME, PASSWORD])
    connection.commit(), connection.close()


def Delete_User(database, IDs):
    connection = sqlite3.connect(database)
    for ID in IDs:
        Delete(connection, "USER", ["ID"], [ID])
    connection.commit(), connection.close()


def Import_User_From_Excel(database, path):
    connection = sqlite3.connect(database)
    sheet = xlrd.open_workbook(path).sheets()[0]
    attributes = sheet.row_values(0)
    ID, NAME = attributes.index("学号"), attributes.index("姓名")
    PASSWORD = [0, attributes.index("密码")]["密码" in attributes]
    for i in range(1, sheet.nrows):
        Insert(connection, "USER", ["ID", "NAME", "PASSWORD"],
               [sheet.row_values(i)[ID], sheet.row_values(i)[NAME],
                [sheet.row_values(i)[PASSWORD], str(uuid4())[:8]][PASSWORD == 0]])
    connection.commit(), connection.close()
    return IMPORT_FROM_XLS_SUCCEED


def Export_User_To_Excel(database, path, attributes):
    connection = sqlite3.connect(database)
    if os.path.splitext(path)[1] == ".xlsx":
        workbook = xlsxwriter.Workbook(path)
        sheet = workbook.add_worksheet("user_sheet")
    else:
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('user_sheet')
    for i, a in enumerate(attributes):
        sheet.write(0, i, a)
    for i, user in enumerate(Select(connection, "USER", attributes)):
        for j in range(len(attributes)):
            sheet.write(i+1, j, user[j])
    connection.close()
    if os.path.splitext(path)[1] == ".xlsx":
        workbook.close()
    else:
        workbook.save(path)
