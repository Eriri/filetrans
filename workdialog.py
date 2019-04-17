import wx
from ObjectListView import ObjectListView,ColumnDefn

class WorkDialog(wx.Dialog):
    def __init__(self,parent,icon,database):
        wx.Dialog.__init__(self,parent,-1,"WD",(0,0),(500,300),wx.DEFAULT_FRAME_STYLE, "work")
        self.SetIcon(icon), self.SetMinSize((500, 300)), self.Center(wx.BOTH)
        self.icon, self.database = icon, database

        self.P, self.B = wx.Panel(self), wx.BoxSizer(wx.HORIZONTAL)

        self.SB = wx.StatusBar(self.P)




