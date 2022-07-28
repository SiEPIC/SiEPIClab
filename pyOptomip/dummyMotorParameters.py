import wx

from hp816x_instr import hp816x
import laserPanel


class dummyMotorParameters(wx.Panel):
    name = 'Dummy motor'

    def __init__(self, parent, connectPanel, **kwargs):
        super(dummyMotorParameters, self).__init__(parent)
        self.connectPanel = connectPanel
        self.InitUI()

    def InitUI(self):
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        fgs = wx.FlexGridSizer(2, 2, 8, 25)

        st1 = wx.StaticText(self, label='Mainframe address:')
        self.tc_address = wx.TextCtrl(self, value='GPIB0::20::INSTR')

        self.connectBtn = wx.Button(self, label='Connect')
        self.connectBtn.Bind(wx.EVT_BUTTON, self.connect)

        fgs.AddMany([(st1, 1, wx.EXPAND), (self.tc_address, 1, wx.EXPAND),
                     (0, 0), (self.connectBtn, 0, wx.ALIGN_BOTTOM)])
        fgs.AddGrowableCol(1, 2)
        hbox.Add(fgs, proportion=1, flag=wx.EXPAND)
        self.SetSizer(hbox)

    def connect(self, event):
        laser = hp816x();
        laser.pwmSlotIndex = [0, 1]
        laser.pwmSlotMap = [(0, 0), (1, 0)]
        laser.panelClass = laserPanel.laserTopPanel  # Give the laser its panel class

        def dummyNumPanels(self):
            return 3

        funcType = type(laser.getNumPWMChannels)

        laser.getNumPWMChannels = funcType(dummyNumPanels, laser, hp816x)
        self.connectPanel.instList.append(laser)