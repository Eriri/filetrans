import wx
import sys
from utilities import *
from serverbase import *

class FtpDialog(wx.Dialog):
    def __init__(self, parent, icon):
        wx.Dialog.__init__(self, parent, -1, "FD", (0, 0), (550, 70),
                           wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX), "ftp")
        self.SetIcon(icon), self.Center(wx.BOTH)
        self.P, self.B = wx.Panel(self), wx.BoxSizer(wx.HORIZONTAL)

        self.B.Add(wx.StaticText(self.P, -1, "端口"), 1, wx.EXPAND | wx.ALL, 5)
        self.PORT = wx.TextCtrl(self.P, -1, str(self.GetParent().ftp_port))
        self.B.Add(self.PORT, 1, wx.EXPAND | wx.ALL, 5)

        self.B.Add(wx.StaticText(self.P, -1, "路径"), 1, wx.EXPAND | wx.ALL, 5)
        self.PATH = wx.TextCtrl(self.P, -1, str(self.GetParent().ftp_path))
        self.B.Add(self.PATH, 1, wx.EXPAND | wx.ALL, 5)

        self.SB = wx.Button(self.P, -1, "选择文件夹")
        self.Bind(wx.EVT_BUTTON, self.select, self.SB)
        self.B.Add(self.SB, 1, wx.EXPAND | wx.ALL, 5)

        self.OK = wx.Button(self.P, -1, "开启FTP服务器")
        self.Bind(wx.EVT_BUTTON, self.click, self.OK)
        self.B.Add(self.OK, 1, wx.EXPAND | wx.ALL, 5)

        self.P.SetSizer(self.B)

    def select(self, event):
        fd = wx.DirDialog(self, "选择文件夹", self.PATH.GetValue())
        if fd.ShowModal() == wx.ID_OK:
            self.PATH.SetValue(fd.GetPath())

    def click(self, event):
        try:
            if not os.path.isdir(self.PATH.GetValue()) or int(self.PORT.GetValue()) >= 65536 or int(self.PORT.GetValue()) <= 0:
                raise Exception("请输入正确配置")
            self.GetParent().ftp_path = self.PATH.GetValue()
            self.GetParent().ftp_port = int(self.PORT.GetValue())
            self.SetReturnCode(wx.ID_OK)
        except Exception as e:
            self.SetReturnCode(wx.ID_ABORT)
            wx.MessageBox(str(e))
        self.Destroy()
