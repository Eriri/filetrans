import wx
import sqlite3
from ObjectListView import ObjectListView, ColumnDefn
from sqlbase import *
from utilities import *


class StudentDialog(wx.Dialog):
    def __init__(self, parent, icon, database):
        wx.Dialog.__init__(self, parent, -1, "SD", (0, 0), (500, 300), wx.DEFAULT_FRAME_STYLE, "student")
        self.SetIcon(icon), self.SetMinSize((500, 300)), self.Center(wx.BOTH)
        self.icon, self.database = icon, database
        self.P,self.B = wx.Panel(self),wx.BoxSizer(wx.HORIZONTAL)
        self.PR, self.BR = wx.Panel(self.P), wx.BoxSizer(wx.VERTICAL)

        self.OLV = ObjectListView(parent=self.P, sortable=True, style=wx.LC_REPORT)
        self.OLV.SetColumns([
            ColumnDefn("学号", "left", 100, "ID"),
            ColumnDefn("姓名", "left", 100, "NAME"),
            ColumnDefn("登录密码", "left", 100, "PASSWORD")])
        self.OLV.CreateCheckStateColumn()

        B = [wx.Button(self.PR, 0, "添加"), wx.Button(self.PR, 1, "删除"),
             wx.Button(self.PR, 2, "从Excel添加"), wx.Button(self.PR, 3, "导出到Excel")]
        for b in B:
            self.BR.Add(b,0,wx.EXPAND|wx.ALL,5), self.Bind(wx.EVT_BUTTON, self.add, b)
        self.PR.SetSizer(self.BR)

        self.B.Add(self.OLV, 1, wx.EXPAND | wx.ALL, 5)
        self.B.Add(self.PR, 0)
        self.P.SetSizer(self.B)

        self.update()

    def update(self):
        connection = sqlite3.connect(self.database)
        USER = Select(connection, "USER", ["*"])
        connection.close()
        self.OLV.DeleteAllItems()
        self.OLV.AddObjects([Model(x[0], x[1], x[2], 0, "", "", "") for x in USER])

    def add(self, event):
        try:
            if event.GetId() == 0:
                D = AddStudent(self, self.icon, self.database)
                D.ShowModal()
            if event.GetId() == 1:
                md = wx.MessageDialog(self, "确认删除？", style=wx.YES_NO | wx.ICON_QUESTION)
                md.SetIcon(self.icon)
                if md.ShowModal() == wx.ID_YES:
                    Delete_User(self.database, [obj.ID for obj in self.OLV.GetCheckedObjects()])
            if event.GetId() == 2:
                D = wx.FileDialog(self, "选择Excel文件", wildcard="Excel files (*.xls;*.xls)|*.xls;*xlsx")
                if D.ShowModal() == wx.ID_OK:
                    Import_User_From_Excel(self.database, D.GetPath())
            if event.GetId() == 3:
                md = wx.MultiChoiceDialog(self, "选择导出属性", "导出", ["学号", "姓名", "密码", "成绩"])
                cte = {0: "ID", 1: "NAME", 2: "PASSWORD", 3: "POINT"}
                if md.ShowModal() == wx.ID_OK:
                    D = wx.FileDialog(self, "选择Excel文件", wildcard="Excel files (*.xls;*.xls)|*.xls;*xlsx")
                    if D.ShowModal() == wx.ID_OK:
                        Export_User_To_Excel(self.database, D.GetPath(), [cte[x] for x in md.GetSelections()])
            self.update()
        except Exception as e:
            wx.MessageBox(str(e))


class AddStudent(wx.Dialog):
    def __init__(self, parent, icon, database):
        wx.Dialog.__init__(self, parent, -1, "AD", (0, 0), (550, 70),
                           wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX), "ad")
        self.icon, self.database = icon, database
        self.Center(wx.BOTH), self.SetIcon(self.icon)
        self.P, self.B = wx.Panel(self), wx.BoxSizer(wx.HORIZONTAL)
        self.B.Add(wx.StaticText(self.P, -1, "学号"), 1, wx.EXPAND | wx.ALL, 5)
        self.ID = wx.TextCtrl(self.P, -1)
        self.B.Add(self.ID, 1, wx.EXPAND | wx.ALL, 5)

        self.B.Add(wx.StaticText(self.P, -1, "姓名"), 1, wx.EXPAND | wx.ALL, 5)
        self.NAME = wx.TextCtrl(self.P, -1)
        self.B.Add(self.NAME, 1, wx.EXPAND | wx.ALL, 5)

        self.B.Add(wx.StaticText(self.P, -1, "密码"), 1, wx.EXPAND | wx.ALL, 5)
        self.PASSWORD = wx.TextCtrl(self.P, -1)
        self.B.Add(self.PASSWORD, 1, wx.EXPAND | wx.ALL, 5)

        self.OK = wx.Button(self.P, -1, "确定")
        self.Bind(wx.EVT_BUTTON, self.click, self.OK)
        self.B.Add(self.OK, 1, wx.EXPAND | wx.ALL, 5)

        self.P.SetSizer(self.B)

    def click(self, event):
        if self.ID.GetValue() == "" or self.NAME.GetValue() == "":
            wx.MessageBox("请正确输入")
            return
        Import_User(self.database, self.ID.GetValue(), self.NAME.GetValue(), self.PASSWORD.GetValue())
        self.Destroy()
