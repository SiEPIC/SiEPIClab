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


class topQontrolMotorPanel(wx.Panel):
    def __init__(self, parent, motor):
        super(topQontrolMotorPanel, self).__init__(parent)
        self.motor = motor;
        self.InitUI()

    def InitUI(self):
        sb = wx.StaticBox(self, label='Motor');
        vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)

        for motorCtrl in self.motor.motorLst:
            motorPanel = QontrolMotorPanel(self, motorCtrl)
            vbox.Add(motorPanel, flag=wx.LEFT | wx.TOP | wx.ALIGN_LEFT, border=0, proportion=0)
            vbox.Add((-1, 2))
            sl = wx.StaticLine(self);
            vbox.Add(sl, flag=wx.EXPAND, border=0, proportion=0)
            vbox.Add((-1, 2))

        self.SetSizer(vbox)


# Panel that appears in the main window which contains the controls for the MG motor.
class QontrolMotorPanel(wx.Panel):

    def __init__(self, parent, motorCtrl):
        super(QontrolMotorPanel, self).__init__(parent)
        self.motorCtrl = motorCtrl;
        self.InitUI()

    def InitUI(self):
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(self, label='Motor')
        hbox.Add(st1, flag=wx.ALIGN_LEFT, border=8)
        st1 = wx.StaticText(self, label='')
        hbox.Add(st1, flag=wx.EXPAND, border=8, proportion=1)
        btn1 = wx.Button(self, label='-', size=(20, 20))
        hbox.Add(btn1, flag=wx.EXPAND | wx.RIGHT, proportion=1, border=8)
        btn1.Bind(wx.EVT_BUTTON, self.OnButton_MinusButtonHandler)

        self.tc = wx.TextCtrl(self, value='0')
        hbox.Add(self.tc, proportion=2, flag=wx.EXPAND)

        st1 = wx.StaticText(self, label='um')
        hbox.Add(st1, flag=wx.ALIGN_LEFT, border=8)

        btn2 = wx.Button(self, label='+', size=(20, 20))
        hbox.Add(btn2, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=8)
        btn2.Bind(wx.EVT_BUTTON, self.OnButton_PlusButtonHandler)
        self.SetSizer(hbox);

    def getMoveValue(self):
        try:
            val = float(self.tc.GetValue());
        except ValueError:
            self.tc.SetValue('0');
            return 0.0;
        return val;

    def OnButton_MinusButtonHandler(self, event):
        self.motorCtrl.moveRelative(-self.getMoveValue());

    def OnButton_PlusButtonHandler(self, event):
        self.motorCtrl.moveRelative(self.getMoveValue());