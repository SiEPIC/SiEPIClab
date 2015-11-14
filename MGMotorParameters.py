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

import MGMotorPanel
from MGMotor_inst import MGMotor

# Panel in the Connect Instruments window which contains the connection settings for the MG motor.
class MGMotorParameters(wx.Panel):
    name='Stage: Thorlabs BBD203'
    def __init__(self, parent, connectPanel, **kwargs):
        super(MGMotorParameters, self).__init__(parent)
        self.connectPanel = connectPanel
        self.InitUI()   

    def InitUI(self):
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        fgs = wx.FlexGridSizer(3, 2, 8, 25)
        
        st1 = wx.StaticText(self, label='Serial Number 1:')
        self.tc_serial1 = wx.TextCtrl(self, value = '94833200') 
        st2 = wx.StaticText(self, label='Serial Number 2:')
        self.tc_serial2 = wx.TextCtrl(self, value = '94833201') 
        
        self.disconnectBtn = wx.Button(self, label='Disconnect')
        self.disconnectBtn.Bind( wx.EVT_BUTTON, self.disconnect)
        self.disconnectBtn.Disable()
        
        self.connectBtn = wx.Button(self, label='Connect')
        self.connectBtn.Bind( wx.EVT_BUTTON, self.connect)
        
        fgs.AddMany([(st1, 1, wx.EXPAND), (self.tc_serial1, 1, wx.EXPAND),\
                     (st2, 1, wx.EXPAND), (self.tc_serial2, 1, wx.EXPAND),
                     (self.disconnectBtn, 0, wx.ALIGN_BOTTOM),(self.connectBtn, 0, wx.ALIGN_BOTTOM)])
        fgs.AddGrowableCol(1,2)
        hbox.Add(fgs, proportion=1, flag=wx.EXPAND)
        self.SetSizer(hbox)
        
    def connect(self, event):
        serialNumList = []
        serial1 = self.tc_serial1.GetValue()
        serial2 = self.tc_serial2.GetValue()
        if serial1 != '':
            serialNumList.append(serial1)
        if serial2 != '':
            serialNumList.append(serial2)
        
        self.stage = MGMotor(serialNumList);
        self.stage.panelClass = MGMotorPanel.topMGMotorPanel # Give the laser its panel class
        self.connectPanel.instList.append(self.stage)
        self.disconnectBtn.Enable()
        self.connectBtn.Disable()   
        
    def disconnect(self, event):
        self.stage.disconnect()
        if self.stage in self.connectPanel.instList:
            self.connectPanel.instList.remove(self.stage)
        self.disconnectBtn.Disable()
        self.connectBtn.Enable()   