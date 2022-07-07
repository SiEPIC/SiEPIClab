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
import os

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

        vboxOuter = wx.BoxSizer(wx.VERTICAL)

        smulabel = wx.StaticBox(self, label='SMU Control')

        vbox = wx.StaticBoxSizer(smulabel, wx.VERTICAL)
        #vbox = wx.BoxSizer(wx.VERTICAL)

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

        st4 = wx.StaticText(self, label='Voltage Reading (V): ')
        self.voltread = wx.StaticText(self, label="0")

        hbox4.AddMany([(st4, 1, wx.EXPAND), (self.voltread, 1, wx.EXPAND)])

        hbox5 = wx.BoxSizer(wx.HORIZONTAL)

        st5 = wx.StaticText(self, label='Current Reading (mA): ')
        self.currentread = wx.StaticText(self, label="0")

        hbox5.AddMany([(st5, 1, wx.EXPAND), (self.currentread, 1, wx.EXPAND)])

        hbox6 = wx.BoxSizer(wx.HORIZONTAL)

        st6 = wx.StaticText(self, label='Resistance (Ω): ')
        self.rread = wx.StaticText(self, label="0")

        hbox6.AddMany([(st6, 1, wx.EXPAND), (self.rread, 1, wx.EXPAND)])


        self.timer = wx.Timer(self, wx.ID_ANY)
        self.Bind(wx.EVT_TIMER, self.UpdateAutoMeasurement, self.timer)
        self.timer.Start(1000)


        vbox.AddMany([(hbox2, 1, wx.EXPAND), (hbox3, 0, wx.EXPAND), (hbox4, 1, wx.EXPAND), (hbox5, 0, wx.EXPAND), (hbox6, 0, wx.EXPAND)])


        sbSweep = wx.StaticBox(self, label='Sweep Settings');
        vboxSweep = wx.StaticBoxSizer(sbSweep, wx.VERTICAL)

        hbox1_1 = wx.BoxSizer(wx.HORIZONTAL)

        sw1 = wx.StaticText(self, label='Set Max. Voltage (V)')
        self.voltmaxset = wx.TextCtrl(self)
        self.voltmaxset.SetValue('0')

        hbox1_1.AddMany([(sw1, 1, wx.EXPAND), (self.voltmaxset, 1, wx.EXPAND)])

        hbox2_1 = wx.BoxSizer(wx.HORIZONTAL)

        sw2 = wx.StaticText(self, label='Set Min. Voltage (V)')
        self.voltminset = wx.TextCtrl(self)
        self.voltminset.SetValue('0')

        hbox2_1.AddMany([(sw2, 1, wx.EXPAND), (self.voltminset, 1, wx.EXPAND)])

        hbox3_1 = wx.BoxSizer(wx.HORIZONTAL)

        sw3 = wx.StaticText(self, label='Set Resolution')
        self.reso = wx.TextCtrl(self)
        self.reso.SetValue('0')

        hbox3_1.AddMany([(sw3, 1, wx.EXPAND), (self.reso, 1, wx.EXPAND)])

        st4_1 = wx.StaticText(self, label='Save folder:')
        hbox4_1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox4_1.Add(st4_1, proportion=1, flag=wx.EXPAND)
        ##
        self.outputFolderTb = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.outputFolderBtn = wx.Button(self, wx.ID_OPEN, size=(50, 20))
        self.outputFolderBtn.Bind(wx.EVT_BUTTON, self.OnButton_SelectOutputFolder)
        hbox4_2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox4_2.AddMany([(self.outputFolderTb, 1, wx.EXPAND), (self.outputFolderBtn, 0, wx.EXPAND)])


        hbox5_1 = wx.BoxSizer(wx.HORIZONTAL)

        self.sweepBtn = wx.Button(self, label='IV Sweep', size=(50, 20))
        self.sweepBtn.Bind(wx.EVT_BUTTON, self.OnButton_Sweep)

        hbox5_1.Add(self.sweepBtn, 1, wx.EXPAND)

        vboxSweep.AddMany([(hbox1_1, 1, wx.EXPAND), (hbox2_1, 0, wx.EXPAND), (hbox3_1, 0, wx.EXPAND), (hbox4_1, 0, wx.EXPAND), (hbox4_2, 0, wx.EXPAND), (hbox5_1, 0, wx.EXPAND)])


        vboxOuter.AddMany([(vbox, 0, wx.EXPAND), (vboxSweep, 0, wx.EXPAND)])

        self.SetSizer(vboxOuter)


        #self.SetSizer(vboxSweep)

    def OnButton_SelectOutputFolder(self, event):
        """ Opens a file dialog to select an output directory for automatic measurement. """
        dirDlg = wx.DirDialog(self, "Open", "", wx.DD_DEFAULT_STYLE)
        dirDlg.ShowModal()
        self.outputFolderTb.SetValue(dirDlg.GetPath())
        dirDlg.Destroy()

    def OnButton_Sweep(self, event):
        result = self.smu.ivsweep(float(self.voltminset.GetValue()), float(self.voltmaxset.GetValue()), float(self.reso.GetValue()))
        bufferfile = os.getcwd()
        print(bufferfile)
        bufferfile = bufferfile + '/ivSweepTestResults.txt'
        print(bufferfile)

        result.save(bufferfile) #saves contents of result table to a buffer file in working directory

        original = open(bufferfile, 'r')
        data = original.readlines() #read contents of buffer file

        savefile = self.outputFolderTb.GetValue()
        savefile = savefile + '/ivsweeptestresults.txt'

        target = open(savefile, 'w') #creates save folder
        target.writelines(data) #writes contents of buffer file to specifed save location

    def UpdateAutoMeasurement(self, event):
        v = self.smu.getvoltage()
        i = self.smu.getcurrent()
        self.voltread.SetLabel(str(int(v*1000)/1000))
        self.currentread.SetLabel(str(int(i*1e6)/1000))
        if v == 0:
            r = 'NA'
        elif i == 0:
            r = 'NA'
        else:
            r = v/i
        self.rread.SetLabel(str(int(r*1000)/1000))


    def OnButton_currentSet(self, event):
        self.smu.setCurrent((float(self.currentset.GetValue())/1e3))
        self.voltset.SetValue('')


    def OnButton_voltageSet(self, event):
        self.smu.setVoltage((float(self.voltset.GetValue())))
        self.currentset.SetValue('')

    def OnButton_currentlimitSet(self, event):
        pass


