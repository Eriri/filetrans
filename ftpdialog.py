import wx
import sys
from ftpbase import *
from utilities import *


class FtpDialog(wx.Dialog):
    def __init__(self, parent, icon):
        wx.Dialog.__init__(self, parent, -1, "FD", (0, 0), (550, 70),
                           wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX), "ftp")
        self.SetIcon(icon), self.Center(wx.BOTH)
        self.P, self.B = wx.Panel(self), wx.BoxSizer(wx.HORIZONTAL)

        self.B.Add(wx.StaticText(self.P, -1, "端口"), 1, wx.EXPAND | wx.ALL, 5)
        self.PORT = wx.TextCtrl(self.P, -1, "2121")
        self.B.Add(self.PORT, 1, wx.EXPAND | wx.ALL, 5)

        self.B.Add(wx.StaticText(self.P, -1, "路径"), 1, wx.EXPAND | wx.ALL, 5)
        self.PATH = wx.TextCtrl(self.P, -1, sys.path[0])
        self.B.Add(self.PATH, 1, wx.EXPAND | wx.ALL, 5)

        self.SB = wx.Button(self.P, -1, "选择文件夹")
        self.Bind(wx.EVT_BUTTON, self.select, self.SB)
        self.B.Add(self.SB, 1, wx.EXPAND | wx.ALL, 5)

        self.OK = wx.Button(self.P, -1, "开启FTP服务器")
        self.Bind(wx.EVT_BUTTON, self.click, self.OK)
        self.B.Add(self.OK, 1, wx.EXPAND | wx.ALL, 5)

        self.P.SetSizer(self.B)

    def select(self, event):
        fd = wx.DirDialog(self, "选择文件夹", sys.path[0])
        if fd.ShowModal() == wx.ID_OK:
            self.PATH.SetValue(fd.GetPath())

    def click(self, event):
        try:
            if self.PATH.GetValue() == "" or not str.isdigit(self.PORT.GetValue()) or int(self.PORT.GetValue()) >= 65536:
                raise Exception("请输入正确配置")
            self.GetParent().ftp_server = Run_Ftp(DEFAULT_LOCAL_ADDRESS, int(self.PORT.GetValue()), self.PATH.GetValue())
        except Exception as e:
            wx.MessageBox(str(e))
        self.Destroy()
