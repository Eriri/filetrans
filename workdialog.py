import wx
from ObjectListView import ObjectListView, ColumnDefn
from serverbase import collect_works
from sqlite3 import connect
from utilities import *
from sqlbase import *


class WorkDialog(wx.Dialog):
    def __init__(self, app):
        wx.Dialog.__init__(self, app, -1, "WD", (0, 0), (500, 300), wx.DEFAULT_FRAME_STYLE, "work")
        self.SetIcon(app.GetIcon()), self.SetMinSize((500, 300)), self.Center(wx.BOTH)

        self.B, self.PR, self.BR = wx.BoxSizer(wx.HORIZONTAL), wx.Panel(self), wx.BoxSizer(wx.VERTICAL)

        self.OLV = ObjectListView(parent=self, sortable=True, style=wx.LC_REPORT)
        self.OLV.SetColumns([
            ColumnDefn("学号", "left", 100, "no"),
            ColumnDefn("姓名", "left", 100, "name"),
            ColumnDefn("IP地址", "left", 100, "ip"),
            ColumnDefn("接收情况", "left", 200, "info")])
        self.B.Add(self.OLV, 1, wx.EXPAND | wx.ALL, 5)

        self.C = wx.Button(self.PR, -1, "开始接收")
        self.Bind(wx.EVT_BUTTON, self.collect, self.C)
        self.BR.Add(self.C, 0, wx.EXPAND | wx.ALL, 5)

        self.G = wx.Gauge(self.PR, -1, style=wx.GA_VERTICAL)
        self.BR.Add(self.G, 1, wx.EXPAND | wx.ALL, 5)

        self.PR.SetSizer(self.BR)
        self.B.Add(self.PR, 0)
        self.SetSizer(self.B)

        self.init_all()

    def init_all(self):
        connection = connect(self.GetParent().database)
        user = [SR(no, name, ip) for no, name, ip in select(connection, "user", ["no", "name", "ip"])]
        connection.close()
        self.OLV.DeleteAllItems(), self.OLV.AddObjects(user)

    def update(self, no, count, info, error=None):
        obj = self.OLV.GetObjectAt(self.OLV.GetIndexOf(SR(no)))
        if info == COLLECT_WORK_SUCCEED:
            obj.fresh_info("成功接收作业，共包括", count)
        elif info == COLLECT_WORK_FAILED:
            obj.fresh_info("接收发生失败，已接收", count, error)
        self.OLV.RefreshObject(obj), self.G.SetValue(self.G.GetValue() + 1)
        if self.G.GetValue() == self.G.GetRange():
            self.C.Enable()

    def collect(self, event=None):
        self.C.Disable(), collect_works(self.GetParent(), self)

