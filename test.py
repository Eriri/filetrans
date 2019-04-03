import sys
import sql
import serverbase
import os
import threading
import time
import multiprocessing
import threading
import socketserver
import wx


class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, id=-1,
                          title="filetrans", size=wx.Size(480, 320))
        self.Bind(wx.EVT_CLOSE, self.c)

    def c(self, event):
        print("?")
        self.Destroy()


class MainApp(wx.App):
    def OnInit(self):
        self.frame = MainFrame()
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


if __name__ == "__main__":
    pass
