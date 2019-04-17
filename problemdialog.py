import wx
import sys
import sqlite3
from ObjectListView import ObjectListView, ColumnDefn
from sqlbase import *
from utilities import *


class ProblemDialog(wx.Dialog):
    def __init__(self, parent, icon, database, path):
        wx.Dialog.__init__(self, parent, -1, "PD", (0, 0), (500, 300), wx.DEFAULT_FRAME_STYLE, "problem")
        self.SetIcon(icon), self.SetMinSize((500, 300)), self.Center(wx.BOTH)
        self.icon, self.database, self.path = icon, database, path
        self.P = wx.Panel(self)
        self.PL, self.PR = wx.Panel(self.P), wx.Panel(self.P)
        self.B, self.BL, self.BR = wx.BoxSizer(wx.HORIZONTAL), wx.BoxSizer(wx.VERTICAL), wx.BoxSizer(wx.VERTICAL)

        self.CB = wx.ComboBox(parent=self.PL, id=-1, value="None", choices=["None"], style=wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX,self.update,self.CB)
        self.BL.Add(self.CB, 0, wx.EXPAND | wx.ALL, 5)

        self.OLV = ObjectListView(parent=self.PL, sortable=True, id=-1, style=wx.LC_REPORT)
        self.OLV.SetColumns([
            ColumnDefn("路径", "left", 100, "PATH"),
            ColumnDefn("分数", "left", 100, "POINT")])
        self.OLV.CreateCheckStateColumn()
        self.BL.Add(self.OLV, 1, wx.EXPAND | wx.ALL, 5)

        self.PL.SetSizer(self.BL)

        BT = [wx.Button(self.PR, 0, "题目编辑"), wx.Button(self.PR, 1, "自动导入测试点"),
              wx.Button(self.PR, 2, "添加测试点"), wx.Button(self.PR, 3, "删除测试点")]
        for b in BT:
            self.BR.Add(b, 1, wx.EXPAND | wx.ALL, 5), self.Bind(wx.EVT_BUTTON, self.add, b)

        self.PR.SetSizer(self.BR)

        self.B.Add(self.PL, 1, wx.EXPAND), self.B.Add(self.PR, 0)
        self.P.SetSizer(self.B)

        self.fresh()

    def add(self, event):
        try:
            if event.GetId() == 0:
                EditProblem(self, self.icon, self.database).ShowModal()
            if event.GetId() == 1 and self.CB.GetValue() != "None":
                i = self.CB.GetValue().split()[0].split(":")[1]
                p = os.path.join(self.path, DEFAULT_PROBLEM_DIR, i)
                md = wx.MessageDialog(self, "确认从目录"+p+"中自动导入测试样点？", style=wx.YES_NO)
                if md.ShowModal() == wx.ID_YES and os.path.isdir(p):
                    fl = [x for x in os.listdir(p) if os.path.isfile(os.path.join(p, x))]
                    inl = [x.split(".")[0] for x in fl if len(x.split("."))==2 and x.split(".")[1] == "in"]
                    outl = [x.split(".")[0] for x in fl if len(x.split("."))==2 and x.split(".")[1] == "out"]
                    val = [os.path.join(p,str(x)+".in")+" "+os.path.join(p,str(x)+".out") for x in inl if x in outl]
                    for f in val:
                        Import_Test(self.database,f,i,10)
            if event.GetId() == 2 and self.CB.GetValue() != "None":
                EditTest(self,self.icon,self.database,self.CB.GetValue().split()[0].split(":")[1]).ShowModal()
            if event.GetId() == 3:
                Delete_Test(self.database,PATHs=[x.PATH for x in self.OLV.GetCheckedObjects()])
        except Exception as e:
            wx.MessageBox(str(e))
        self.fresh()

    def fresh(self, event=None):
        connection, pre = sqlite3.connect(self.database), self.CB.GetValue()
        choices = ["题目:"+str(x[0])+"   时限:"+str(x[1])+"秒   空间:"+str(x[2])+"兆" for x in Select(connection, "PROBLEM", ["*"])]
        connection.close()
        self.CB.Clear(), choices.append("None"), self.CB.AppendItems(choices)
        self.CB.SetValue(pre) if pre in choices else self.CB.SetValue("None")
        self.update()

    def update(self, event=None):
        self.OLV.DeleteAllItems()
        if self.CB.GetValue() != "None":
            connection,i = sqlite3.connect(self.database),self.CB.GetValue().split()[0].split(":")[1]
            self.OLV.AddObjects(
                [Test(x[0], x[1], x[2]) for x in Select(connection, "TEST", ["*"], ["BELONG"], [i])])
            connection.close()


class EditProblem(wx.Dialog):
    def __init__(self, parent, icon, database):
        wx.Dialog.__init__(self, parent, -1, "EP", (0, 0), (550, 120),
                           wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX), "ep")
        self.icon, self.database = icon, database
        self.Center(wx.BOTH), self.SetIcon(self.icon)

        self.P, self.B = wx.Panel(self), wx.BoxSizer(wx.VERTICAL)
        self.PU, self.BU = wx.Panel(self.P), wx.BoxSizer(wx.HORIZONTAL)
        self.PD, self.BD = wx.Panel(self.P), wx.BoxSizer(wx.HORIZONTAL)

        self.CB = wx.ComboBox(parent=self.PU, id=-1, value="None", choices=["None"], style=wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX, self.update, self.CB)
        self.BU.Add(self.CB, 1, wx.EXPAND | wx.ALL, 5)

        self.d = wx.Button(self.PU, -1, "删除")
        self.Bind(wx.EVT_BUTTON, self.delete, self.d)
        self.BU.Add(self.d, 0, wx.EXPAND | wx.ALL, 5)

        self.PU.SetSizer(self.BU)

        self.BD.Add(wx.StaticText(self.PD, -1, "题目名称:"), 1, wx.EXPAND | wx.ALL, 5)
        self.ID = wx.TextCtrl(self.PD, -1)
        self.ID.SetMaxSize((60, 60))
        self.BD.Add(self.ID, 1, wx.ALL, 5)

        self.BD.Add(wx.StaticText(self.PD, -1, "运行时限/秒:"), 1, wx.EXPAND | wx.ALL, 5)
        self.TIME = wx.TextCtrl(self.PD, -1)
        self.TIME.SetMaxSize((60, 60))
        self.BD.Add(self.TIME, 1, wx.ALL, 5)

        self.BD.Add(wx.StaticText(self.PD, -1, "内存空间/兆:"), 1, wx.EXPAND | wx.ALL, 5)
        self.MEMORY = wx.TextCtrl(self.PD, -1)
        self.MEMORY.SetMaxSize((60, 60))
        self.BD.Add(self.MEMORY, 1, wx.ALL, 5)

        self.e = wx.Button(self.PD, -1, "编辑/添加")
        self.Bind(wx.EVT_BUTTON, self.edit, self.e)
        self.BD.Add(self.e, 1, wx.EXPAND | wx.ALL, 5)

        self.PD.SetSizer(self.BD)

        self.B.Add(self.PU, 1, wx.EXPAND), self.B.Add(self.PD, 1, wx.EXPAND), self.P.SetSizer(self.B)
        self.fresh()

    def fresh(self, event=None):
        connection, pre = sqlite3.connect(self.database), self.CB.GetValue()
        choices = [x[0] for x in Select(connection, "PROBLEM", ["ID"])]
        self.CB.Clear(), choices.append("None"), connection.close()
        self.CB.AppendItems(choices)
        self.CB.SetValue(pre) if pre in choices else self.CB.SetValue("None")
        self.update()

    def update(self, event=None):
        if self.CB.GetValue() == "None":
            self.ID.SetEditable(True),self.ID.SetValue(""),self.TIME.SetValue(""),self.MEMORY.SetValue("")
        else:
            connection = sqlite3.connect(self.database)
            data = Select(connection, "PROBLEM", ["TIME", "MEMORY"], ["ID"], [self.CB.GetValue()])[0]
            self.ID.SetValue(self.CB.GetValue()), self.ID.SetEditable(False)
            self.TIME.SetValue(str(data[0])), self.MEMORY.SetValue(str(data[1]))
            connection.close()

    def delete(self, event):
        try:
            if self.CB.GetValue() != "None":
                Delete_Problem(self.database, [self.CB.GetValue()])
                Delete_Test(self.database,BELONGs=[self.CB.GetValue()])
                self.fresh()
        except Exception as e:
            wx.MessageBox(str(e))

    def edit(self, event):
        try:
            if float(self.TIME.GetValue()) > 0 and int(self.MEMORY.GetValue()) > 0 and len(self.ID.GetValue()) > 0:
                Import_Problem(self.database, self.ID.GetValue(), float(self.TIME.GetValue()), int(self.MEMORY.GetValue()))
                self.fresh()
            else:
                raise Exception("请输入正确参数")
        except Exception as e:
            wx.MessageBox(str(e))


class EditTest(wx.Dialog):
    def __init__(self,parent,icon,database,belong):
        wx.Dialog.__init__(self,parent,-1,"ET",(0,0),(700,70),
                           wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX), "et")
        self.icon, self.database,self.belong = icon, database, belong
        self.Center(wx.BOTH), self.SetIcon(self.icon)

        self.P = wx.Panel(self)
        self.B = wx.BoxSizer(wx.HORIZONTAL)

        self.I = wx.TextCtrl(self.P,-1,"")
        self.I.SetMaxSize((80,70))
        self.B.Add(self.I,1,wx.ALL,5)
        self.IB = wx.Button(self.P,0,"选择输入文件路径")
        self.Bind(wx.EVT_BUTTON,self.select,self.IB)
        self.B.Add(self.IB,1,wx.EXPAND|wx.ALL,5)

        self.O = wx.TextCtrl(self.P, -1, "")
        self.O.SetMaxSize((80, 70))
        self.B.Add(self.O, 1,wx.ALL, 5)
        self.OB = wx.Button(self.P, 1, "选择输出文件路径")
        self.Bind(wx.EVT_BUTTON, self.select, self.OB)
        self.B.Add(self.OB, 1, wx.EXPAND | wx.ALL, 5)

        self.B.Add(wx.StaticText(self.P,-1,"测试点分数"),1,wx.EXPAND|wx.ALL,5)
        self.PT = wx.TextCtrl(self.P,-1)
        self.PT.SetMaxSize((80, 70))
        self.B.Add(self.PT,1, wx.ALL,5)

        self.OK = wx.Button(self.P,-1,"添加")
        self.Bind(wx.EVT_BUTTON,self.click,self.OK)
        self.B.Add(self.OK,1,wx.EXPAND|wx.ALL,5)

        self.P.SetSizer(self.B)

    def select(self,event):
        fd = wx.FileDialog(self,"选择文件",sys.path[0])
        fd.SetIcon(self.icon),fd.Center(wx.BOTH)
        if fd.ShowModal() == wx.ID_OK:
            [self.I,self.O][event.GetId()].SetValue(fd.GetPath())

    def click(self,event):
        try:
            if os.path.isfile(self.I.GetValue()) and os.path.isfile(self.O.GetValue()) and int(self.PT.GetValue())>=0:
                Import_Test(self.database,self.I.GetValue()+" "+self.O.GetValue(),self.belong,int(self.PT.GetValue()))
            else:
                raise Exception("请输入正确参数")
        except Exception as e:
            wx.MessageBox(str(e))
        self.Destroy()