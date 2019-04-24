import sys
import wx
import sqlite3
from serverbase import *
from sqlbase import *
from wx import *
from ObjectListView import ObjectListView, ColumnDefn
from utilities import *
from studentdialog import StudentDialog
from problemdialog import ProblemDialog
from workdialog import WorkDialog
from ftpdialog import FtpDialog


class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "FT", (0, 0), (600, 400), wx.DEFAULT_FRAME_STYLE, "main")
        self.local_address, self.server_port, self.client_port = DEFAULT_LOCAL_ADDRESS, DEFAULT_SERVER_PORT, DEFAULT_CLIENT_PORT
        self.path, self.database, self.server, self.ftp_server, self.status = None, None, None, None, PROJECT_STATUS_OFF

        self.Center(wx.BOTH), self.SetMinSize((600, 400))
        self.icon = wx.Icon()
        self.icon.CopyFromBitmap(wx.Bitmap("favicon.bmp", wx.BITMAP_TYPE_ANY))
        self.SetIcon(self.icon)

        MB, ME, ELSE = wx.MenuBar(), wx.Menu(), wx.Menu()
        MB.Append(ME, "工作区"), MB.Append(ELSE, "其他选项"), self.SetMenuBar(MB)

        self.Bind(wx.EVT_MENU, self.open, ME.Append(-1, "打开工作区..."))
        self.Bind(wx.EVT_MENU, self.close, ME.Append(-1, "关闭当前工作区"))
        self.Bind(wx.EVT_MENU, self.destroy, ME.Append(-1, "退出"))
        self.Bind(wx.EVT_MENU, self.change_server_port, ELSE.Append(-1, "选择服务器端口"))
        self.Bind(wx.EVT_MENU, self.change_client_port, ELSE.Append(-1, "选择客户端端口"))
        self.Bind(wx.EVT_MENU, self.open_ftp_server, ELSE.Append(-1, "运行FTP服务器"))
        self.Bind(wx.EVT_MENU, self.close_ftp_server, ELSE.Append(-1, "关闭FTP服务器"))
        self.Bind(wx.EVT_MENU, self.about, ELSE.Append(-1, "关于/帮助"))

        self.P, self.FGS, self.Buttons = wx.Panel(self), wx.FlexGridSizer(1, 2, 0, 0), wx.BoxSizer(wx.VERTICAL)

        self.OLV = ObjectListView(parent=self.P, sortable=True, style=wx.LC_REPORT)
        self.OLV.SetColumns([
            ColumnDefn("学号", "left", 100, "ID"),
            ColumnDefn("姓名", "left", 100, "NAME"),
            ColumnDefn("提交情况", "left", 100, "PROBLEM"),
            ColumnDefn("最终成绩", "left", 100, "POINT"),
            ColumnDefn("登录密码", "left", 100, "PASSWORD"),
            ColumnDefn("登陆时间", "left", 175, "TIME")])

        B = [wx.Button(self.P, 0, "学生管理"),
             wx.Button(self.P, 1, "题目管理"),
             wx.Button(self.P, 2, "接收作业"),
             wx.Button(self.P, 3, "发送文件"),
             wx.Button(self.P, 4, "系统评测")]
        for b in B:
            b.SetMinSize((100, 50)), self.Buttons.Add(b), self.Bind(wx.EVT_BUTTON, self.add, b)

        self.OLV.SetMinSize((400, 1000)), self.FGS.Add(self.OLV, 1, wx.EXPAND | wx.ALL, 5)
        self.Buttons.SetMinSize((100, 400)), self.FGS.Add(self.Buttons, 1, wx.EXPAND | wx.ALL, 5)
        self.FGS.AddGrowableCol(0), self.P.SetSizer(self.FGS)

    def destroy(self, event):
        self.close(), self.Destroy()

    def open(self, event=None):
        try:
            dd = wx.DirDialog(self, "选择工作区文件夹", sys.path[0])
            if dd.ShowModal() == wx.ID_OK:
                self.close()
                self.path, self.database = dd.GetPath(), Initiate(dd.GetPath())
                self.server = Run_Server(self.local_address, self.server_port, self.database)
                self.update()
                if not os.path.isdir(os.path.join(self.path, DEFAULT_PROBLEM_DIR)):
                    os.mkdir(os.path.join(self.path, DEFAULT_PROBLEM_DIR))
                if not os.path.isdir(os.path.join(self.path, DEFAULT_WORK_DIR)):
                    os.mkdir(os.path.join(self.path, DEFAULT_WORK_DIR))
                self.status = PROJECT_STATUS_ON
        except Exception as e:
            wx.MessageBox(str(e))

    def close(self, event=None):
        try:
            if self.status is PROJECT_STATUS_ON:
                self.server.shutdown(), self.server.server_close()
                self.path, self.database, self.server = None, None, None
                self.OLV.DeleteAllItems()
                self.status = PROJECT_STATUS_OFF
        except Exception as e:
            wx.MessageBox(str(e))

    def change_server_port(self, event):
        try:
            ted = wx.TextEntryDialog(self, "监听端口（0~65535）", "选择服务器端口", str(self.server_port))
            if ted.ShowModal() == wx.ID_OK:
                port = ted.GetValue()
                if not str.isdigit(port) or int(port) >= 65536:
                    raise Exception("请输入正确端口")
                if self.status is PROJECT_STATUS_ON:
                    self.server.shutdown(), self.server.server_close()
                self.server_port, self.server = int(port), Run_Server(self.local_address, int(port), self.database)
        except Exception as e:
            wx.MessageBox(str(e))

    def change_client_port(self, event):
        try:
            ted = wx.TextEntryDialog(self, "监听端口（0~65535）", "选择客户端端口", str(self.client_port))
            if ted.ShowModal() == wx.ID_OK:
                port = ted.GetValue()
                if not str.isdigit(port) or int(port) >= 65536:
                    raise Exception("请输入正确端口")
                self.client_port = int(port)
        except Exception as e:
            wx.MessageBox(str(e))

    def open_ftp_server(self, event=None):
        self.close_ftp_server()
        FtpDialog(self, self.icon).ShowModal()

    def close_ftp_server(self, event=None):
        if self.ftp_server is not None:
            self.ftp_server.close()
            self.ftp_server = None

    def about(self, event):
        msg = wx.MessageBox(message="这是一个尚未完成的程序\n请尽可能保证各种路径中不含特殊标点字符")

    def update(self, event=None):
        connection = sqlite3.connect(self.database)
        PROBLEM = [x[0] for x in Select(connection, "PROBLEM", ["ID"])]
        USER = Select(connection, "USER", ["*"])
        connection.close()
        self.OLV.DeleteAllItems()
        self.OLV.AddObjects([Model(x[0], x[1], x[2], x[3], PROBLEM, x[4], self.path) for x in USER])

    def add(self, event):
        if self.status is PROJECT_STATUS_ON:
            [StudentDialog(self, self.icon, self.database),
             ProblemDialog(self, self.icon, self.database, self.path),
             WorkDialog(self, self.icon, self.database), ][event.GetId()].ShowModal()
            #SendDialog(self, self.icon, self.database),
            #TestDialog(self, self.icon, self.database)
            self.update()


class MainApp(wx.App):
    def __init__(self):
        wx.App.__init__(self)
        self.frame = MainFrame()
        self.frame.Show()
        self.SetTopWindow(self.frame)


if __name__ == "__main__":
    app = MainApp()
    app.MainLoop()
