from serverbase import *


class ProblemDialog(Dialog):
    def __init__(self, app):
        Dialog.__init__(self, app, -1, "PD", (0, 0), (500, 300), DEFAULT_FRAME_STYLE, "problem")
        self.SetIcon(app.GetIcon()), self.SetMinSize((500, 300)), self.Center(BOTH)
        self.P = Panel(self)
        self.PL, self.PR = Panel(self.P), Panel(self.P)
        self.B, self.BL, self.BR = BoxSizer(HORIZONTAL), BoxSizer(VERTICAL), BoxSizer(VERTICAL)

        self.CB = ComboBox(parent=self.PL, id=-1, value="None", choices=["None"], style=CB_READONLY)
        self.Bind(EVT_COMBOBOX, self.update, self.CB)
        self.BL.Add(self.CB, 0, EXPAND | ALL, 5)

        self.OLV = ObjectListView(parent=self.PL, sortable=True, id=-1, style=LC_REPORT)
        self.OLV.SetColumns([
            ColumnDefn("测试点", "left", 100, "no"),
            ColumnDefn("输入", "left", 100, "in_path"),
            ColumnDefn("输出", "left", 100, "out_path"),
            ColumnDefn("分数", "left", 100, "point")])
        self.OLV.CreateCheckStateColumn()
        self.BL.Add(self.OLV, 1, EXPAND | ALL, 5)

        self.PL.SetSizer(self.BL)

        BT = [Button(self.PR, 0, "题目编辑"), Button(self.PR, 1, "自动导入测试点"),
              Button(self.PR, 2, "添加测试点"), Button(self.PR, 3, "删除测试点")]
        for b in BT:
            self.BR.Add(b, 1, EXPAND | ALL, 5), self.Bind(EVT_BUTTON, self.add, b)

        self.PR.SetSizer(self.BR)

        self.B.Add(self.PL, 1, EXPAND), self.B.Add(self.PR, 0)
        self.P.SetSizer(self.B)

        self.fresh()

    def add(self, event):
        try:
            if event.GetId() == 0:
                EditProblem(self).ShowModal()
            if event.GetId() == 1 and self.CB.GetValue() != "None":
                p = os.path.join(self.GetParent().prob_dir, self.CB.GetValue())
                md = MessageDialog(self, "确认从目录" + p + "中自动导入测试样点？", style=YES_NO)
                if md.ShowModal() == ID_YES and os.path.isdir(p):
                    fl = [x for x in os.listdir(p) if os.path.isfile(os.path.join(p, x))]
                    inl = [x.split(".")[0] for x in fl if len(x.split(".")) == 2 and x.split(".")[1] == "in"]
                    outl = [x.split(".")[0] for x in fl if len(x.split(".")) == 2 and x.split(".")[1] == "out"]
                    val = [x for x in inl if x in outl]
                    connection = connect(self.GetParent().database)
                    for f in val:
                        insert(connection, "test", ["no", "belong", "in_path", "out_path", "point"],
                               [os.path.basename(f), self.CB.GetValue(), os.path.join(p, f) + ".in", os.path.join(p, f) + ".out", 10])
                    connection.commit(), connection.close()
            if event.GetId() == 2 and self.CB.GetValue() != "None":
                EditTest(self, self.CB.GetValue()).ShowModal()
            if event.GetId() == 3:
                connection = connect(self.GetParent().database)
                obj = self.OLV.GetCheckedObjects()
                for o in obj:
                    delete(connection, "test", ["no"], [o.no])
                connection.commit(), connection.close()
        except Exception as e:
            MessageBox(str(e))
        self.fresh()

    def fresh(self, event=None):
        connection, pre = connect(self.GetParent().database), self.CB.GetValue()
        choices = [x[0] for x in select(connection, "problem", ["no"])]
        connection.close()
        self.CB.Clear(), choices.append("None"), self.CB.AppendItems(choices)
        self.CB.SetValue(pre) if pre in choices else self.CB.SetValue("None")
        self.update()

    def update(self, event=None):
        self.OLV.DeleteAllItems()
        if self.CB.GetValue() != "None":
            connection, i = connect(self.GetParent().database), self.CB.GetValue()
            test = select(connection, "test", ["*"], ["belong"], [i])
            connection.close()
            self.OLV.AddObjects(
                [Test(no, belong, in_path, out_path, point) for no, belong, in_path, out_path, point in test])


class EditProblem(Dialog):
    def __init__(self, app):
        Dialog.__init__(self, app, -1, "EP", (0, 0), (550, 120),
                           DEFAULT_FRAME_STYLE & ~(RESIZE_BORDER | MAXIMIZE_BOX), "ep")
        self.Center(BOTH), self.SetIcon(app.GetParent().GetIcon())

        self.P, self.B = Panel(self), BoxSizer(VERTICAL)
        self.PU, self.BU = Panel(self.P), BoxSizer(HORIZONTAL)
        self.PD, self.BD = Panel(self.P), BoxSizer(HORIZONTAL)

        self.CB = ComboBox(parent=self.PU, id=-1, value="None", choices=["None"], style=CB_READONLY)
        self.Bind(EVT_COMBOBOX, self.update, self.CB)
        self.BU.Add(self.CB, 1, EXPAND | ALL, 5)

        self.d = Button(self.PU, -1, "删除")
        self.Bind(EVT_BUTTON, self.delete, self.d)
        self.BU.Add(self.d, 0, EXPAND | ALL, 5)

        self.PU.SetSizer(self.BU)

        self.BD.Add(StaticText(self.PD, -1, "题目名称:"), 1, EXPAND | ALL, 5)
        self.NO = TextCtrl(self.PD, -1)
        self.NO.SetMaxSize((60, 60))
        self.BD.Add(self.NO, 1, ALL, 5)

        self.BD.Add(StaticText(self.PD, -1, "运行时限/秒:"), 1, EXPAND | ALL, 5)
        self.TIME = TextCtrl(self.PD, -1)
        self.TIME.SetMaxSize((60, 60))
        self.BD.Add(self.TIME, 1, ALL, 5)

        self.BD.Add(StaticText(self.PD, -1, "内存空间/兆:"), 1, EXPAND | ALL, 5)
        self.MEMORY = TextCtrl(self.PD, -1)
        self.MEMORY.SetMaxSize((60, 60))
        self.BD.Add(self.MEMORY, 1, ALL, 5)

        self.e = Button(self.PD, -1, "编辑/添加")
        self.Bind(EVT_BUTTON, self.edit, self.e)
        self.BD.Add(self.e, 1, EXPAND | ALL, 5)

        self.PD.SetSizer(self.BD)

        self.B.Add(self.PU, 1, EXPAND), self.B.Add(self.PD, 1, EXPAND), self.P.SetSizer(self.B)
        self.fresh()

    def fresh(self, event=None):
        connection, pre = connect(self.GetParent().GetParent().database), self.CB.GetValue()
        choices = [x[0] for x in select(connection, "problem", ["no"])]
        self.CB.Clear(), choices.append("None"), connection.close()
        self.CB.AppendItems(choices)
        self.CB.SetValue(pre) if pre in choices else self.CB.SetValue("None")
        self.update()

    def update(self, event=None):
        if self.CB.GetValue() == "None":
            self.NO.SetEditable(True), self.NO.SetValue(""), self.TIME.SetValue(""), self.MEMORY.SetValue("")
        else:
            connection = connect(self.GetParent().GetParent().database)
            data = select_one(connection, "problem", ["time", "memory"], ["no"], [self.CB.GetValue()])
            connection.close()
            self.NO.SetValue(self.CB.GetValue()), self.NO.SetEditable(False)
            self.TIME.SetValue(str(data[0])), self.MEMORY.SetValue(str(data[1]))

    def delete(self, event):
        try:
            if self.CB.GetValue() != "None":
                connection = connect(self.GetParent().GetParent().database)
                delete(connection, "problem", ["no"], [self.CB.GetValue()])
                delete(connection, "test", ["belong"], [self.CB.GetValue()])
                connection.commit(), connection.close()
                self.fresh()
        except Exception as e:
            MessageBox(str(e))

    def edit(self, event):
        try:
            if float(self.TIME.GetValue()) > 0 and int(self.MEMORY.GetValue()) > 0 and len(self.NO.GetValue()) > 0:
                connection = connect(self.GetParent().GetParent().database)
                insert(connection, "problem", ["no", "time", "memory"],
                       [self.NO.GetValue(), float(self.TIME.GetValue()), int(self.MEMORY.GetValue())])
                connection.commit(), connection.close()
                self.fresh()
            else:
                raise Exception("请输入正确参数")
        except Exception as e:
            MessageBox(str(e))


class EditTest(Dialog):
    def __init__(self, app, belong):
        Dialog.__init__(self, app, -1, "ET", (0, 0), (700, 70),
                           DEFAULT_FRAME_STYLE & ~(RESIZE_BORDER | MAXIMIZE_BOX), "et")
        self.belong = belong
        self.Center(BOTH), self.SetIcon(self.GetParent().GetParent().GetIcon())

        self.P = Panel(self)
        self.B = BoxSizer(HORIZONTAL)

        self.B.Add(StaticText(self.P, -1, "测试点"), 1, EXPAND | ALL, 5)
        self.NO = TextCtrl(self.P, -1, "")
        self.NO.SetMaxSize((80, 70))
        self.B.Add(self.NO, 1, ALL, 5)

        self.IB = Button(self.P, 0, "输入路径")
        self.Bind(EVT_BUTTON, self.select, self.IB)
        self.B.Add(self.IB, 1, EXPAND | ALL, 5)
        self.I = TextCtrl(self.P, -1, "")
        self.I.SetMaxSize((80, 70))
        self.B.Add(self.I, 1, ALL, 5)

        self.OB = Button(self.P, 1, "输出路径")
        self.Bind(EVT_BUTTON, self.select, self.OB)
        self.B.Add(self.OB, 1, EXPAND | ALL, 5)
        self.O = TextCtrl(self.P, -1, "")
        self.O.SetMaxSize((80, 70))
        self.B.Add(self.O, 1, ALL, 5)

        self.B.Add(StaticText(self.P, -1, "分数"), 1, EXPAND | ALL, 5)
        self.PT = TextCtrl(self.P, -1)
        self.PT.SetMaxSize((80, 70))
        self.B.Add(self.PT, 1, ALL, 5)

        self.OK = Button(self.P, -1, "添加")
        self.Bind(EVT_BUTTON, self.click, self.OK)
        self.B.Add(self.OK, 1, EXPAND | ALL, 5)

        self.P.SetSizer(self.B)

    def select(self, event):
        fd = FileDialog(self, "选择文件", None)
        fd.SetIcon(self.GetParent().GetParent().GetIcon()), fd.Center(BOTH)
        if fd.ShowModal() == ID_OK:
            [self.I, self.O][event.GetId()].SetValue(fd.GetPath())

    def click(self, event):
        try:
            if self.NO.GetValue() != "" and os.path.isfile(self.I.GetValue()) and os.path.isfile(self.O.GetValue()) and int(self.PT.GetValue()) >= 0:
                connection = connect(self.GetParent().GetParent().database)
                insert(connection, "test", ["no", "belong", "in_path", "out_path", "point"],
                       [self.NO.GetValue(), self.belong, self.I.GetValue(), self.O.GetValue(), self.PT.GetValue()])
                connection.commit(), connection.close()
            else:
                raise Exception("请输入正确参数")
        except Exception as e:
            MessageBox(str(e))
        self.Destroy()
