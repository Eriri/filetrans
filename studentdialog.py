from serverbase import *
from xlrd import open_workbook
from xlwt import Workbook as xlswb
from xlsxwriter import Workbook as xlsxwb


class StudentDialog(Dialog):
    def __init__(self, app):
        Dialog.__init__(self, app, -1, "SD", (0, 0), (500, 300), DEFAULT_FRAME_STYLE, "sd")
        self.SetIcon(app.GetIcon()), self.SetMinSize((500, 300)), self.Center(BOTH)
        self.P, self.B = Panel(self), BoxSizer(HORIZONTAL)
        self.PR, self.BR = Panel(self.P), BoxSizer(VERTICAL)
        self.SD = set()

        self.OLV = ObjectListView(parent=self.P, sortable=True, style=LC_REPORT)
        self.OLV.SetColumns([
            ColumnDefn("学号", "left", 100, "no"),
            ColumnDefn("姓名", "left", 100, "name")])
        self.OLV.CreateCheckStateColumn()

        B = [Button(self.PR, 0, "添加"), Button(self.PR, 1, "删除"),
             Button(self.PR, 2, "从Excel添加"), Button(self.PR, 3, "导出到Excel")]
        for b in B:
            self.BR.Add(b, 0, EXPAND | ALL, 5), self.Bind(EVT_BUTTON, self.button_func, b)
        self.PR.SetSizer(self.BR)

        self.B.Add(self.OLV, 1, EXPAND | ALL, 5)
        self.B.Add(self.PR, 0)
        self.P.SetSizer(self.B)

        self.init_all()

    def init_all(self):
        connection = connect(self.GetParent().database)
        user = select(connection, "user", ["no", "name"])
        connection.close()
        self.OLV.DeleteAllItems()
        for no, name in user:
            self.OLV.AddObject(Model(no, name, path=self.GetParent().work_dir))
            self.SD.add(no)

    def add(self, nos):
        connection = connect(self.GetParent().database)
        for no in nos:
            obj = Model(no, select_one(connection, "user", ["name"], ["no"], [no])[0])
            if no in self.SD:
                self.OLV.RefreshObject(obj)
            else:
                self.OLV.AddObject(obj), self.SD.add(no)
        connection.close()
        self.GetParent().add(nos)

    def delete(self, nos):
        for no in nos:
            self.OLV.RemoveObject(Model(no))
            self.SD.remove(no)
        self.GetParent().delete(nos)

    def button_func(self, event):
        try:
            if event.GetId() == 0:
                AddStudent(self).ShowModal()
            if event.GetId() == 1:
                md = MessageDialog(self, "确认删除？", style=YES_NO | ICON_QUESTION)
                md.SetIcon(self.GetParent().GetIcon()), md.SetTitle("删除学生")
                if md.ShowModal() == ID_YES:
                    nos = [obj.no for obj in self.OLV.GetCheckedObjects()]
                    delete_user(self.GetParent().database, nos), self.delete(nos)
            if event.GetId() == 2:
                D = FileDialog(self, "选择Excel文件", wildcard="Excel files (*.xls;*.xls)|*.xls;*xlsx")
                if D.ShowModal() == ID_OK:
                    AddStudents(self, D.GetPath()).ShowModal()
            if event.GetId() == 3:
                md = MultiChoiceDialog(self, "选择导出属性", "导出", ["学号", "姓名", "成绩"])
                cte = {0: "no", 1: "name", 2: "point"}
                if md.ShowModal() == ID_OK:
                    D = FileDialog(self, "选择Excel文件", wildcard="Excel files (*.xls;*.xls)|*.xls;*xlsx")
                    if D.ShowModal() == ID_OK:
                        attribute = [cte[x] for x in md.GetSelections()]
                        connection = connect(self.GetParent().database)
                        path, user = D.GetPath(), select(connection,"user",attribute)
                        connection.close()
                        if os.path.splitext(path)[1] == ".xlsx":
                            workbook = xlsxwb(path)
                            sheet = workbook.add_worksheet("user_sheet")
                        else:
                            workbook = xlswb()
                            sheet = workbook.add_sheet("user_sheet")
                        for i, a in enumerate(attribute):
                            sheet.write(0,i,a)
                        for i, u in enumerate(user):
                            for j in range(len(attribute)):
                                sheet.write(i+1,j,u[j])
                        if os.path.splitext(path)[1] == ".xlsx":
                            workbook.close()
                        else:
                            workbook.save(path)
                        MessageBox("导出成功")

        except Exception as e:
            MessageBox(str(e))


class AddStudent(Dialog):
    def __init__(self, app):
        Dialog.__init__(self, app, -1, "AD", (0, 0), (400, 70),
                           DEFAULT_FRAME_STYLE & ~(RESIZE_BORDER | MAXIMIZE_BOX), "ad")
        self.Center(BOTH), self.SetIcon(app.GetParent().GetIcon())
        self.P, self.B = Panel(self), BoxSizer(HORIZONTAL)

        self.B.Add(StaticText(self.P, -1, "学号"), 1, EXPAND | ALL, 5)
        self.NO = TextCtrl(self.P, -1)
        self.B.Add(self.NO, 1, EXPAND | ALL, 5)

        self.B.Add(StaticText(self.P, -1, "姓名"), 1, EXPAND | ALL, 5)
        self.NAME = TextCtrl(self.P, -1)
        self.B.Add(self.NAME, 1, EXPAND | ALL, 5)

        self.OK = Button(self.P, -1, "确定")
        self.Bind(EVT_BUTTON, self.click, self.OK)
        self.B.Add(self.OK, 1, EXPAND | ALL, 5)

        self.P.SetSizer(self.B)

    def click(self, event):
        if self.NO.GetValue() == "" or self.NAME.GetValue() == "":
            MessageBox("请正确输入")
            return

        import_user(self.GetParent().GetParent().database, self.NO.GetValue(), self.NAME.GetValue())
        self.GetParent().add([self.NO.GetValue()])
        self.Destroy()


class AddStudents(Dialog):
    def __init__(self, app, path):
        Dialog.__init__(self, app, -1, "ADS", (0, 0), (450, 75),
                           DEFAULT_FRAME_STYLE & ~(RESIZE_BORDER | MAXIMIZE_BOX), "ads")
        self.Center(BOTH), self.SetIcon(app.GetParent().GetIcon())
        self.P, self.B = Panel(self), BoxSizer(HORIZONTAL)

        self.sheet = open_workbook(path).sheets()[0]
        self.attribute = self.sheet.row_values(0)
        self.attribute.append("None")

        self.B.Add(StaticText(self.P, -1, "选择学号列名"), 1, EXPAND | ALL, 5)
        self.NO = ComboBox(self.P, -1, value="None", choices=self.attribute, style=CB_READONLY)
        self.B.Add(self.NO, 1, EXPAND | ALL, 5)

        self.B.Add(StaticText(self.P, -1, "选择姓名列名"), 1, EXPAND | ALL, 5)
        self.NAME = ComboBox(self.P, -1, value="None", choices=self.attribute, style=CB_READONLY)
        self.B.Add(self.NAME, 1, EXPAND | ALL, 5)

        self.OK = Button(self.P, -1, "导入")
        self.Bind(EVT_BUTTON, self.click, self.OK)
        self.B.Add(self.OK, 1, EXPAND | ALL, 5)

        self.P.SetSizer(self.B)

    def click(self, event):
        if self.NO.GetValue() != "None" and self.NAME.GetValue() != "None":
            no, name = self.attribute.index(self.NO.GetValue()), self.attribute.index(self.NAME.GetValue())
            connection, nos = connect(self.GetParent().GetParent().database), []
            for i in range(1, self.sheet.nrows):
                insert(connection, "user", ["no", "name"], [self.sheet.row_values(i)[no], self.sheet.row_values(i)[name]])
                nos.append(self.sheet.row_values(i)[no])
            connection.commit(), connection.close()
            self.GetParent().add(nos), self.Destroy()
        else:
            MessageBox("请选择属性列名"), self.Destroy()
