from serverbase import *


class WorkDialog(Dialog):
    def __init__(self, app):
        Dialog.__init__(self, app, -1, "WD", (0, 0), (500, 300), DEFAULT_FRAME_STYLE, "work")
        self.SetIcon(app.GetIcon()), self.SetMinSize((500, 300)), self.Center(BOTH)

        self.B, self.PR, self.BR = BoxSizer(HORIZONTAL), Panel(self), BoxSizer(VERTICAL)

        self.OLV = ObjectListView(parent=self, sortable=True, style=LC_REPORT)
        self.OLV.SetColumns([
            ColumnDefn("学号", "left", 100, "no"),
            ColumnDefn("姓名", "left", 100, "name"),
            ColumnDefn("IP地址", "left", 100, "ip"),
            ColumnDefn("接收情况", "left", 200, "info")])
        self.OLV.CreateCheckStateColumn()
        self.B.Add(self.OLV, 1, EXPAND | ALL, 5)

        self.C = Button(self.PR, 0, "全部接收")
        self.Bind(EVT_BUTTON, self.collect, self.C)
        self.BR.Add(self.C, 0, EXPAND | ALL, 5)

        self.CS = Button(self.PR, 1, "接收选中用户")
        self.Bind(EVT_BUTTON, self.collect, self.CS)
        self.BR.Add(self.CS, 0, EXPAND | ALL, 5)

        self.G = Gauge(self.PR, -1, style=GA_VERTICAL)
        self.BR.Add(self.G, 1, EXPAND | ALL, 5)

        self.PR.SetSizer(self.BR)
        self.B.Add(self.PR, 0)
        self.SetSizer(self.B)

        self.init_all()

    def init_all(self):
        connection = connect(self.GetParent().database)
        user = [SR(no, name, ip) for no, name, ip in select(connection, "user", ["no", "name", "ip"])]
        connection.close()
        self.OLV.DeleteAllItems(), self.OLV.AddObjects(user)

    def update(self, no, count, info, error=None):
        obj = self.OLV.GetObjectAt(self.OLV.GetIndexOf(SR(no)))
        if info == COLLECT_WORK_SUCCEED:
            obj.fresh_info("成功接收作业，共包括", count)
        elif info == COLLECT_WORK_FAILED:
            obj.fresh_info("接收发生失败，已接收", count, error)
        self.OLV.RefreshObject(obj), self.G.SetValue(self.G.GetValue() + 1)
        if self.G.GetValue() == self.G.GetRange():
            self.C.Enable(), self.CS.Enable()

    def collect(self, event):
        self.C.Disable(), self.CS.Disable()
        collect_works(self.GetParent(), self, event.GetId())

