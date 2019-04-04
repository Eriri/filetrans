import sys
import wx
from serverbase import *
from sql import *
from wx import *
from ObjectListView import ObjectListView, ColumnDefn
from sf import StudentFrame
from pf import ProblemFrame
from utilities import MainModel

local_address = "127.0.0.1"
server_port,client_port = 8080,9090
proj_path, proj_ss, proj_db,prob_path = None, None, None, None


class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title="filetrans", size=(570, 380),
                          style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.Center(wx.BOTH)
        self.Bind(wx.EVT_CLOSE, self.destroy)

        MB, ME, ELSE = wx.MenuBar(), wx.Menu(), wx.Menu()
        MB.Append(ME, "工作区"), MB.Append(ELSE, "其他选项")

        open_ = ME.Append(-1, "打开工作区...")
        self.Bind(wx.EVT_MENU, self.open_proj, open_)
        close_ = ME.Append(-1, "关闭当前工作区")
        self.Bind(wx.EVT_MENU, self.close_proj, close_)
        exit_ = ME.Append(-1, "退出")
        self.Bind(wx.EVT_MENU, self.destroy, exit_)

        change_server_port_ = ELSE.Append(-1, "选择服务器端口")
        self.Bind(EVT_MENU, self.change_sp, change_server_port_)

        change_client_port_ = ELSE.Append(-1, "选择客户端端口")
        self.Bind(EVT_MENU, self.change_cp, change_client_port_)

        about_ = ELSE.Append(-1, "关于")
        self.Bind(wx.EVT_MENU, self.about, about_)

        self.SetMenuBar(MB)

        Bs = wx.Button(parent=self, label="学生管理",
                       size=(120, 60), pos=(420, 10))
        self.Bind(wx.EVT_BUTTON, lambda e: self.add_mf("S"), Bs)

        Bp = wx.Button(parent=self, label="题目管理",
                       size=(120, 60), pos=(420, 90))
        self.Bind(wx.EVT_BUTTON, lambda e: self.add_mf("P"), Bp)

        Bw = wx.Button(parent=self, label="接收作业",
                       size=(120, 60), pos=(420, 170))
        self.Bind(wx.EVT_BUTTON, lambda e: self.add_mf("W"), Bw)

        Bt = wx.Button(parent=self, label="系统评测",
                       size=(120, 60), pos=(420, 250))

        self.Buttons = [Bs, Bp, Bw, Bt]
        for b in self.Buttons:
            b.Show(True), b.Disable()

        self.OLV = ObjectListView(parent=self, pos=(10, 10), size=(400, 300),
                                  sortable=True, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.OLV.SetColumns([
            ColumnDefn("学号", "left", 100, "Id"),
            ColumnDefn("姓名", "left", 80, "name"),
            ColumnDefn("登陆时间", "left", 100, "ctime"),
            ColumnDefn("提交情况", "left", 100, "ws"),
            ColumnDefn("登录密码", "left", 100, "pwd")
        ])
        self.OLV.SetEmptyListMsg("")

    def destroy(self, event):
        if proj_ss is not None:
            try:
                proj_ss.shutdown()
                proj_ss.server_close()
            except Exception as e:
                pass
        self.Destroy()

    def open_proj(self, event=None):
        dd = wx.DirDialog(parent=self, message="选择工作区文件夹",
                          defaultPath=sys.path[0])
        if dd.ShowModal() == wx.ID_OK:
            global proj_path, proj_ss, proj_db, prob_path
            if proj_path is not None:
                self.close_proj()
            proj_path = dd.GetPath()
            proj_db = init_db(proj_path)
            if not os.path.isdir(os.path.join(proj_path,"problems")):
                os.mkdir(os.path.join(proj_path,"problems"))
            prob_path = os.path.join(proj_path,"problems")
            try:
                proj_ss = run_ss(local_address, server_port, proj_db)
                for b in self.Buttons:
                    b.Enable()
            except Exception as e:
                md = wx.MessageDialog(self, message=str(e))
                if md.ShowModal() == wx.ID_OK:
                    pass
            self.update_olv()

    def close_proj(self, event=None):
        global proj_path, proj_ss
        if proj_path is not None:
            proj_path = None
            if proj_ss is not None:
                try:
                    proj_ss.shutdown()
                    proj_ss.server_close()
                except Exception as e:
                    pass
            for b in self.Buttons:
                b.Disable()
            self.OLV.DeleteAllItems()

    def change_sp(self, event):
        global proj_ss, server_port
        ted = wx.TextEntryDialog(
            self, "监听端口（0~65535）", "选择服务器端口", str(server_port))
        if ted.ShowModal() == wx.ID_OK:
            port = ted.GetValue()
            if str.isdigit(port) and int(port) < 65536:
                pre_port = server_port
                server_port = int(port)
                if proj_path is not None:
                    if proj_ss is not None:
                        try:
                            proj_ss.shutdown()
                            proj_ss.server_close()
                        except Exception as e:
                            pass
                    try:
                        proj_ss = run_ss(local_address, server_port, proj_db)
                    except Exception as e:
                        server_port = pre_port
                        md = wx.MessageDialog(self, message=str(e))
                        if md.ShowModal() == wx.ID_OK:
                            pass
            else:
                md = wx.MessageDialog(self,message="请输入正确端口")
                if md.ShowModal() == wx.ID_OK:
                    pass

    def change_cp(self, event):
        global client_port
        ted = wx.TextEntryDialog(
            self, "监听端口（0~65535）", "选择客户端端口", str(server_port))
        if ted.ShowModal() == wx.ID_OK:
            port = ted.GetValue()
            if str.isdigit(port) and int(port) < 65536:
                pre_port = client_port
                client_port = int(port)
            else:
                md = wx.MessageDialog(self, message="请输入正确端口")
                if md.ShowModal() == wx.ID_OK:
                    pass

    def about(self, event):
        msg = wx.MessageBox(message="这是一个尚未完成的程序")

    def update_olv(self, event=None):
        con, cur = open_db(proj_db)
        probs = [x[0] for x in select_all(cur, "problem_info", ["id"])]
        items = select_all(cur, "user_info", ["*"])
        close_db(con, cur)
        models = []
        for item in items:
            models.append(MainModel(item[0], item[1], item[2], item[3], probs, proj_path))
        self.OLV.DeleteAllItems()
        self.OLV.AddObjects(models)

    def add_mf(self, T):
        if T == "S":
            MF = StudentFrame(self, proj_path, proj_db).Show()
        if T == "P":
            MF = ProblemFrame(self, prob_path, proj_db).Show()
        if T == "W":
            MF = WorkFrame(self).Show()


class WorkFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent=parent, title="学生管理", size=(
            640, 400), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.Bind(wx.EVT_CLOSE, self.destroy)

    def destroy(self, event):
        self.Show(False)
        self.GetParent().Thaw()
        self.GetParent().update_olv()


class MainApp(wx.App):
    def __init__(self):
        wx.App.__init__(self)
        self.frame = MainFrame()
        self.frame.Show()
        self.SetTopWindow(self.frame)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = MainApp()
    app.MainLoop()
