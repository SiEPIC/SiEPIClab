import wx


# Panel that appears in the main window which contains the controls for the Thorlabs motors.
class topBSC203MotorPanel(wx.Panel):
    def __init__(self, parent, motor):
        super(topBSC203MotorPanel, self).__init__(parent)
        self.bsc = motor
        self.numAxes = self.bsc.numAxes
        self.InitUI()

    def InitUI(self):
        sb = wx.StaticBox(self, label='Wedge Probe Stage')
        vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)

        for axis in range(0, self.numAxes):
            motorPanel = BSC203Panel(self, axis+1)
            motorPanel.motor = self.bsc
            vbox.Add(motorPanel, flag=wx.LEFT | wx.TOP | wx.ALIGN_LEFT, border=0, proportion=0)
            vbox.Add((-1, 2))
            sl = wx.StaticLine(self)
            vbox.Add(sl, flag=wx.EXPAND, border=0, proportion=0)
            vbox.Add((-1, 2))

        self.SetSizer(vbox)


class BSC203Panel(wx.Panel):

    def __init__(self, parent, axis):
        super(BSC203Panel, self).__init__(parent)
        self.parent = parent
        self.axis = axis
        self.InitUI()

    def InitUI(self):

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        if self.axis == 1:
            st1 = wx.StaticText(self, label='X')
            hbox.Add(st1, flag=wx.ALIGN_LEFT, border=8)
        if self.axis == 2:
            st1 = wx.StaticText(self, label='Y')
            hbox.Add(st1, flag=wx.ALIGN_LEFT, border=8)
        if self.axis == 3:
            st1 = wx.StaticText(self, label='Z')
            hbox.Add(st1, flag=wx.ALIGN_LEFT, border=8)
        st1 = wx.StaticText(self, label='')
        hbox.Add(st1, flag=wx.EXPAND, border=8, proportion=1)
        btn1 = wx.Button(self, label='-', size=(50, 20))
        btn2 = wx.Button(self, label='+', size=(50, 20))

        self.initialvalue = 0
        if self.axis == 1:
            self.initialvalue = 100
        elif self.axis == 2:
            self.initialvalue = 100
        elif self.axis == 3:
            self.initialvalue = 0


        hbox.Add(btn1, flag=wx.EXPAND | wx.RIGHT, proportion=0, border=8)
        btn1.Bind(wx.EVT_BUTTON, self.OnButton_MinusButtonHandler)
        self.tc = wx.TextCtrl(self, value=str(self.initialvalue))  # change str(self.axis) to '0'

        hbox.Add(self.tc, proportion=2, flag=wx.EXPAND)
        st1 = wx.StaticText(self, label='um')
        hbox.Add(st1, flag=wx.ALIGN_LEFT, border=8)
        hbox.Add(btn2, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=8)
        btn2.Bind(wx.EVT_BUTTON, self.OnButton_PlusButtonHandler)
        self.SetSizer(hbox)

    def getMoveValue(self):
        try:
            val = float(self.tc.GetValue())
        except ValueError:
            self.tc.SetValue('0')
            print("Value Error")
            return 0.0
        print(val)
        return val

    def OnButton_MinusButtonHandler(self, event):

        if self.axis == 1:
            self.parent.bsc.moveRelativeXYZ(int(self.getMoveValue()), 0, 0)
            print("Axis 1 Moved Negative")

        if self.axis == 2:
            self.parent.bsc.moveRelativeXYZ(0, int(self.getMoveValue()), 0)
            print("Axis 2 Moved Negative")

        if self.axis == 3:
            self.parent.bsc.moveRelativeXYZ(0,0, int(self.getMoveValue()))
            print("Axis 3 Moved Negative")

    def OnButton_PlusButtonHandler(self, event):
        if self.axis == 1:
            self.parent.bsc.moveRelativeXYZ(int((-1)*self.getMoveValue()), 0, 0)
            print("Axis 1 Moved Positive")

        if self.axis == 2:
            self.parent.bsc.moveRelativeXYZ(0, int((-1) * self.getMoveValue()), 0)
            print("Axis 2 Moved Positive")

        if self.axis == 3:
            self.parent.bsc.moveRelativeXYZ(0,0, int((-1) * self.getMoveValue()))
            print("Axis 3 Moved Positive")
