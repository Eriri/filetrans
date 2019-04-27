import wx
from ObjectListView import ObjectListView, ColumnDefn
from sqlite3 import connect
from sqlbase import select
from utilities import *
from serverbase import *


class SendDialog(wx.Dialog):
    def __init__(self, app):
        wx.Dialog.__init__(self, app, -1, "SD", (0, 0), (550, 350), wx.DEFAULT_FRAME_STYLE, "sd")
        self.SetIcon(app.GetIcon()), self.SetMinSize((500, 300)), self.Center(wx.BOTH)
        self.PL, self.PR = wx.Panel(self), wx.Panel(self)
        self.B, self.BL, self.BR = wx.BoxSizer(wx.HORIZONTAL), wx.BoxSizer(wx.VERTICAL), wx.BoxSizer(wx.VERTICAL)

        self.F = ObjectListView(parent=self.PL, sortable=True, style=wx.LC_REPORT)
        self.F.SetColumns([ColumnDefn("文件路径", "left", 200, "path")])
        self.F.CreateCheckStateColumn()
        self.BL.Add(self.F, 1, wx.EXPAND | wx.ALL, 5)

        self.U = ObjectListView(parent=self.PL, sortable=True, style=wx.LC_REPORT)
        self.U.SetColumns([
            ColumnDefn("学号", "left", 100, "no"),
            ColumnDefn("姓名", "left", 100, "name"),
            ColumnDefn("IP地址", "left", 100, "ip"),
            ColumnDefn("发送情况", "left", 200, "info")])
        self.BL.Add(self.U, 1, wx.EXPAND | wx.ALL, 5)

        self.PL.SetSizer(self.BL)

        self.Bt = [wx.Button(self.PR, 0, "添加文件"), wx.Button(self.PR, 1, "删除文件"), wx.Button(self.PR, 2, "开始发送")]
        for b in self.Bt:
            self.BR.Add(b, 1, wx.EXPAND | wx.ALL, 5), self.Bind(wx.EVT_BUTTON, self.button_func, b)

        self.G = wx.Gauge(self.PR, -1, style=wx.GA_VERTICAL)
        self.BR.Add(self.G, 1, wx.EXPAND | wx.ALL, 5)

        self.PR.SetSizer(self.BR)

        self.B.Add(self.PL, 1), self.B.Add(self.PR, 0), self.SetSizer(self.B)

        self.init_all()

    def init_all(self):
        connection = connect(self.GetParent().database)
        user = [SR(no, name, ip) for no, name, ip in select(connection, "user", ["no", "name", "ip"])]
        connection.close()
        self.U.DeleteAllItems(), self.U.AddObjects(user)

    def update(self, no, count, info, error=None):
        obj = self.U.GetObjectAt(self.U.GetIndexOf(SR(no)))
        if info == SEND_FILE_SUCCEED:
            obj.fresh_info("成功发送文件，共包括", count)
        elif info == SEND_FILE_FAILED:
            obj.fresh_info("发送发生失败，已发送", count, error)
        self.U.RefreshObject(obj), self.G.SetValue(self.G.GetValue() + 1)
        if self.G.GetValue() == self.G.GetRange():
            for b in self.Bt:
                b.Enable()

    def button_func(self, event):
        if event.GetId() == 0:
            fd = wx.FileDialog(self, "选择文件路径", style=wx.FD_DEFAULT_STYLE | wx.FD_MULTIPLE)
            if fd.ShowModal() == wx.ID_OK:
                for x in fd.GetPaths():
                    if FP(x) not in set(self.F.GetObjects()):
                        self.F.AddObject(FP(x))
        elif event.GetId() == 1:
            self.F.RemoveObjects(self.F.GetCheckedObjects())
        elif event.GetId() == 2:
            for b in self.Bt:
                b.Disable()
            send_files(self.GetParent(), self)
