import os
import sys
from wx import EVT_BUTTON, EVT_MENU, EVT_COMBOBOX, EVT_CLOSE, EVT_ICONIZE
from wx import HORIZONTAL, VERTICAL, EXPAND, ALL, BOTH, GA_VERTICAL
from wx import ID_OK, ID_YES, YES_NO, ICON_QUESTION, ID_ABORT
from wx import BITMAP_TYPE_ICO
from wx import DEFAULT_FRAME_STYLE, LC_REPORT, RESIZE_BORDER, MAXIMIZE_BOX, CB_READONLY, FD_DEFAULT_STYLE, FD_MULTIPLE
from wx import Frame, Dialog, Icon, MenuBar, Menu, Panel, BoxSizer, Button, Gauge
from wx import DirDialog,  TextEntryDialog, MultiChoiceDialog, MessageDialog, FileDialog
from wx import MessageBox, ComboBox
from wx import TextCtrl, StaticText
from wx import App, SingleInstanceChecker, GetUserId, NewId
from wx.adv import TaskBarIcon, EVT_TASKBAR_LEFT_DOWN, EVT_TASKBAR_RIGHT_DOWN
from wx.adv import Animation, AnimationCtrl, ANIMATION_TYPE_GIF
from ObjectListView import ObjectListView, ColumnDefn

NO_ERROR = "NO ERROR"

CLIENT_SEARCH_SERVER = "SEARCH SERVER"
CLIENT_DISCOVER_SERVER = "DISCOVER SERVER"
CLIENT_ONLINE_CHECK = "ONLINE CHECK"
CLIENT_KICK_OUT = "KICK OUT"

CLIENT_VERITY = "VERITY"
CLIENT_VERITY_SUCCEED = "VERITY SUCCEED"
CLIENT_VERITY_FAILED = "VERITY FAILED"

CLIENT_COLLECT_WORK = "COLLECT WORK"
COLLECT_WORK_SUCCEED = "COLLECT WORK SUCCEED"
COLLECT_WORK_FAILED = "COLLECT WORK FAILED"

CLIENT_SEND_FILE = "SEND FILE"
CLIENT_RECV_FILE = "RECV FILE"

RECV_FILE_OVER = "RECV FILE OVER"
RECV_FILE_SUCCEED = "RECV FILE SUCCEED"
RECV_FILE_FAILED = "RECV FILE FAILED"
RECV_SUCCEED = "RECV SUCCEED"
RECV_FAILED = "RECV FAILED"

SEND_FILE_NOW = "SEND FILE NOW"
SEND_FILE_OVER = "SEND FILE OVER"
SEND_FILE_SUCCEED = "SEND FILE SUCCEED"
SEND_FILE_FAILED = "SEND FILE FAILED"

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
TABLE_TEST = 'create table test(no text primary key,belong text not null,in_path text,out_path text,point int not null)'
DEFAULT_SERVER_TCP_PORT = 7777
DEFAULT_CLIENT_TCP_PORT = 8888
DEFAULT_UDP_PORT = 9999
DEFAULT_FTP_PORT = 2121
PROJECT_STATUS_ON = "PROJECT_STATUS_ON"
PROJECT_STATUS_OFF = "PROJECT_STATUS_OFF"
DEFAULT_LOCAL_ADDRESS = "127.0.0.1"


def has(path, x, lang):
    for su in lang:
        if os.path.isfile(os.path.join(path, x+su)):
            return 1
    return 0


class Model(object):
    def __init__(self, no, name=None, prob=None, ip=None, point=None, path=None, lang=None):
        self.no = no
        self.name = name
        self.prob = " ".join([x+["☐", "☑"][has(os.path.join(path,no), x, lang)] for x in prob]) if prob is not None else ""
        self.ip = ip
        self.point = point
        self.path = os.path.join(path, no)

    def __eq__(self, other):
        return hash(self.no) == hash(other.no)

    def __hash__(self):
        return hash(self.no)

    def fresh_prob(self, prob, lang):
        self.prob = " ".join([x+["☐", "☑"][has(self.path, x, lang)] for x in prob])


class Test(object):
    def __init__(self, no, belong, in_path, out_path, point):
        self.no = no
        self.belong = belong
        self.in_path = in_path
        self.out_path = out_path
        self.point = point

    def __eq__(self, other):
        return hash(self.no) == hash(other.no)

    def __hash__(self):
        return hash(self.no)


class SR(object):
    def __init__(self, no, name=None, ip=None, op=None, files=None):
        self.no = no
        self.name = name
        self.ip = ip
        self.info = ""
        if op is not None:
            self.info = op + str(files)

    def __eq__(self, other):
        return hash(self.no) == hash(other.no)

    def __hash__(self):
        return hash(self.no)

    def fresh_info(self, op, files, error=None):
        self.info = op
        self.info += str(files) if len(files) > 0 else ""
        self.info += error if error is not None else ""


class FP(object):
    def __init__(self, path):
        self.path = path

    def __eq__(self, other):
        return hash(self.path) == hash(other.path)

    def __hash__(self):
        return hash(self.path)