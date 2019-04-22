import os
import time

LOG_INFO_SUCCEED = "SUCCEED"
LOG_INFO_FAILED = "FAILED"
LOG_INFO_SERVER_ERROR = "SERVER ERROR"
CLIENT_ONLINE_CHECK = "ONLINE CHECK"
CLIENT_ONLINE_NOW = "ONLINE NOW"
CLIENT_OFFLINE = "OFFLINE"
CLIENT_SEND_FILE = "SEND FILE"
CLIENT_RECV_FILE = "RECV FILE"
CLIENT_VERITY = "VERITY"
CLIENT_LOG_IN = "LOG IN"
CLIENT_COLLECT_WORK = "COLLECT WORK"
RECV_FILE_OVER = "RECV FILE OVER"
COLLECT_WORK_ERROR = "COLLECT ERROR"
LANGUAGE_CONFIG = [".c", ".cpp", ".java"]
IMPORT_FROM_XLS_SUCCEED = "导入成功"
IMPORT_FROM_XLS_ERROR = "导入错误"
EXPORT_TO_XLS_SUCCEED = "导出成功"
EXPORT_TO_XLS_ERROR = "导出错误"
DEFAULT_DATABASE = "conf.db"
DEFAULT_PROBLEM_DIR = "problem"
DEFAULT_WORK_DIR = "work"
TABLE_USER = 'create table USER(ID text primary key not null,NAME text not null,PASSWORD text not null,TIME real,POINT int)'
TABLE_IP = 'create table IP(IP text primary key not null,ID text not null,NAME text not null,TIME real)'
TABLE_PROBLEM = 'create table PROBLEM(ID text primary key not null,TIME real not null,MEMORY int not null)'
TABLE_TEST = 'create table TEST(PATH text primary key,BELONG text not null,POINT int not null)'
DEFAULT_LOCAL_ADDRESS = "127.0.0.1"
DEFAULT_SERVER_PORT = 8080
DEFAULT_CLIENT_PORT = 8080
PROJECT_STATUS_ON = "PROJECT_STATUS_ON"
PROJECT_STATUS_OFF = "PROJECT_STATUS_OFF"


def Has(path, x):
    for suffix in LANGUAGE_CONFIG:
        if os.path.isfile(os.path.join(path, x, suffix)):
            return 1
    return 0


class Model(object):
    def __init__(self, ID, NAME, PASSWORD, TIME, PROBLEM, POINT, path):
        self.ID = ID
        self.NAME = NAME
        self.PASSWORD = PASSWORD
        self.TIME = time.ctime(TIME)
        self.PROBLEM = " ".join([x+["☒", "☑"][Has(path, x)] for x in PROBLEM])
        self.POINT = POINT


class Test(object):
    def __init__(self, PATH, BELONG, POINT):
        self.PATH = PATH
        self.BELONG = BELONG
        self.POINT = POINT


class User(object):
    def __init__(self, ID, IP):
        self.ID = ID
        self.IP = IP
        self.FILES = ""