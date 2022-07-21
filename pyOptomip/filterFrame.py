import wx

class filterFrame(wx.Frame):

    def __init__(self, parent, devList):

        displaySize = wx.DisplaySize()
        super(filterFrame, self).__init__(parent, title='Filter', size=(displaySize[0] * 3/ 8.0, displaySize[1] * 2/ 4.0))

        self.devList = devList
        try:
            self.InitUI()
        except Exception as e:
            raise
        self.Centre()
        self.Show()

    def InitUI(self):
        self.Bind(wx.EVT_CLOSE, self.OnExitApp)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox.Add(vbox, flag=wx.EXPAND, border=0, proportion=1)
        self.SetSizer(hbox)

    def OnExitApp(self, event):
        self.Destroy()
