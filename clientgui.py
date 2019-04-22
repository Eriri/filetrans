from serverbase import *
import sys
import wx


class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "C")







class MainApp(wx.App):
    def __init__(self):
        wx.App.__init__(self)
        self.mf = MainFrame()
        self.mf.Show()
        self.SetTopWindow(self.mf)


if __name__ == "__main__":
    app = wx.App()
