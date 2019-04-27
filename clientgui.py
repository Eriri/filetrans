from serverbase import *
import wx


class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "C", (0, 0), (600, 400), wx.DEFAULT_FRAME_STYLE, "c")
        self.path,
        self.no, self.name


        self.icon = wx.Icon()
        self.icon.CopyFromBitmap(wx.Bitmap("favicon.bmp", wx.BITMAP_TYPE_ANY))
        self.SetIcon(self.icon), self.Center(wx.BOTH), self.SetMinSize((600, 400))


class MainApp(wx.App):
    def __init__(self):
        wx.App.__init__(self)
        self.mf = MainFrame()
        self.mf.Show()
        self.SetTopWindow(self.mf)
        print(self._check)

    def OnInit(self):
        self._check = wx.SingleInstanceChecker(wx.GetUserId())
        if self._check.IsAnotherRunning():
            wx.MessageBox("已经运行")
            return False
        return True

    def OnExit(self):
        del self._check
        return True


if __name__ == "__main__":
   app = MainApp()
   app.MainLoop()
