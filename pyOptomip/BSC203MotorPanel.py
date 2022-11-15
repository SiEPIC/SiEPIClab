import wx


# Panel that appears in the main window which contains the controls for the Thorlabs motors.
class topBSC203MotorPanel(wx.Panel):
    def __init__(self, parent, motor):
        super(topBSC203MotorPanel, self).__init__(parent)
        self.bsc = motor
        self.numAxes = self.bsc.numAxes
        self.InitUI()

    def InitUI(self):
        sb = wx.StaticBox(self, label='BSC203')
        vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)

        for axis in range(0, self.numAxes):
            motorPanel = BSC203Panel(self, axis)
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
        st1 = wx.StaticText(self, label='Electrical Probing Control')
        hbox.Add(st1, flag=wx.ALIGN_LEFT, border=8)
        st1 = wx.StaticText(self, label='')
        hbox.Add(st1, flag=wx.EXPAND, border=8, proportion=1)
        if self.axis == 1:
            btn1 = wx.Button(self, label='Down', size=(80, 20))
            btn2 = wx.Button(self, label='Up', size=(80, 20))
        elif self.axis ==2:
            btn1 = wx.Button(self, label='Right', size=(80, 20))
            btn2 = wx.Button(self, label='Left', size=(80, 20))
        else:
            btn1 = wx.Button(self, label='Forwards', size=(80, 20))
            btn2 = wx.Button(self, label='Back', size=(80, 20))


        hbox.Add(btn1, flag=wx.EXPAND | wx.RIGHT, proportion=0, border=8)
        btn1.Bind(wx.EVT_BUTTON, self.OnButton_MinusButtonHandler)
        self.tc = wx.TextCtrl(self, value=str(self.axis))  # change str(self.axis) to '0'
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

        if self.axis == 2:
            self.parent.bsc.bsc.move_relative(distance=int((1000)*-1*self.getMoveValue()), channel=0)
            print("Axis 1 Moved")

        if self.axis == 1:
            self.parent.bsc.bsc.move_relative(distance=int((1000)*-1*self.getMoveValue()), bay=2, channel=0)
            print("Axis 2 Moved")

        if self.axis == 0:
            self.parent.bsc.bsc.move_relative(distance=int((1000)*-1*self.getMoveValue()), bay=1, channel=0)
            print("Axis 3 Moved")

    def OnButton_PlusButtonHandler(self, event):
        if self.axis == 2:
            self.parent.bsc.bsc.move_relative(distance=int((1000)*self.getMoveValue()), bay=0, channel=0)
            self.parent.bsc.bsc.identify()
            print("Axis 1 Moved")

        if self.axis == 1:
            self.parent.bsc.bsc.move_relative(distance=int((1000)*self.getMoveValue()), bay=2, channel=0)
            print("Axis 2 Moved")

        if self.axis == 0:
            self.parent.bsc.bsc.move_relative(distance=int((1000)*self.getMoveValue()), bay=1, channel=0)
            print("Axis 3 Moved")
