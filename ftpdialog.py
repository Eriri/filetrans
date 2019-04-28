from serverbase import *


class FtpDialog(Dialog):
    def __init__(self, app):
        Dialog.__init__(self, app, -1, "FD", (0, 0), (550, 70),
                        DEFAULT_FRAME_STYLE & ~(RESIZE_BORDER | MAXIMIZE_BOX), "ftp")
        self.SetIcon(app.icon), self.Center(BOTH)
        self.P, self.B = Panel(self), BoxSizer(HORIZONTAL)

        self.B.Add(StaticText(self.P, -1, "端口"), 1, EXPAND | ALL, 5)
        self.PORT = TextCtrl(self.P, -1, str(app.ftp_port))
        self.B.Add(self.PORT, 1, EXPAND | ALL, 5)

        self.B.Add(StaticText(self.P, -1, "路径"), 1, EXPAND | ALL, 5)
        self.PATH = TextCtrl(self.P, -1, str(app.ftp_path))
        self.B.Add(self.PATH, 1, EXPAND | ALL, 5)

        self.SB = Button(self.P, -1, "选择文件夹")
        self.Bind(EVT_BUTTON, self.select, self.SB)
        self.B.Add(self.SB, 1, EXPAND | ALL, 5)

        self.OK = Button(self.P, -1, "开启FTP服务器")
        self.Bind(EVT_BUTTON, self.click, self.OK)
        self.B.Add(self.OK, 1, EXPAND | ALL, 5)

        self.P.SetSizer(self.B)

    def select(self, event):
        fd = DirDialog(self, "选择文件夹", self.PATH.GetValue())
        if fd.ShowModal() == ID_OK:
            self.PATH.SetValue(fd.GetPath())

    def click(self, event):
        try:
            if not os.path.isdir(self.PATH.GetValue()) or int(self.PORT.GetValue()) >= 65536 or int(self.PORT.GetValue()) <= 0:
                raise Exception("请输入正确配置")
            self.GetParent().ftp_path = self.PATH.GetValue()
            self.GetParent().ftp_port = int(self.PORT.GetValue())
            self.SetReturnCode(ID_OK)
        except Exception as e:
            self.SetReturnCode(ID_ABORT)
            MessageBox(str(e))
        self.Destroy()
