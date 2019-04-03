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
        wx.Frame.__init__(self, parent=None, title="filetrans", size=(570, 380),
                          style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.Bind(wx.EVT_CLOSE, self.destroy)

        PMF = ProblemFrame(parent=self)
        WMF = WorkFrame(parent=self)
        PMF.Show(False), WMF.Show(False)

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

        Bs = wx.Button(parent=self, label="学生管理", size=(120, 60), pos=(420, 10))
        self.Bind(wx.EVT_BUTTON, lambda e: self.add_mf("S"), Bs)

        Bp = wx.Button(parent=self, label="题目管理", size=(120, 60), pos=(420, 90))
        self.Bind(wx.EVT_BUTTON, lambda e: (PMF.Show(True), self.Freeze()), Bp)

        Bw = wx.Button(parent=self, label="作业管理", size=(120, 60), pos=(420, 170))
        self.Bind(wx.EVT_BUTTON, lambda e: (WMF.Show(True), self.Freeze()), Bw)

        Bt = wx.Button(parent=self, label="系统评测", size=(120, 60), pos=(420, 250))

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
        global proj_path, proj_ss
        if proj_path is not None:
            proj_ss.shutdown()
            proj_ss.server_close()
        self.Destroy()

    def open_proj(self, event=None):
        dd = wx.DirDialog(parent=self, message="选择工作区文件夹", defaultPath=sys.path[0])
        if dd.ShowModal() == wx.ID_OK:
            global proj_path, proj_ss, proj_db
            if proj_path is not None:
                self.close_proj()
            proj_path = dd.GetPath()
            proj_db = init_db(proj_path)
            try:
                proj_ss = run_ss(local_address, server_port, proj_db)
                for b in self.Buttons:
                    b.Enable()
            except Exception as e:
                wx.MessageDialog(self, message=str(e))
            self.update_olv()

    def close_proj(self, event=None):
        global proj_path, proj_ss
        if proj_path is not None:
            proj_path = None
            proj_ss.shutdown()
            proj_ss.server_close()
            for b in self.Buttons:
                b.Disable()
            self.OLV.DeleteAllItems()

    def change_sp(self, event):
        global proj_ss,server_port
        ted = wx.TextEntryDialog(self, "监听端口（0~65535）", "选择服务器端口", str(server_port))
        if ted.ShowModal() == wx.ID_OK:
            port = ted.GetValue()
            if str.isdigit(port) and int(port) < 65536:
                server_port = int(port)
                if proj_path is not None:
                    proj_ss.shutdown()
                    proj_ss.server_close()
                    try:
                        proj_ss = run_ss(local_address, server_port, proj_db)
                        print("ok")
                    except Exception as e:
                        print("??")
                        wx.MessageDialog(self, message=str(e))
            else:
                md = wx.MessageDialog(message="请输入正确端口")

    def change_cp(self, event):
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
            models.append(MainModel(item[0], item[1], item[2], item[3], probs))
        self.OLV.DeleteAllItems()
        self.OLV.AddObjects(models)

    def add_mf(self, T):
        if T == "S":
            MF = StudentFrame(parent=self)
        elif T == "P":
            MF = ProblemFrame(parent=self)
        elif T == "W":
            MF = WorkFrame(parent=self)
        MF.Show(True)
        self.Freeze()


class StudentFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent=parent, title="学生管理", size=(
            530, 260), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.Bind(wx.EVT_CLOSE, self.destroy)
        self.OLV = ObjectListView(parent=self, pos=(10, 10), size=(380, 200),
                                  sortable=True, style=wx.LC_REPORT | wx.BORDER_SUNKEN)

        self.OLV.SetColumns([
            ColumnDefn("学号", "left", 100, "Id"),
            ColumnDefn("姓名", "left", 80, "name"),
            ColumnDefn("登录密码", "left", 100, "pwd")
        ])
        self.OLV.CreateCheckStateColumn()
        self.update_olv()

        Ba = wx.Button(parent=self, label="添加学生", size=(100, 20), pos=(400, 10))
        self.Bind(wx.EVT_BUTTON, lambda e: AddStudentDialog(self).Show(True), Ba)

        Bx = wx.Button(parent=self, label="从Excel添加学生", size=(100, 20), pos=(400, 40))
        self.Bind(wx.EVT_BUTTON, self.xls_add, Bx)

        Bd = wx.Button(parent=self, label="删除学生", size=(100, 20), pos=(400, 70))
        self.Bind(wx.EVT_BUTTON, self.del_usr, Bd)

        Bo = wx.Button(parent=self, label="导出学生到Excel", size=(100, 20), pos=(400, 100))
        self.Bind(wx.EVT_BUTTON, self.xls_out, Bo)

    def destroy(self, event):
        self.GetParent().Thaw()
        self.GetParent().update_olv()
        self.Destroy()

    def update_olv(self, event=None):
        con, cur = open_db(proj_db)
        probs = [x[0] for x in select_all(cur, "problem_info", ["id"])]
        items = select_all(cur, "user_info", ["*"])
        close_db(con, cur)
        models = []
        for item in items:
            models.append(MainModel(item[0], item[1], item[2], item[3], probs))
        self.OLV.DeleteAllItems()
        self.OLV.AddObjects(models)

    def xls_add(self, event):
        fd = wx.FileDialog(self, "选择Excel文件", defaultDir=proj_path)
        if fd.ShowModal() == wx.ID_OK:
            path = fd.GetPath()
            if path[-4:] == ".xls" or path[-5:] == ".xlsx":
                md = wx.MessageDialog(self, message=import_user_from_xls(proj_db, path))
                if md.ShowModal() == wx.ID_OK:
                    pass
            else:
                md = wx.MessageDialog(self, message="请选择有效Excel文件")
                if md.ShowModal() == wx.ID_OK:
                    pass
        self.update_olv()

    def del_usr(self, event):
        delete_user(proj_db, [obj.Id for obj in self.OLV.GetCheckedObjects()])
        self.update_olv()

    def xls_out(self, event):
        fd = wx.FileDialog(self, "选择Excel文件", defaultDir=proj_path)
        if fd.ShowModal() == wx.ID_OK:
            path = fd.GetPath()
            if path[-4:] == ".xls":
                if export_user_to_xls(proj_db, path) == EXPORT_TO_XLS_ERROR:
                    md = wx.MessageDialog(self, message="仅支持xls文件，请确保目标文件已关闭")
                else:
                    md = wx.MessageDialog(self, message=EXPORT_TO_XLS_SUCCEED)
                if md.ShowModal() == wx.ID_OK:
                    pass
            else:
                md = wx.MessageDialog(self, message="仅支持xls文件，请确保目标文件已关闭")
                if md.ShowModal() == wx.ID_OK:
                    pass


class AddStudentDialog(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent=parent, size=(500, 80),
                          style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.GetParent().Freeze()
        self.Bind(wx.EVT_CLOSE, self.destroy)
        Ok = wx.Button(self, label="确定", size=(80, 30), pos=(400, 5))

        Id_ = wx.StaticText(self, label="学号", size=(40, 30), pos=(10, 10))
        Id = wx.TextCtrl(self, size=(80, 20), pos=(40, 10))

        Name_ = wx.StaticText(self, label="姓名", size=(40, 30), pos=(130, 10))
        Name = wx.TextCtrl(self, size=(80, 20), pos=(160, 10))

        Pwd_ = wx.StaticText(self, label="密码", size=(40, 30), pos=(250, 10))
        Pwd = wx.TextCtrl(self, size=(80, 20), pos=(280, 10), value="选填")

        self.Bind(EVT_BUTTON, lambda e: self.click(Id.GetValue(), Name.GetValue(), Pwd.GetValue()), Ok)

    def destroy(self, event):
        self.GetParent().Thaw()
        self.Destroy()

    def click(self, Id, Name, Pwd):
        if Id == "" or Name == "":
            md = wx.MessageDialog(self, message="信息不能为空")
            if md.ShowModal() == wx.ID_OK:
                self.GetParent().Thaw()
                self.Destroy()
        if Pwd == "" or Pwd == "选填":
            import_user(proj_db, Id, Name)
        else:
            import_user(proj_db, Id, Name, Pwd)
        self.GetParent().Thaw()
        self.GetParent().update_olv()
        self.Destroy()


class ProblemFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent=parent, title="学生管理", size=(640, 400),
                          style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.Bind(wx.EVT_CLOSE, self.destroy)

    def destroy(self, event):
        self.Show(False)
        self.GetParent().Thaw()
        self.GetParent().update_olv()


class WorkFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent=parent, title="学生管理", size=(
            640, 400), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.Bind(wx.EVT_CLOSE, self.destroy)

    def destroy(self, event):
        self.Show(False)
        self.GetParent().Thaw()
        self.GetParent().update_olv()


class MainModel(object):
    def __init__(self, Id, name, pwd, ctime, probs):
        self.Id = Id
        self.name = name
        self.pwd = pwd
        self.ctime = ctime
        vprobs = []
        for prob in probs:
            v = "□"*len(prob)
            for suf in LANGUAGE_CONFIG:
                if os.path.isfile(os.path.join(proj_path, Id, prob+suf)):
                    v = prob
            vprobs.append(v)
        self.ws = "|".join(vprobs)


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
