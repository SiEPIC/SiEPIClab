# The MIT License (MIT)

# Copyright (c) 2015 Michael Caverley

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import wx


# Panel that appears in the main window which contains the controls for the Qontrol motors.
class topQontrolMotorPanel(wx.Panel):
    def __init__(self, parent, motor):
        super(topQontrolMotorPanel, self).__init__(parent)
        self.qontrol = motor
        self.numAxes = self.qontrol.numAxes
        self.maxAxis = self.numAxes + 1
        self.InitUI()

    def InitUI(self):
        sb = wx.StaticBox(self, label='Qontrol')
        vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)

        axis = 1
        for motorCtrl in range(axis, self.maxAxis):
            motorPanel = QontrolPanel(self, motorCtrl, axis)
            motorPanel.motor = self.qontrol
            vbox.Add(motorPanel, flag=wx.LEFT | wx.TOP | wx.ALIGN_LEFT, border=0, proportion=0)
            vbox.Add((-1, 2))
            sl = wx.StaticLine(self)
            vbox.Add(sl, flag=wx.EXPAND, border=0, proportion=0)
            vbox.Add((-1, 2))
            axis = axis + 1

        self.SetSizer(vbox)


class QontrolPanel(wx.Panel):

    def __init__(self, parent, motorCtrl, axis):
        super(QontrolPanel, self).__init__(parent)
        self.parent = parent
        self.motorCtrl = motorCtrl
        self.axis = axis
        self.InitUI()

    def InitUI(self):

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(self, label='Electrical Probing Control')
        hbox.Add(st1, flag=wx.ALIGN_LEFT, border=8)
        st1 = wx.StaticText(self, label='')
        hbox.Add(st1, flag=wx.EXPAND, border=8, proportion=1)
        btn1 = wx.Button(self, label='-', size=(20, 20))
        hbox.Add(btn1, flag=wx.EXPAND | wx.RIGHT, proportion=0, border=8)
        btn1.Bind(wx.EVT_BUTTON, self.OnButton_MinusButtonHandler)

        self.tc = wx.TextCtrl(self, value=str(self.axis))  # change str(self.axis) to '0'
        hbox.Add(self.tc, proportion=2, flag=wx.EXPAND)

        st1 = wx.StaticText(self, label='um')
        hbox.Add(st1, flag=wx.ALIGN_LEFT, border=8)

        btn2 = wx.Button(self, label='+', size=(20, 20))
        hbox.Add(btn2, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=8)
        btn2.Bind(wx.EVT_BUTTON, self.OnButton_PlusButtonHandler)
        self.SetSizer(hbox);

    def getMoveValue(self):
        try:
            val = float(self.tc.GetValue())
        except ValueError:
            self.tc.SetValue('0')
            return 0.0
        return val

    def OnButton_MinusButtonHandler(self, event):

        if self.axis == 1:
            current_position = self.parent.qontrol.q.x[0]
            self.parent.qontrol.q.x[0] = (-1 * (current_position+self.getMoveValue()))
            print("Axis 1 Moved")

        if self.axis == 2:
            current_position = self.parent.qontrol.q.x[1]
            self.parent.qontrol.q.x[1] = (-1 * (current_position + self.getMoveValue()))
            print("Axis 2 Moved")

        if self.axis == 3:
            current_position = self.parent.qontrol.q.x[2]
            self.parent.qontrol.q.x[2] = (-1 * (current_position + self.getMoveValue()))
            print("Axis 3 Moved")

    def OnButton_PlusButtonHandler(self, event):

        if self.axis == 1:
            current_position = self.parent.qontrol.q.x[0]
            self.parent.qontrol.q.x[0] = (current_position + self.getMoveValue())
            print("Axis 1 Moved")
        if self.axis == 2:
            current_position = self.parent.qontrol.q.x[1]
            self.parent.qontrol.q.x[1] = (current_position + self.getMoveValue())
            print("Axis 2 Moved")
        if self.axis == 3:
            current_position = self.parent.qontrol.q.x[2]
            self.parent.qontrol.q.x[2] = (current_position + self.getMoveValue())
            print("Axis 3 Moved")
