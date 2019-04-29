from serverbase import *

from studentdialog import StudentDialog
from problemdialog import ProblemDialog
from workdialog import WorkDialog
from senddialog import SendDialog
from ftpdialog import FtpDialog


class MainFrame(Frame):
    def __init__(self):
        Frame.__init__(self, None, -1, "FTServer", (0, 0), (600, 400), DEFAULT_FRAME_STYLE, "ft")
        self.path, self.database, self.work_dir, self.prob_dir = None, None, None, None
        self.server_tcp_port, self.client_tcp_port, self.tcp_server = DEFAULT_SERVER_TCP_PORT, DEFAULT_CLIENT_TCP_PORT, None
        self.udp_port, self.udp_server = DEFAULT_UDP_PORT, None
        self.ftp_path, self.ftp_port, self.ftp_server = "", DEFAULT_FTP_PORT, None
        self.prob, self.lang = [], LANGUAGE_CONFIG
        self.status = PROJECT_STATUS_OFF
        self.SD = set()
        os.chdir(getattr(sys, '_MEIPASS', os.getcwd()))
        self.icon = Icon(os.path.join(os.path.abspath("."),"favicon.ico"), BITMAP_TYPE_ICO)
        self.SetIcon(self.icon), self.Center(BOTH), self.SetMinSize((600, 400))

        MB, ME, ELSE = MenuBar(), Menu(), Menu()
        MB.Append(ME, "工作区"), MB.Append(ELSE, "其他选项"), self.SetMenuBar(MB)

        self.Bind(EVT_MENU, self.open, ME.Append(-1, "打开工作区..."))
        self.Bind(EVT_MENU, self.close, ME.Append(-1, "关闭当前工作区"))
        self.Bind(EVT_MENU, self.destroy, ME.Append(-1, "退出"))
        self.Bind(EVT_MENU, self.select_server_tcp_port, ELSE.Append(-1, "选择服务器TCP端口"))
        self.Bind(EVT_MENU, self.select_client_tcp_port, ELSE.Append(-1, "选择客户端TCP端口"))
        self.Bind(EVT_MENU, self.select_udp_port, ELSE.Append(-1, "选择UDP广播端口"))
        self.Bind(EVT_MENU, self.start_ftp_server, ELSE.Append(-1, "开启FTP服务器"))
        self.Bind(EVT_MENU, self.close_ftp_server, ELSE.Append(-1, "关闭FTP服务器"))
        self.Bind(EVT_MENU, self.select_extension, ELSE.Append(-1, "程序扩展名设置"))
        self.Bind(EVT_MENU, self.about, ELSE.Append(-1, "关于/帮助"))

        self.P, self.B = Panel(self), BoxSizer(HORIZONTAL)
        self.PR, self.BR = Panel(self.P), BoxSizer(VERTICAL)

        self.OLV = ObjectListView(parent=self.P, sortable=True, style=LC_REPORT)
        self.OLV.SetColumns([
            ColumnDefn("学号", "left", 100, "no"),
            ColumnDefn("姓名", "left", 100, "name"),
            ColumnDefn("提交情况", "left", 100, "prob"),
            ColumnDefn("IP地址", "left", 175, "ip"),
            ColumnDefn("最终成绩", "left", 100, "point")])

        B = [Button(self.PR, 0, "学生管理"), Button(self.PR, 1, "题目管理"),
             Button(self.PR, 2, "接收作业"), Button(self.PR, 3, "发送文件"),
             Button(self.PR, 4, "系统评测")]
        for b in B:
            self.BR.Add(b, 0, EXPAND | ALL, 5), self.Bind(EVT_BUTTON, self.button_func, b)
        self.PR.SetSizer(self.BR)
        self.B.Add(self.OLV, 1, EXPAND | ALL, 5)
        self.B.Add(self.PR, 0)
        self.P.SetSizer(self.B),self.PR.Disable()

    def destroy(self, event):
        self.close(), self.Destroy()

    def open(self, event=None):
        try:
            dd = DirDialog(self, "选择工作区文件夹")
            if dd.ShowModal() == ID_OK:
                self.close()
                self.path, self.database = dd.GetPath(), initiate(dd.GetPath())
                self.tcp_server, self.udp_server = run_server_tcp(self), run_server_udp(self)
                if not os.path.isdir(os.path.join(self.path, DEFAULT_WORK_DIR)):
                    os.mkdir(os.path.join(self.path, DEFAULT_WORK_DIR))
                if not os.path.isdir(os.path.join(self.path, DEFAULT_PROBLEM_DIR)):
                    os.mkdir(os.path.join(self.path, DEFAULT_PROBLEM_DIR))
                self.work_dir = os.path.join(self.path, DEFAULT_WORK_DIR)
                self.prob_dir = os.path.join(self.path, DEFAULT_PROBLEM_DIR)
                self.status = PROJECT_STATUS_ON
                self.init_all(), self.PR.Enable()
        except Exception as e:
            MessageBox(str(e))

    def close(self, event=None):
        try:
            if self.status is PROJECT_STATUS_ON:
                self.tcp_server.shutdown(), self.tcp_server.server_close()
                self.udp_server.shutdown()
                if self.ftp_server is not None:
                    self.ftp_server.close_all()
                self.path = self.database = self.work_dir = None
                self.tcp_server = self.udp_server = self.ftp_server = None
                self.OLV.DeleteAllItems(), self.PR.Disable(), self.SD.clear()
                self.status = PROJECT_STATUS_OFF
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
                if self.tcp_server is not None:
                    self.tcp_server.shutdown(), self.tcp_server.server_close()
                    self.tcp_server = run_server_tcp(self)
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
        except Exception as e:
            MessageBox(str(e))

    def select_udp_port(self, event):
        try:
            ted = TextEntryDialog(self, "广播端口（0~65535）", "选择UDP广播端口", str(self.udp_port))
            if ted.ShowModal() == ID_OK:
                port = ted.GetValue()
                if int(port) >= 65536 or int(port) <= 0:
                    raise Exception("请输入正确端口")
                self.udp_port = int(port)
                if self.udp_server is not None:
                    self.udp_server.shutdown()
                    self.udp_server = run_server_udp(self)
        except Exception as e:
            MessageBox(str(e))

    def start_ftp_server(self, event=None):
        self.close_ftp_server()
        if FtpDialog(self).ShowModal() == ID_OK:
            self.ftp_server = run_server_ftp(self)

    def close_ftp_server(self, event=None):
        if self.ftp_server is not None:
            self.ftp_server.close_all()
            self.ftp_server = None

    def select_extension(self, event=None):
        md = MultiChoiceDialog(self,"选择允许的程序类型","确认",LANGUAGE_CONFIG)
        md.SetIcon(self.GetIcon()), md.SetSelections([LANGUAGE_CONFIG.index(x) for x in self.lang])
        if md.ShowModal() == ID_OK:
            self.lang = [LANGUAGE_CONFIG[x] for x in md.GetSelections()]
            if self.status == PROJECT_STATUS_ON:
                self.fresh_prob()

    def about(self, event):
        msg = MessageBox("这是一个尚未完成的程序\n请尽可能保证各种路径中不含特殊标点字符\n请尽可能保证收发文件时文件处于关闭状态")

    def init_all(self, event=None):
        connection = connect(self.database)
        self.prob = [x[0] for x in select(connection, "problem", ["no"])]
        user = select(connection, "user", ["no", "name", "ip", "point"])
        connection.close()
        self.OLV.DeleteAllItems()
        for no, name, ip, point in user:
            self.OLV.AddObject(Model(no, name, self.prob, ip, point, self.work_dir, self.lang))
            self.SD.add(no)

    def fresh_prob(self):
        connection = connect(self.database)
        self.prob = [x[0] for x in select(connection,"problem",["no"])]
        connection.close()
        obj = self.OLV.GetObjects()
        for o in obj:
            o.fresh_prob(self.prob, self.lang)
        self.OLV.RefreshObjects(obj)

    def update(self, nos):
        connection = connect(self.database)
        for no in nos:
            name, ip, point = select_one(connection, "user", ["name", "ip", "point"], ["no"], [no])
            self.OLV.RefreshObject(Model(no, name, self.prob, ip, point, self.work_dir, self.lang))

    def add(self, nos):
        connection = connect(self.database)
        for no in nos:
            name, ip, point = select_one(connection, "user", ["name", "ip", "point"], ["no"], [no])
            obj = Model(no, name, self.prob, ip, point, self.work_dir, self.lang)
            if no in self.SD:
                self.OLV.RefreshObject(obj)
            else:
                self.OLV.AddObject(obj)
                self.SD.add(no)
        connection.close()

    def delete(self, nos):
        for no in nos:
            self.OLV.RemoveObject(Model(no, path=self.work_dir))
            self.SD.remove(no)

    def button_func(self, event):
        if self.status is PROJECT_STATUS_ON:
            if event.GetId() == 0:
                StudentDialog(self).ShowModal()
            elif event.GetId() == 1:
                ProblemDialog(self).ShowModal(), self.fresh_prob()
            elif event.GetId() == 2:
                WorkDialog(self).ShowModal(), self.fresh_prob()
            elif event.GetId() == 3:
                SendDialog(self).ShowModal()
            elif event.GetId() == 4:
                pass
                #JudgeDialog(self).ShowModel, self.fresh_point()


class MainApp(App):
    def __init__(self):
        App.__init__(self)
        self.frame = MainFrame()
        self.frame.Show()
        self.SetTopWindow(self.frame)

    def OnInit(self):
        self._check = SingleInstanceChecker("Server"+GetUserId())
        if self._check.IsAnotherRunning():
            MessageBox("已经运行")
            return False
        return True

    def OnExit(self):
        del self._check
        return True


if __name__ == "__main__":
    MainApp().MainLoop()
