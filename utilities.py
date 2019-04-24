import os
import time

LOG_INFO_SUCCEED = "SUCCEED"
LOG_INFO_FAILED = "FAILED"
LOG_INFO_SERVER_ERROR = "SERVER ERROR"
CLIENT_SEARCH_SERVER = "SERVER"
CLIENT_ONLINE_CHECK = "ONLINE CHECK"
CLIENT_ONLINE_NOW = "ONLINE NOW"
CLIENT_KICK_OUT = "KICK OUT"
CLIENT_SEND_FILE = "SEND FILE"
CLIENT_RECV_FILE = "RECV FILE"
CLIENT_VERITY = "VERITY"
CLIENT_LOG_IN = "LOG IN"
CLIENT_LOG_OUT = "LOG OUT"
CLIENT_COLLECT_WORK = "COLLECT WORK"
RECV_FILE_OVER = "RECV FILE OVER"
SEND_FILE_OVER = "SEND FILE OVER"
COLLECT_WORK_ERROR = "COLLECT ERROR"
LANGUAGE_CONFIG = [".c", ".cpp", ".java", ".py", ".pas"]
IMPORT_FROM_XLS_SUCCEED = "导入成功"
IMPORT_FROM_XLS_ERROR = "导入错误"
EXPORT_TO_XLS_SUCCEED = "导出成功"
EXPORT_TO_XLS_ERROR = "导出错误"
DEFAULT_DATABASE = "conf.db"
DEFAULT_PROBLEM_DIR = "problems"
DEFAULT_WORK_DIR = "works"
TABLE_USER = 'create table user(no text primary key not null,name text not null,ip text,point int)'
TABLE_PROBLEM = 'create table problem(no text primary key not null,time real not null,memory int not null)'
TABLE_TEST = 'create table test(path text primary key,belong text not null,point int not null)'
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
    def __init__(self, ID, NAME, PROBLEM, POINT, IP, TIME, path):
        self.ID = ID
        self.NAME = NAME
        self.PROBLEM = " ".join([x+["☒", "☑"][Has(path, x)] for x in PROBLEM])
        self.POINT = POINT
        self.IP = IP
        self.TIME = time.ctime(TIME)

    def __eq__(self, other):
        return hash(self.ID) == hash(other.ID)

    def __hash__(self):
        return hash(self.ID)


class Test(object):
    def __init__(self, PATH, BELONG, POINT):
        self.PATH = PATH
        self.BELONG = BELONG
        self.POINT = POINT