from serverbase import *
import wx
import wx.adv


class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, app):
        wx.adv.TaskBarIcon.__init__(self)
        self.SetIcon(app.icon)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN,app.z_up)
        self.Bind(wx.adv.EVT_TASKBAR_RIGHT_DOWN,lambda e: self.PopupMenu())
        self.id_about, self.id_exit = wx.NewId(), wx.NewId()
        self.Bind(wx.EVT_MENU,app.about,id=self.id_about)
        self.Bind(wx.EVT_MENU,app.destroy,id=self.id_exit)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(self.id_about,"关于")
        menu.Append(self.id_exit,"退出")
        return menu

class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "C", (0, 0), (600, 400),
                         wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX), "c")
        self.path, self.prob, self.no, self.name = None, None, None, None
        self.tcp_server, self.client_tcp_port = None, DEFAULT_SERVER_TCP_PORT
        self.server_address, self.server_tcp_port = None, DEFAULT_SERVER_TCP_PORT
        self.udp_port = DEFAULT_UDP_PORT
        self.udp_server, self.verity_server= run_client_udp(self), run_client_verity(self)
        self.status = PROJECT_STATUS_OFF

        self.icon = wx.Icon("favicon.ico", wx.BITMAP_TYPE_ICO)
        self.taskbaricon = TaskBarIcon(self)
        self.SetIcon(self.icon), self.Center(wx.BOTH), self.SetMinSize((600, 400))
        self.Bind(wx.EVT_ICONIZE,self.z_down), self.Bind(wx.EVT_CLOSE,self.destroy)
        
        MB, M = wx.MenuBar(), wx.Menu()
        MB.Append(M, "选项"), self.SetMenuBar(MB)
        self.Bind(wx.EVT_MENU, self.select_server_tcp_port, M.Append(-1, "选择服务器TCP端口"))
        self.Bind(wx.EVT_MENU, self.select_client_tcp_port, M.Append(-1, "选择客户端TCP端口"))
        self.Bind(wx.EVT_MENU, self.select_udp_port, M.Append(-1, "选择UDP监听端口"))
        self.Bind(wx.EVT_MENU, self.about, M.Append(-1, "关于"))
        self.Bind(wx.EVT_MENU, self.destroy, M.Append(-1, "退出"))

        self.P, self.B = wx.Panel(self), wx.BoxSizer(wx.HORIZONTAL)
        self.PL, self.BL = wx.Panel(self.P), wx.BoxSizer(wx.VERTICAL)
        self.PR, self.BR = wx.Panel(self.P), wx.BoxSizer(wx.VERTICAL)

        self.NO_P, self.NO_B = wx.Panel(self.PL), wx.BoxSizer(wx.VERTICAL)
        self.NO_S, self.NO_T = wx.StaticText(self.NO_P,-1,"学号"), wx.TextCtrl(self.NO_P,-1)
        self.NO_B.Add(self.NO_S), self.NO_B.Add(self.NO_T), self.NO_P.SetSizer(self.NO_B)
        
        self.NAME_P, self.NAME_B = wx.Panel(self.PL), wx.BoxSizer(wx.VERTICAL)
        self.NAME_S, self.NAME_T = wx.StaticText(self.NAME_P,-1,"姓名"), wx.TextCtrl(self.NAME_P,-1)
        self.NAME_B.Add(self.NAME_S), self.NAME_B.Add(self.NAME_T), self.NAME_P.SetSizer(self.NAME_B)

        self.PATH_P, self.PATH_B = wx.Panel(self.PL), wx.BoxSizer(wx.VERTICAL)
        self.PATH_S, self.PATH_T, self.PATH_BT = wx.StaticText(self.PATH_P,-1,"工作目录"), wx.TextCtrl(self.PATH_P,-1), wx.Button(self.PATH_P,-1,"选择")
        self.PATH_B.Add(self.PATH_S), self.PATH_B.Add(self.PATH_T), self.PATH_B.Add(self.PATH_BT) self.PATH_P.SetSizer(self.PATH_B)
        self.Bind(wx.EVT_BUTTON, self.choose_dir, self.PATH_BT)

        self.NW_P, self.NW_B = wx.Panel(self.PR), wx.BoxSizer(wx.VERTICAL)
        self.NW_A, self.NW_S = wx.adv.AnimationCtrl(self.NW_P,-1), wx.StaticText(self.NW_P,-1)
        self.NW_B.Add(self.NW_A), self.NW_B.Add(self.NW_S), self.NW_P.SetSizer(self.NW_B)

        self.search_gif = wx.adv.Animation("search.gif", wx.adv.ANIMATION_TYPE_GIF)
        self.connected_gif = wx.adv.Animation("connected.gif", wx.adv.ANIMATION_TYPE_GIF)

        self.BT = wx.Button(self.PR,-1,"登录")
        self.Bind(wx.EVT_BUTTON, self.verity, self.BT)

        self.P.SetSizer(self.B)
        self.close()
    
    def open(self, event=None):
        pass

    def close(self, message=None):
        if message is not None:
            wx.MessageBox(message)
        if self.status == PROJECT_STATUS_ON:
            self.B.Clear(), self.SetSize(300,200)
            self.status = PROJECT_STATUS_OFF
            if self.tcp_server is not None:
                self.tcp_server.shutdown(), self.tcp_server.close()
                self.tcp_server = None
            self.path = self.prob = self.no = self.name = None
        self.B.Add(self.no)
        
    def fresh_prob(self, prob):
        self.prob = prob
    
    def fresh_verity_info(self, info, data):
        if info == CLIENT_SEARCH_SERVER:
            self.NW_A.Stop(), self.NW_A.SetAnimation(self.search_gif), self.NW_A.Play()
            self.NW_S.SetLabelText("连接中...")
        else:
            self.NW_A.Stop(), self.NW_A.SetAnimation(self.connected_gif), self.NW_A.Play()
            self.NW_S.SetLabelText(str(self.server_address))
    
    def verity(self, event=None):
        pass

    def z_up(self, event):
        self.Iconize(False), self.Show(False)

    def z_down(self, event):
        self.Iconize(True), self.Show(False)

    def about(self,event):
        wx.MessageBox("这是一个尚未完成的程序\n请尽可能保证各种路径中不含特殊标点字符")

    def destroy(self, event):
        self.Destroy(), self.taskbaricon.Destroy()
        



class MainApp(wx.App):
    def __init__(self):
        wx.App.__init__(self)
        self.mf = MainFrame()
        self.mf.Show(), self.SetTopWindow(self.mf)

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
