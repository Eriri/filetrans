import wx
from ObjectListView import ObjectListView,ColumnDefn


class ProblemFrame(wx.Frame):
    def __init__(self, parent, prob_path, proh_db):
        parent.Freeze()
        wx.Frame.__init__(self, parent=parent, title="题目管理", size=(530, 260),
                          style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.Center(wx.BOTH)
        self.Bind(wx.EVT_CLOSE, self.destroy)
        self.C = wx.Choice(parent=self,pos=(10,10),size=(200,26))
        self.OLV = ObjectListView(parent=self,pos=(10,40),size=(200,100),sortable=True )


    def add_prob(self,event):
        pass

    def del_prob(self,event):
        pass

    def add_test(self,event):
        pass

    def del_test(self,event):
        pass

    def destroy(self,event):
        self.GetParent().Thaw()
        self.GetParent().update_olv()
        self.Destroy()