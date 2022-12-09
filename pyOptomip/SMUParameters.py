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

import SMU
import SMUFrame
import pyvisa as visa
from keithley2600 import Keithley2600


# Panel in the Connect Instruments window which contains the connection settings for the SMU.
class SMUParameters(wx.Panel):
    name = 'Source Meter Unit'

    def __init__(self, parent, connectPanel, **kwargs):
        super(SMUParameters, self).__init__(parent)
        self.connectPanel = connectPanel
        self.InitUI()

    def InitUI(self):
        sb = wx.StaticBox(self, label='SMU Connection Parameters');
        vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # First Parameter: Serial Port
        self.para1 = wx.BoxSizer(wx.HORIZONTAL)
        self.para1name = wx.StaticText(self, label='Serial Port')
        self.para1tc = wx.ComboBox(self, choices=visa.ResourceManager().list_resources())
        for x in visa.ResourceManager().list_resources():
            if x == 'GPIB0::26::INSTR:':
                self.para1tc.SetValue('GPIB0::20::INSTR')
        # self.para1tc = wx.TextCtrl(self,value='ASRL5::INSTR')
        self.para1.AddMany([(self.para1name, 1, wx.EXPAND), (self.para1tc, 1, wx.EXPAND)])

        self.disconnectBtn = wx.Button(self, label='Disconnect')
        self.disconnectBtn.Bind(wx.EVT_BUTTON, self.disconnect)
        self.disconnectBtn.Disable()

        self.connectBtn = wx.Button(self, label='Connect')
        self.connectBtn.Bind(wx.EVT_BUTTON, self.connect)

        hbox.AddMany([(self.disconnectBtn, 0), (self.connectBtn, 0)])
        vbox.AddMany([(self.para1, 0, wx.EXPAND), (hbox, 0)])

        self.SetSizer(vbox)

    def connect(self, event):
        self.stage = SMU.SMUClass()
        self.stage.connect(str(self.para1tc.GetValue()), visa.ResourceManager())
        self.stage.panelClass = SMUFrame.topSMUPanel
        self.connectPanel.instList.append(self.stage)
        self.disconnectBtn.Enable()
        self.connectBtn.Disable()

    def disconnect(self, event):
        self.stage.disconnect()
        if self.stage in self.connectPanel.instList:
            self.connectPanel.instList.remove(self.stage)
        self.disconnectBtn.Disable()
        self.connectBtn.Enable()