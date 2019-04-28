from serverbase import *

class MyTaskBarIcon(TaskBarIcon):
    def __init__(self, app):
        TaskBarIcon.__init__(self)
        self.SetIcon(app.icon)
        self.Bind(EVT_TASKBAR_LEFT_DOWN,app.z_up)
        self.Bind(EVT_TASKBAR_RIGHT_DOWN,lambda e: self.PopupMenu())
        self.id_about, self.id_exit = NewId(), NewId()
        self.Bind(EVT_MENU,app.about,id=self.id_about)
        self.Bind(EVT_MENU,app.destroy,id=self.id_exit)

    def CreatePopupMenu(self):
        menu = Menu()
        menu.Append(self.id_about,"关于")
        menu.Append(self.id_exit,"退出")
        return menu

class MainFrame(Frame):
    def __init__(self):
        Frame.__init__(self, None, -1, "C", (0, 0), (400, 150), DEFAULT_FRAME_STYLE & ~(RESIZE_BORDER | MAXIMIZE_BOX), "c")
        self.path, self.prob, self.no, self.name = None, None, None, None
        self.tcp_server, self.client_tcp_port = None, DEFAULT_SERVER_TCP_PORT
        self.server_address, self.server_tcp_port = None, DEFAULT_SERVER_TCP_PORT
        self.udp_port = DEFAULT_UDP_PORT
        self.udp_server, self.verity_server= run_client_udp(self), run_client_verity(self)
        self.status, self.network_status = PROJECT_STATUS_OFF, CLIENT_SEARCH_SERVER

        self.icon = Icon("favicon.ico", BITMAP_TYPE_ICO)
        self.taskbaricon = MyTaskBarIcon(self)
        self.SetIcon(self.icon), self.Center(BOTH)
        self.Bind(EVT_ICONIZE,self.z_down), self.Bind(EVT_CLOSE,self.destroy)
        
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

        self.NONAME_P, self.NONAME_B = Panel(self.PL), BoxSizer(HORIZONTAL)

        self.NO_S, self.NO_T = StaticText(self.NONAME_P,-1,"学号"), TextCtrl(self.NONAME_P,-1)
        self.NAME_S, self.NAME_T = StaticText(self.NONAME_P,-1,"姓名"), TextCtrl(self.NONAME_P,-1)

        self.NONAME_B.Add(self.NO_S,1,EXPAND|ALL,5), self.NONAME_B.Add(self.NO_T,1,EXPAND|ALL,5)
        self.NONAME_B.Add(self.NAME_S,1,EXPAND|ALL,5), self.NONAME_B.Add(self.NAME_T,1,EXPAND|ALL,5)
        self.NONAME_P.SetSizer(self.NONAME_B)

        self.PATH_P, self.PATH_B = Panel(self.PL), BoxSizer(HORIZONTAL)
        self.PATH_S, self.PATH_T, self.PATH_BT = StaticText(self.PATH_P,-1,"工作目录"), TextCtrl(self.PATH_P,-1), Button(self.PATH_P,-1,"选择")
        self.PATH_B.Add(self.PATH_S,1,EXPAND|ALL,5), self.PATH_B.Add(self.PATH_T,1,EXPAND|ALL,5), self.PATH_B.Add(self.PATH_BT,1,EXPAND|ALL,5)
        self.PATH_P.SetSizer(self.PATH_B)
        self.Bind(EVT_BUTTON, self.choose_dir, self.PATH_BT)

        self.BL.Add(self.NONAME_P,1,EXPAND|ALL,5),self.BL.Add(self.PATH_P,1,EXPAND|ALL,5)

        

        self.search_gif = Animation("search_s.gif", ANIMATION_TYPE_GIF)
        self.connected_gif = Animation("connected_s.gif", ANIMATION_TYPE_GIF)

        self.NW_S = StaticText(self.PR,-1)
        self.BT = Button(self.PR,-1,"登录")
        self.Bind(EVT_BUTTON, self.verity, self.BT)

        self.BR.Add(self.NW_S,1,EXPAND|ALL,5),self.BR.Add(self.BT,1,EXPAND|ALL,5)

        self.P.SetSizer(self.B), self.PL.SetSizer(self.BL), self.PR.SetSizer(self.BR)
        self.close()
    
    def open(self, event=None):
        pass

    def close(self, message=None):
        if message is not None:
            MessageBox(message)
        self.status = PROJECT_STATUS_OFF
        if self.tcp_server is not None:
            self.tcp_server.shutdown(), self.tcp_server.close()
            self.tcp_server = None
        self.path = self.prob = self.no = self.name = None
        self.B.Clear(), self.B.Add(self.PL,1,EXPAND), self.B.Add(self.PR,0,EXPAND)
        if self.network_status == CLIENT_SEARCH_SERVER:
            self.NW_S.SetLabelText("网络信息\n连接中...")
        else:
            self.NW_S.SetLabelText("网络信息\n地址："+str(self.server_address))
        self.SetSize(400,150), self.Show(True)
        
    def fresh_prob(self, prob):
        self.prob = prob
    
    def fresh_verity_info(self, info, data):
        self.network_status = info
        if info == CLIENT_SEARCH_SERVER:
            self.NW_S.SetLabelText("网络信息\n连接中...")
        else:
            self.NW_S.SetLabelText("网络信息\n地址："+str(self.server_address))

    def verity(self, event=None):
        pass

    def choose_dir(self, event):
        pass

    def select_server_tcp_port(self, event):
        pass
    
    def select_client_tcp_port(self, event):
        pass
    
    def select_udp_port(self, event):
        pass

    def z_up(self, event):
        self.Iconize(False), self.Show(False)

    def z_down(self, event):
        self.Iconize(True), self.Show(False)

    def about(self,event):
        MessageBox("这是一个尚未完成的程序\n请尽可能保证各种路径中不含特殊标点字符")

    def destroy(self, event):
        self.Destroy(), self.taskbaricon.Destroy()
        



class MainApp(App):
    def __init__(self):
        App.__init__(self)
        self.mf = MainFrame()
        self.mf.Show(), self.SetTopWindow(self.mf)

    def OnInit(self):
        self._check = SingleInstanceChecker(GetUserId())
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
