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
from hp816x_N77Det_instr import hp816x_N77Det
import laserPanel

# Panel in the Connect Instruments window which contains the connection settings for the hp816x 
# mainframe with the N77xx detector.
class hp816x_N77Det_instrParameters(wx.Panel):
    name='Laser: hp816x with N77 Detector'
    def __init__(self, parent, connectPanel, **kwargs):
        super(hp816x_N77Det_instrParameters, self).__init__(parent)
        self.connectPanel = connectPanel
        self.visaAddrLst = kwargs['visaAddrLst']
        self.InitUI()
        
        
    def InitUI(self):
        sb = wx.StaticBox(self, label='Agilent 816x With N77 Detector Parameters');
        vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        self.para1 = wx.BoxSizer(wx.HORIZONTAL)
        self.para1name = wx.StaticText(self,label='Mainframe Address')
        self.para1tc = wx.ComboBox(self, choices=self.visaAddrLst)
        #self.para1tc = wx.TextCtrl(self,value='GPIB0::20::INSTR')
        self.para1.AddMany([(self.para1name,1,wx.EXPAND),(self.para1tc,1,wx.EXPAND)])
        
        self.para2 = wx.BoxSizer(wx.HORIZONTAL)
        self.para2name = wx.StaticText(self,label='Detector Address')
        self.para2tc = wx.ComboBox(self, choices=self.visaAddrLst)
        #self.para2tc = wx.TextCtrl(self,value='GPIB0::20::INSTR')
        self.para2.AddMany([(self.para2name,1,wx.EXPAND),(self.para2tc,1,wx.EXPAND)])
        
        self.disconnectBtn = wx.Button(self, label='Disconnect')
        self.disconnectBtn.Bind( wx.EVT_BUTTON, self.disconnect)
        self.disconnectBtn.Disable()
        
        self.connectBtn = wx.Button(self, label='Connect')
        self.connectBtn.Bind( wx.EVT_BUTTON, self.connect)
        
        hbox.AddMany([(self.disconnectBtn, 0), (self.connectBtn, 0)])
        
        vbox.AddMany([(self.para1,0,wx.EXPAND), (self.para2,0,wx.EXPAND), (hbox, 0)])
        
        
        
        self.SetSizer(vbox)
        
        
    def connect(self, event):
        self.laser = hp816x_N77Det();
        self.laser.connect(self.para1tc.GetValue(), self.para2tc.GetValue(), reset=0, forceTrans=1)
        self.laser.panelClass = laserPanel.laserTopPanel # Give the laser its panel class
        self.connectPanel.instList.append(self.laser)
        self.disconnectBtn.Enable()
        self.connectBtn.Disable()
        
    def disconnect(self, event):
        self.laser.disconnect()
        if self.laser in self.connectPanel.instList:
            self.connectPanel.instList.remove(self.laser)
        self.disconnectBtn.Disable()
        self.connectBtn.Enable()
         
