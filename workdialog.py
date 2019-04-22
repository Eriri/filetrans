import wx
from ObjectListView import ObjectListView,ColumnDefn

class WorkDialog(wx.Dialog):
    def __init__(self,parent,icon,database):
        wx.Dialog.__init__(self,parent,-1,"WD",(0,0),(500,300),wx.DEFAULT_FRAME_STYLE, "work")
        self.SetIcon(icon), self.SetMinSize((500, 300)), self.Center(wx.BOTH)
        self.icon, self.database = icon, database

        self.B, self.PR, self.BR = wx.BoxSizer(wx.HORIZONTAL), wx.Panel(self), wx.BoxSizer(wx.VERTICAL)

        self.OLV = ObjectListView(parent=self,sortable=True,style=wx.LC_REPORT)
        self.OLV.SetColumns([
            ColumnDefn("学号","left",100,"ID"),
            ColumnDefn("IP","left",100,"IP")])

    def update(self,event=None):





