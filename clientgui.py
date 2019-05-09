from serverbase import *


class MyTaskBarIcon(TaskBarIcon):
    def __init__(self, app):
        TaskBarIcon.__init__(self)
        self.SetIcon(app.icon)
        self.Bind(EVT_TASKBAR_LEFT_DOWN, app.z_up)
        self.Bind(EVT_TASKBAR_RIGHT_DOWN, self.pop)
        self.id_about, self.id_exit = NewId(), NewId()
        self.Bind(EVT_MENU, app.about, id=self.id_about)
        self.Bind(EVT_MENU, app.destroy, id=self.id_exit)

    def CreatePopupMenu(self):
        menu = Menu()
        menu.Append(self.id_about, "关于")
        menu.Append(self.id_exit, "退出")
        return menu

    def pop(self, event):
        self.PopupMenu(self.CreatePopupMenu())


class MainFrame(Frame):
    def __init__(self):
        Frame.__init__(self, None, -1, "FTClient", (0, 0), (450, 130), DEFAULT_FRAME_STYLE, "c")
        self.path, self.prob, self.lang, self.no, self.name = None, [], [], None, None
        self.tcp_server, self.client_tcp_port = None, DEFAULT_CLIENT_TCP_PORT
        self.server_address, self.server_tcp_port = None, DEFAULT_SERVER_TCP_PORT
        self.udp_port = DEFAULT_UDP_PORT
        self.udp_server, self.verity_server = run_client_udp(self), run_client_verity(self)
        self.status, self.network_status = PROJECT_STATUS_OFF, CLIENT_SEARCH_SERVER

        os.chdir(getattr(sys, '_MEIPASS', os.getcwd()))
        self.icon = Icon("favicon.ico", BITMAP_TYPE_ICO)
        self.taskbaricon = MyTaskBarIcon(self)
        self.SetIcon(self.icon), self.Center(BOTH)
        self.Bind(EVT_ICONIZE, self.z_down), self.Bind(EVT_CLOSE, self.destroy)

        MB, M = MenuBar(), Menu()
        MB.Append(M, "选项"), self.SetMenuBar(MB)
        self.Bind(EVT_MENU, self.select_server_tcp_port, M.Append(-1, "选择服务器TCP端口"))
        self.Bind(EVT_MENU, self.select_client_tcp_port, M.Append(-1, "选择客户端TCP端口"))
        self.Bind(EVT_MENU, self.select_udp_port, M.Append(-1, "选择UDP监听端口"))
        self.Bind(EVT_MENU, self.about, M.Append(-1, "关于"))
        self.Bind(EVT_MENU, self.destroy, M.Append(-1, "退出"))

        self.P, self.B = Panel(self), BoxSizer(HORIZONTAL)
        self.PL, self.BL = Panel(self.P), BoxSizer(VERTICAL)
        self.PR, self.BR = Panel(self.P), BoxSizer(VERTICAL)
        self.P.SetSizer(self.B), self.PL.SetSizer(self.BL), self.PR.SetSizer(self.BR)

        self.NONAME_P, self.NONAME_B = Panel(self.PL), BoxSizer(HORIZONTAL)
        self.NO_S, self.NO_T = StaticText(self.NONAME_P, -1, "学号"), TextCtrl(self.NONAME_P, -1)
        self.NAME_S, self.NAME_T = StaticText(self.NONAME_P, -1, "姓名"), TextCtrl(self.NONAME_P, -1)
        self.NONAME_B.Add(self.NO_S, 1, EXPAND | ALL, 5), self.NONAME_B.Add(self.NO_T, 1, EXPAND | ALL, 5)
        self.NONAME_B.Add(self.NAME_S, 1, EXPAND | ALL, 5), self.NONAME_B.Add(self.NAME_T, 1, EXPAND | ALL, 5)
        self.NONAME_P.SetSizer(self.NONAME_B)

        self.PATH_P, self.PATH_B = Panel(self.PL), BoxSizer(HORIZONTAL)
        self.PATH_S, self.PATH_T, self.PATH_BT = StaticText(self.PATH_P, -1, "工作目录"), TextCtrl(self.PATH_P, -1), Button(self.PATH_P, -1, "选择")
        self.PATH_B.Add(self.PATH_S, 1, EXPAND | ALL, 5), self.PATH_B.Add(self.PATH_T, 1, EXPAND | ALL, 5), self.PATH_B.Add(self.PATH_BT, 1, EXPAND | ALL, 5)
        self.PATH_P.SetSizer(self.PATH_B)
        self.Bind(EVT_BUTTON, self.choose_dir, self.PATH_BT)

        self.NW_S = StaticText(self.PR, -1)
        self.BT = Button(self.PR, -1, "登录")
        self.Bind(EVT_BUTTON, self.open, self.BT)

        self.BL.Add(self.NONAME_P, 1, EXPAND), self.BL.Add(self.PATH_P, 1, EXPAND)
        self.BR.Add(self.NW_S, 1, EXPAND | ALL, 5), self.BR.Add(self.BT, 1, EXPAND | ALL, 5)

        self.PAL = ObjectListView(parent=self.P, style=LC_REPORT)
        self.PAL.SetColumns([ColumnDefn("题目信息", "left", 200, "info")])
        self.FE = ObjectListView(parent=self.P, style=LC_REPORT)
        self.FE.SetColumns([ColumnDefn("文件信息", "left", 200, "info")])

        self.close()

    def open(self, event=None):
        if not os.path.isdir(self.PATH_T.GetValue()) or self.NO_T.GetValue() == "" or self.PATH_T.GetValue() == "":
            MessageBox("请输入正确登录信息与文件夹")
        else:
            self.no, self.name, self.path, info = self.NO_T.GetValue(), self.NAME_T.GetValue(), self.PATH_T.GetValue(), None
            if os.path.isfile(os.path.join(self.path, DEFAULT_LOG_INFO)):
                with open(os.path.join(self.path, DEFAULT_LOG_INFO), "rb") as f:
                    if f.read() == base64.b64encode((self.no+self.name).encode()):
                        info = CLIENT_VERITY_SUCCEED
            if info is None:
                info = verity_user(self)
            if info == CLIENT_VERITY_SUCCEED:
                self.status, self.tcp_server = PROJECT_STATUS_ON, run_client_tcp(self)
                self.PAL.Show(True), self.FE.Show(True), self.PL.Show(False), self.PR.Show(False)
                self.B.Clear(), self.B.Add(self.PAL, 1, EXPAND | ALL, 5), self.B.Add(self.FE, 1, EXPAND | ALL, 5)
                self.SetSize(500, 300)
                with open(os.path.join(self.path, DEFAULT_LOG_INFO), "wb") as f:
                    f.write(base64.b64encode((self.no+self.name).encode()))
            elif info == CLIENT_VERITY_FAILED:
                MessageBox("登录信息错误")
            elif info == CLIENT_SEARCH_SERVER:
                MessageBox("无法连接到服务器")

    def close(self, message=None):
        if message is not None:
            MessageBox(message)
            os.remove(os.path.join(self.path, DEFAULT_LOG_INFO))
        if self.tcp_server is not None:
            self.tcp_server.shutdown(), self.tcp_server.server_close()
        self.status, self.tcp_server = PROJECT_STATUS_OFF, None
        self.path, self.no, self.name, self.prob, self.lang = None, None, None, [], []
        self.fresh_server_info(self.network_status)
        self.PAL.Show(False), self.FE.Show(False), self.PL.Show(True), self.PR.Show(True)
        self.B.Clear(), self.B.Add(self.PL, 1, EXPAND), self.B.Add(self.PR, 0, EXPAND)
        self.SetSize(450, 130), self.Show(True)

    def fresh_prob_lang(self, prob=None, lang=None):
        if prob is not None and lang is not None:
            self.prob, self.lang = prob, lang
        if self.status == PROJECT_STATUS_ON:
            self.PAL.DeleteAllItems(), self.FE.DeleteAllItems()
            for p in self.prob:
                self.PAL.AddObject({"info": "题目：" + str(p)})
            self.PAL.AddObject({"info": "允许语言类型：" + str(self.lang)})
            cand = list(chain.from_iterable([[no + su for su in self.lang] for no in self.prob]))
            for name in cand:
                if os.path.isfile(os.path.join(self.path, name)):
                    self.FE.AddObject({"info": name})

    def show_info(self, info, data, error=None):
        if error is not None:
            MessageBox(info + str(data) + error)
        else:
            MessageBox(info + str(data))

    def fresh_server_info(self, info):
        self.network_status = info
        if info == CLIENT_SEARCH_SERVER:
            self.NW_S.SetLabelText("服务器IP:连接中...................")
        else:
            self.NW_S.SetLabelText("服务器IP:" + str(self.server_address))

    def choose_dir(self, event):
        try:
            dd = DirDialog(self, "选择文件夹")
            if dd.ShowModal() == ID_OK:
                self.PATH_T.SetValue(dd.GetPath())
        except Exception as e:
            MessageBox(str(e))

    def select_server_tcp_port(self, event):
        try:
            ted = TextEntryDialog(self, "监听端口（0~65535）", "选择服务器端口", str(self.server_tcp_port))
            if ted.ShowModal() == ID_OK:
                port = ted.GetValue()
                if int(port) >= 65536 or int(port) <= 0:
                    raise Exception("请输入正确端口")
                self.server_tcp_port = int(port)
        except Exception as e:
            MessageBox(str(e))

    def select_client_tcp_port(self, event):
        try:
            ted = TextEntryDialog(self, "监听端口（0~65535）", "选择客户端端口", str(self.client_tcp_port))
            if ted.ShowModal() == ID_OK:
                port = ted.GetValue()
                if int(port) >= 65536 or int(port) <= 0:
                    raise Exception("请输入正确端口")
                self.client_tcp_port = int(port)
                if self.tcp_server is not None:
                    self.tcp_server.shutdown(), self.tcp_server.server_close()
                    self.tcp_server = run_client_tcp(self)
        except Exception as e:
            MessageBox(str(e))

    def select_udp_port(self, event):
        try:
            ted = TextEntryDialog(self, "广播端口（0~65535）", "选择UDP监听端口", str(self.udp_port))
            if ted.ShowModal() == ID_OK:
                port = ted.GetValue()
                if int(port) >= 65536 or int(port) <= 0:
                    raise Exception("请输入正确端口")
                self.udp_port = int(port)
                if self.udp_server is not None:
                    self.udp_server.shutdown(), self.udp_server.server_close()
                    self.udp_server = run_client_udp(self)
        except Exception as e:
            MessageBox(str(e))

    def z_up(self, event):
        self.Iconize(False), self.Show(True)

    def z_down(self, event):
        self.Iconize(True), self.Show(False)

    def about(self, event):
        MessageBox("这是一个尚未完成的程序\n请尽可能保证各种路径中不含特殊标点字符\n请尽可能保证收发文件时文件处于关闭状态")

    def destroy(self, event):
        self.close()
        self.udp_server.shutdown(), self.udp_server.server_close()
        self.verity_server.shutdown()
        self.Destroy(), self.taskbaricon.Destroy()


class MainApp(App):
    def __init__(self):
        App.__init__(self)
        self.mf = MainFrame()
        self.mf.Show(), self.SetTopWindow(self.mf)

    def OnInit(self):
        self._check = SingleInstanceChecker("Client"+GetUserId())
        if self._check.IsAnotherRunning():
            MessageBox("已经运行")
            return False
        return True

    def OnExit(self):
        del self._check
        return True


if __name__ == "__main__":
    app = MainApp()
    app.MainLoop()
