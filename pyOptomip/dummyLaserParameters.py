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

from hp816x_instr import hp816x
import laserPanel

class dummyLaserParameters(wx.Panel):
    name='Dummy laser'
    def __init__(self, parent, connectPanel, **kwargs):
        super(dummyLaserParameters, self).__init__(parent)
        self.connectPanel = connectPanel
        self.InitUI()   

    def InitUI(self):
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        fgs = wx.FlexGridSizer(2, 2, 8, 25)
        
        st1 = wx.StaticText(self, label='Mainframe address:')
        self.tc_address = wx.TextCtrl(self, value = 'GPIB0::20::INSTR') 
        
        
        self.connectBtn = wx.Button(self, label='Connect')
        self.connectBtn.Bind( wx.EVT_BUTTON, self.connect)
        
        fgs.AddMany([(st1, 1, wx.EXPAND), (self.tc_address, 1, wx.EXPAND),
                     (0,0),(self.connectBtn, 0, wx.ALIGN_BOTTOM)])
        fgs.AddGrowableCol(1,2)
        hbox.Add(fgs, proportion=1, flag=wx.EXPAND)
        self.SetSizer(hbox)
        
    def connect(self, event):
        laser = hp816x()
        laser.pwmSlotIndex = [0,1]
        laser.pwmSlotMap = [(0,0),(1,0)]
        laser.panelClass = laserPanel.laserTopPanel # Give the laser its panel class
        def dummyNumPanels(self):
            return 3
        funcType =type(laser.getNumPWMChannels)
        
        laser.getNumPWMChannels = funcType(dummyNumPanels, laser, hp816x)
        self.connectPanel.instList.append(laser)