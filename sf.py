import wx
from utilities import MainModel
from sql import *
from ObjectListView import ObjectListView, ColumnDefn


class StudentFrame(wx.Frame):
    def __init__(self, parent, proj_path, proj_db):
        parent.Freeze()
        wx.Frame.__init__(self, parent=parent, title="学生管理", size=(
            530, 260), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.proj_path = proj_path
        self.proj_db = proj_db
        self.Center(wx.BOTH)
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

        Ba = wx.Button(parent=self, size=(100, 20), pos=(400, 10),label="添加学生",)
        Bx = wx.Button(parent=self,size=(100, 20), pos=(400, 40) ,label="从Excel添加学生")
        Be = wx.Button(parent=self,size=(100, 20), pos=(400, 70) ,label="修改学生")
        Bd = wx.Button(parent=self, size=(100, 20), pos=(400, 100), label="删除学生")
        Bo = wx.Button(parent=self, size=(100, 20), pos=(400, 130), label="导出学生到Excel")

        self.Bind(wx.EVT_BUTTON, self.add_user, Ba)
        self.Bind(wx.EVT_BUTTON, self.xls_add, Bx)
        self.Bind(wx.EVT_BUTTON, self.edit_user,Be)
        self.Bind(wx.EVT_BUTTON, self.del_usr, Bd)
        self.Bind(wx.EVT_BUTTON, self.xls_out, Bo)

    def destroy(self, event):
        self.GetParent().Thaw()
        self.GetParent().update_olv()
        self.Destroy()

    def update_olv(self, event=None):
        con, cur = open_db(self.proj_db)
        probs = [x[0] for x in select_all(cur, "problem_info", ["id"])]
        items = select_all(cur, "user_info", ["*"])
        close_db(con, cur)
        models = []
        for item in items:
            models.append(
                MainModel(item[0], item[1], item[2], item[3], probs, self.proj_path))
        self.OLV.DeleteAllItems()
        self.OLV.AddObjects(models)

    def add_user(self, event):
        StudentDialog(self, self.proj_db).Show()

    def edit_user(self, event):
        if len(self.OLV.GetCheckedObjects())==1:
            obj = self.OLV.GetCheckedObjects()[0]
            sd = StudentDialog(self,self.proj_db,[obj.Id,obj.name,obj.pwd])
            if sd.ShowModal() == wx.ID_OK:
                pass
        else:
            md = wx.MessageDialog(self,message="请选择一个学生")
            if md.ShowModal() == wx.ID_OK:
                pass

    def del_usr(self, event):
        delete_user(self.proj_db, [
                    obj.Id for obj in self.OLV.GetCheckedObjects()])
        self.update_olv()

    def xls_add(self, event):
        fd = wx.FileDialog(self, "选择Excel文件", defaultDir=self.proj_path)
        if fd.ShowModal() == wx.ID_OK:
            path = fd.GetPath()
            if path[-4:] == ".xls" or path[-5:] == ".xlsx":
                md = wx.MessageDialog(
                    self, message=import_user_from_xls(self.proj_db, path))
                if md.ShowModal() == wx.ID_OK:
                    pass
            else:
                md = wx.MessageDialog(self, message="请选择有效Excel文件")
                if md.ShowModal() == wx.ID_OK:
                    pass
        self.update_olv()

    def xls_out(self, event):
        fd = wx.FileDialog(self, "选择Excel文件", defaultDir=self.proj_path)
        if fd.ShowModal() == wx.ID_OK:
            path = fd.GetPath()
            if path[-4:] == ".xls":
                if export_user_to_xls(self.proj_db, path) == EXPORT_TO_XLS_ERROR:
                    md = wx.MessageDialog(self, message="仅支持xls文件，请确保目标文件已关闭")
                else:
                    md = wx.MessageDialog(self, message=EXPORT_TO_XLS_SUCCEED)
                if md.ShowModal() == wx.ID_OK:
                    pass
            else:
                md = wx.MessageDialog(self, message="仅支持xls文件，请确保目标文件已关闭")
                if md.ShowModal() == wx.ID_OK:
                    pass


class StudentDialog(wx.Dialog):
    def __init__(self, parent, proj_db,def_list=None):
        parent.Freeze()
        wx.Dialog.__init__(self, parent=parent, size=(500, 80),
                          style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))

        self.proj_db = proj_db
        self.Bind(wx.EVT_CLOSE, self.destroy)
        self.Center(wx.BOTH)

        Id_ = wx.StaticText(self, label="学号", size=(40, 30), pos=(10, 10))
        Name_ = wx.StaticText(self, label="姓名", size=(40, 30), pos=(130, 10))
        Pwd_ = wx.StaticText(self, label="密码", size=(40, 30), pos=(250, 10))
        Ok = wx.Button(self, label="确定", size=(80, 30), pos=(400, 5))
        Id = wx.TextCtrl(self, size=(80, 20), pos=(40, 10))
        Name = wx.TextCtrl(self, size=(80, 20), pos=(160, 10))
        Pwd = wx.TextCtrl(self, size=(80, 20), pos=(280, 10))
        if def_list is not None:
            Id.SetValue(def_list[0])
            Id.Disable()
            Name.SetValue(def_list[1])
            Pwd.SetValue(def_list[2])
        else:
            Pwd.SetValue("选填")

        self.Bind(wx.EVT_BUTTON, lambda e: self.click(
            Id.GetValue(), Name.GetValue(), Pwd.GetValue()), Ok)

    def destroy(self, event):
        self.GetParent().Thaw()
        self.Destroy()

    def click(self, Id, Name, Pwd):
        if Id == "" or Name == "":
            md = wx.MessageDialog(self, message="信息不能为空")
            if md.ShowModal() == wx.ID_OK:
                self.GetParent().Thaw()
                self.Destroy()
                return
        if Pwd == "" or Pwd == "选填":
            import_user(self.proj_db, Id, Name)
        else:
            import_user(self.proj_db, Id, Name, Pwd)
        self.SetId(wx.ID_OK)
        self.GetParent().Thaw()
        self.GetParent().update_olv()
        self.Destroy()
