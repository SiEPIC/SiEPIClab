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

# Panel that appears in the main window which contains the controls for the Corvus motor.
class topCorvusPanel(wx.Panel):
    def __init__(self, parent, motor):
        super(topCorvusPanel, self).__init__(parent)
        self.motor = motor;
        self.maxaxis= motor.NumberOfAxis+1
        self.InitUI()
        
        
    def InitUI(self):
        sb = wx.StaticBox(self, label='Corvus');
        vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)
        
        axis = 1
        for motorCtrl in range(axis,self.maxaxis):
            motorPanel = CorvusPanel(self, motorCtrl,axis)
            motorPanel.motor = self.motor
            vbox.Add(motorPanel, flag=wx.LEFT | wx.TOP | wx.ALIGN_LEFT, border=0, proportion=0)
            vbox.Add((-1, 2))
            sl = wx.StaticLine(self);
            vbox.Add(sl, flag=wx.EXPAND, border=0, proportion=0)
            vbox.Add((-1, 2))
            axis = axis + 1
    
        self.SetSizer(vbox)
    

class CorvusPanel(wx.Panel):
  
    def __init__(self, parent, motorCtrl,axis):
        super(CorvusPanel, self).__init__(parent)
        self.motorCtrl = motorCtrl;
        self.axis = axis;
        self.InitUI()
        
    def InitUI(self):
        

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(self, label='Motor Control')
        hbox.Add(st1, flag=wx.ALIGN_LEFT, border=8)
        st1 = wx.StaticText(self, label='')
        hbox.Add(st1, flag=wx.EXPAND, border=8, proportion=1)
        btn1 = wx.Button(self, label='-', size=(20, 20))
        hbox.Add(btn1,flag=wx.EXPAND|wx.RIGHT, proportion=0, border=8)
        btn1.Bind( wx.EVT_BUTTON, self.OnButton_MinusButtonHandler)


        self.tc = wx.TextCtrl(self, value = str(self.axis)) #change str(self.axis) to '0'
        hbox.Add(self.tc, proportion=2, flag=wx.EXPAND)

        st1 = wx.StaticText(self, label='um')
        hbox.Add(st1, flag=wx.ALIGN_LEFT, border=8)

        btn2 = wx.Button(self, label='+', size=(20, 20))
        hbox.Add(btn2, proportion=0, flag=wx.EXPAND|wx.LEFT | wx.RIGHT, border=8)
        btn2.Bind( wx.EVT_BUTTON, self.OnButton_PlusButtonHandler)
        self.SetSizer(hbox);
        
        
    def getMoveValue(self):
        try:
            val = float(self.tc.GetValue());
        except ValueError:
            self.tc.SetValue('0');
            return 0.0;
        return val;
  
  
    def OnButton_MinusButtonHandler(self, event):
        
        if self.axis == 1:
            self.motor.moveRelative(-1*self.getMoveValue());
            print "Axis 1 Moved"
            
        if self.axis == 2:
            self.motor.moveRelative(0,-1*self.getMoveValue());
            print"Axis 2 Moved"
        if self.axis == 3:
            self.motor.moveRelative(0,0,-1*self.getMoveValue());
            print "Axis 3 Moved"
        
    def OnButton_PlusButtonHandler(self, event):

        if self.axis == 1:
            self.motor.moveRelative(self.getMoveValue());
            print "Axis 1 Moved"
        if self.axis == 2:
            self.motor.moveRelative(0,self.getMoveValue());
            print"Axis 2 Moved"
        if self.axis == 3:
            self.motor.moveRelative(0,0,self.getMoveValue());
            print "Axis 3 Moved"