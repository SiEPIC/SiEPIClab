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
from keithley2600 import Keithley2600
from SMU import SMUClass


# Panel that appears in the main window which contains the controls for the Corvus motor.
class topSMUPanel(wx.Panel):
    def __init__(self, parent, smu):
        super(topSMUPanel, self).__init__(parent)
        self.smu = smu
        self.InitUI()

    def InitUI(self):
        sb = wx.StaticBox(self, label='SMU');
        vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)

        SMUpanel = SMUPanel(self)
        SMUpanel.smu = self.smu
        vbox.Add(SMUpanel, flag=wx.LEFT | wx.TOP | wx.ALIGN_LEFT, border=0, proportion=0)
        vbox.Add((-1, 2))
        sl = wx.StaticLine(self)
        vbox.Add(sl, flag=wx.EXPAND, border=0, proportion=0)
        vbox.Add((-1, 2))

        self.SetSizer(vbox)




class SMUPanel(wx.Panel):

    def __init__(self, parent):
        super(SMUPanel, self).__init__(parent)
        self.InitUI()

    def InitUI(self):

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(self, label='SMU Control')
        hbox1.Add(st1, flag=wx.ALIGN_LEFT, border=8)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(self, label='Set Voltage (V)')
        self.voltset = wx.TextCtrl(self)
        self.voltset.SetValue('0')
        self.btn_voltageset = wx.Button(self, label='Set', size=(50, 20))
        self.btn_voltageset.Bind(wx.EVT_BUTTON, self.OnButton_voltageSet)

        hbox2.AddMany([(st2, 1, wx.EXPAND), (self.voltset, 1, wx.EXPAND),(self.btn_voltageset, 1, wx.EXPAND)])

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)

        st3 = wx.StaticText(self, label='Set Current (mA)')
        self.currentset = wx.TextCtrl(self)
        self.currentset.SetValue('0')
        self.btn_currentset = wx.Button(self, label='Set', size=(50, 20))
        self.btn_currentset.Bind(wx.EVT_BUTTON, self.OnButton_currentSet)

        hbox3.AddMany([(st3, 1, wx.EXPAND), (self.currentset, 1, wx.EXPAND), (self.btn_currentset, 1, wx.EXPAND)])



        hbox4 = wx.BoxSizer(wx.HORIZONTAL)

        hbox45 = wx.BoxSizer(wx.HORIZONTAL)

        fgs = wx.FlexGridSizer(4, 2, 8, 25)

        st4 = wx.StaticText(self, label='Voltage Reading')
        self.voltread = wx.TextCtrl(self)
        self.voltread.SetValue('0')

        hbox45.AddMany([(st4, 1, wx.EXPAND), (self.voltread, 1, wx.EXPAND)])

        fgs.Add(hbox4, 1, wx.EXPAND)

        hbox4.Add(fgs, proportion=1, flag=wx.ALL, border=0)
        self.SetSizer(hbox4)



        #self.timer = wx.Timer(self, wx.ID_ANY)
        #self.Bind(wx.EVT_TIMER, SMUClass.getvoltage, self.timer)
        #self.timer.Start(1000)




        hbox5 = wx.BoxSizer(wx.HORIZONTAL)

        st5 = wx.StaticText(self, label='Current Reading')
        self.currentread = wx.TextCtrl(self)
        self.currentread.SetValue('0')
        self.currentread = wx.StaticText(self, label='1')
        # self.PowerSt.SetFont(font)
        hbox2.Add(self.currentread, proportion=0)




        hbox5.AddMany([(st5, 1, wx.EXPAND), (self.currentread, 1, wx.EXPAND)])

        vbox.AddMany([(hbox1, 0, wx.EXPAND), (hbox2, 1, wx.EXPAND), (hbox3, 0, wx.EXPAND), (hbox4, 0, wx.EXPAND), (hbox5, 0, wx.EXPAND)])

        self.SetSizer(vbox)

        #v = self.k.smua.measure.v()  # measures and returns the SMUA voltage
        #print(v)
        #i = self.k.smua.measure.i()  # measures current at SMUA
        #print(i)
        #SMUClass.setVoltage(1, 0.5, visaName)
        # SMUClass.setCurrent(1, 0.05, visaName)
        # k.apply_voltage(k.smua, 1)
        #v = self.k.smua.measure.v()  # measures and returns the SMUA voltage
       # print(v)
        #i = self.k.smua.measure.i()
       # print(i)

    def UpdateAutoMeasurement(self, event):
        self.smu.smua.measure
        v = self.k.smua.measure.v()
        panel.currentread.SetLabel(str(self.laser.readPWM(panel.slot, panel.chan)))


    def OnButton_currentSet(self, event):
        self.smu.setCurrent((float(self.currentset.GetValue())/1e3))
        self.smu.read_error_queue()

    def OnButton_voltageSet(self, event):
        self.smu.setVoltage((float(self.voltset.GetValue())))

    def OnButton_currentlimitSet(self, event):
        pass