from serverbase import *
from sql import *
from wx import *
import sys
import threading
import wx
from ObjectListView import ObjectListView, ColumnDefn

local_address = "127.0.0.1"
server_port = 8080
client_port = 9090
proj_path, proj_ss, proj_db = None, None, None


class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title="filetrans",
                          size=(640, 400), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.Bind(wx.EVT_CLOSE, self.destroy)

        MB, ME, ELSE = wx.MenuBar(), wx.Menu(), wx.Menu()
        MB.Append(ME, "工作区"), MB.Append(ELSE, "其他")
        open_ = ME.Append(-1, "打开工作区...")
        self.Bind(wx.EVT_MENU, self.open_proj, open_)
        close_ = ME.Append(-1, "关闭当前工作区")
        self.Bind(wx.EVT_MENU, self.close_proj, close_)
        exit_ = ME.Append(-1, "退出")
        self.Bind(wx.EVT_MENU, self.destroy, exit_)
        about_ = ELSE.Append(-1, "关于")
        self.Bind(wx.EVT_MENU, self.about, about_)

        self.SetMenuBar(MB)
        self.Bs = wx.Button(parent=self, label="学生管理",
                            size=(120, 60), pos=(460, 20))
        self.Bp = wx.Button(parent=self, label="题目管理",
                            size=(120, 60), pos=(460, 100))
        self.Bw = wx.Button(parent=self, label="作业管理",
                            size=(120, 60), pos=(460, 180))
        self.Bt = wx.Button(parent=self, label="系统评测",
                            size=(120, 60), pos=(460, 260))
        self.Buttons = [self.Bs, self.Bp, self.Bw, self.Bt]
        for b in self.Buttons:
            b.Show(True), b.Disable()

        self.OLV = ObjectListView(parent=self, pos=(20, 20), size=(400, 300),
                                  sortable=True, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.OLV.SetColumns([
            ColumnDefn("学号", "left", 120, "Id"),
            ColumnDefn("姓名", "left", 120, "name"),
            ColumnDefn("登陆时间", "left", 120, "ctime"),
            ColumnDefn("提交情况", "left", 120, "ws"),
            ColumnDefn("登录密码", "left", 120, "pwd")
        ])
        self.OLV.SetEmptyListMsg("")
        self.OLV.Show(True)

    def destroy(self, event):
        global proj_path, proj_ss
        if proj_path != None:
            proj_ss.shutdown()
        self.Destroy()

    def open_proj(self, event=None):
        dd = wx.DirDialog(parent=self, message="选择工作区文件夹",
                          defaultPath=sys.path[0])
        if dd.ShowModal() == wx.ID_OK:
            global proj_path, proj_ss, proj_db
            if proj_path != None:
                self.close_proj()
            proj_path = dd.GetPath()
            proj_db = init_db(proj_path)
            proj_ss = run_ss(local_address, server_port, proj_db)
            for b in self.Buttons:
                b.Enable()
            self.update_olv()

    def close_proj(self, event=None):
        global proj_path, proj_ss
        if proj_path != None:
            proj_path = None
            proj_ss.server_close()
            proj_ss.shutdown()
            for b in self.Buttons:
                b.Disable()
            self.OLV.DeleteAllItems()

    def about(self, event):
        msg = wx.MessageBox(message="这是一个尚未完成的程序")

    def update_olv(self, event=None):
        con, cur = open_db(proj_db)
        probs = [x[0] for x in select_all(cur, "problem_info", ["id"])]
        items = gen_models(probs, select_all(cur, "user_info", ["*"]))
        close_db(con, cur)
        self.OLV.DeleteAllItems()
        self.OLV.AddObjects(items)


def gen_models(probs, items):
    models = []
    for item in items:
        models.append(MainModel(item[0], item[1], item[2], item[3], probs))
    return models


class MainModel(object):
    def __init__(self, Id, name, pwd, ctime, probs):
        self.Id = Id
        self.name = name
        self.pwd = pwd
        self.ctime = ctime
        for i in range(len(probs)):
            if os.path.isfile(os.path.join(proj_path, Id, probs[i])) == False:
                probs[i] = "□"*len(probs[i])
        self.ws = "|".join(probs)


class StudentFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent=parent, title="学生管理")


class MainApp(wx.App):
    def OnInit(self):
        self.frame = MainFrame()
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = MainApp()
    app.MainLoop()
