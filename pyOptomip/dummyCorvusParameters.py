import wx
from dummyCorvus_instr import dummyCorvus
import dummyCorvusFrame


class dummyCorvusParameters(wx.Panel):
    name = 'Dummy Corvus'

    def __init__(self, parent, connectPanel, **kwargs):
        super(dummyCorvusParameters, self).__init__(parent)
        self.connectPanel = connectPanel
        self.InitUI()

    def InitUI(self):
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        fgs = wx.FlexGridSizer(2, 2, 8, 25)

        self.connectBtn = wx.Button(self, label='Connect')
        self.connectBtn.Bind(wx.EVT_BUTTON, self.connect)

        fgs.AddMany([(0, 0), (self.connectBtn, 0, wx.ALIGN_BOTTOM)])
        fgs.AddGrowableCol(1, 2)
        hbox.Add(fgs, proportion=1, flag=wx.EXPAND)
        self.SetSizer(hbox)

    def connect(self, event):
        self.corvus = dummyCorvus()
        self.corvus.panelClass = dummyCorvusFrame.topCorvusPanel
        self.connectPanel.instList.append(self.corvus)
        self.connectBtn.Disable()
