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
import myMatplotlibPanel
import wx
import csv
import numpy as np
from keithley2600 import Keithley2600
from SMU import SMUClass


# Panel that appears in the main window which contains the controls for the Corvus motor.
class topSMUPanel(wx.Panel):
    def __init__(self, parent, smu):
        super(topSMUPanel, self).__init__(parent)
        self.smu = smu
        self.InitUI()

    def InitUI(self):
        sb = wx.StaticBox(self, label='SMU')
        hbox = wx.StaticBoxSizer(sb, wx.HORIZONTAL)
        #vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox2 = wx.BoxSizer(wx.VERTICAL)

        self.graph = myMatplotlibPanel.myMatplotlibPanel(self)
        hbox.Add(self.graph, flag=wx.EXPAND, border=0, proportion=1)

        SMUpanel = SMUPanel(self, self.graph)
        SMUpanel.smu = self.smu
        vbox.Add(SMUpanel, flag=wx.LEFT | wx.TOP | wx.ALIGN_LEFT, border=0, proportion=0)
        vbox.Add((-1, 2))
        sl = wx.StaticLine(self)
        vbox.Add(sl, flag=wx.EXPAND, border=0, proportion=0)
        vbox.Add((-1, 2))

        hbox.Add(vbox, flag=wx.EXPAND, border=0, proportion=1)

        self.SetSizer(hbox)


class SMUPanel(wx.Panel):

    def __init__(self, parent, graph):
        super(SMUPanel, self).__init__(parent)
        self.graphPanel = graph
        self.InitUI()
        self.plotflag = 'A'
        self.dependantA = []
        self.dependantB = []

    def InitUI(self):

        vboxOuter = wx.BoxSizer(wx.VERTICAL)

        smulabel = wx.StaticBox(self, label='SMU Control')

        vbox = wx.StaticBoxSizer(smulabel, wx.VERTICAL)
        #vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(self, label='Select SMU Output')
        self.smuasel = wx.CheckBox(self, label='A', pos=(20, 20))
        self.smuasel.SetValue(False)
        self.smubsel = wx.CheckBox(self, label='B', pos=(20, 20))
        self.smubsel.SetValue(False)
        self.btn_outputtoggle = wx.Button(self, label='ON/OFF', size=(50, 20))
        self.btn_outputtoggle.Bind(wx.EVT_BUTTON, self.OnButton_outputToggle)

        hbox1.AddMany([(st1, 1, wx.EXPAND), (self.smuasel, 1, wx.EXPAND), (self.smubsel, 1, wx.EXPAND), (self.btn_outputtoggle, 1, wx.EXPAND)])

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




        hbox3_5 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(self, label='Set Voltage limit (V)')
        self.voltlim = wx.TextCtrl(self)
        self.voltlim.SetValue('0')
        self.btn_voltagelim = wx.Button(self, label='Set', size=(50, 20))
        self.btn_voltagelim.Bind(wx.EVT_BUTTON, self.OnButton_voltagelim)

        hbox3_5.AddMany([(st2, 1, wx.EXPAND), (self.voltlim, 1, wx.EXPAND), (self.btn_voltagelim, 1, wx.EXPAND)])

        hbox3_75 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(self, label='Set Current limit (mA)')
        self.currentlim = wx.TextCtrl(self)
        self.currentlim.SetValue('0')
        self.btn_currentlim = wx.Button(self, label='Set', size=(50, 20))
        self.btn_currentlim.Bind(wx.EVT_BUTTON, self.OnButton_currentlim)

        hbox3_75.AddMany([(st2, 1, wx.EXPAND), (self.currentlim, 1, wx.EXPAND), (self.btn_currentlim, 1, wx.EXPAND)])

        hbox3_85 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(self, label='Set Power limit (mW)')
        self.powerlim = wx.TextCtrl(self)
        self.powerlim.SetValue('0')
        self.btn_powerlim = wx.Button(self, label='Set', size=(50, 20))
        self.btn_powerlim.Bind(wx.EVT_BUTTON, self.OnButton_powerlim)

        hbox3_85.AddMany([(st2, 1, wx.EXPAND), (self.powerlim, 1, wx.EXPAND), (self.btn_powerlim, 1, wx.EXPAND)])

        hbox3_9 = wx.BoxSizer(wx.HORIZONTAL)

        sp4_1 = wx.StaticText(self, label='                                                Channel A ')

        sp4_2 = wx.StaticText(self, label='                         Channel B ')

        hbox3_9.AddMany([(sp4_1, 1, wx.EXPAND),  (sp4_2, 1, wx.EXPAND)])


        hbox4 = wx.BoxSizer(wx.HORIZONTAL)

        st4 = wx.StaticText(self, label='Voltage Reading (V): ')

        self.voltreadA = wx.StaticText(self, label="0")
        self.voltreadB = wx.StaticText(self, label="0")

        hbox4.AddMany([(st4, 1, wx.EXPAND), (self.voltreadA, 1, wx.EXPAND), (self.voltreadB, 1, wx.EXPAND)])

        hbox5 = wx.BoxSizer(wx.HORIZONTAL)

        st5 = wx.StaticText(self, label='Current Reading (mA): ')
        self.currentreadA = wx.StaticText(self, label="0")
        self.currentreadB = wx.StaticText(self, label="0")

        hbox5.AddMany([(st5, 1, wx.EXPAND), (self.currentreadA, 1, wx.EXPAND), (self.currentreadB, 1, wx.EXPAND)])

        hbox6 = wx.BoxSizer(wx.HORIZONTAL)

        st6 = wx.StaticText(self, label='Resistance (Ω): ')
        self.rreadA = wx.StaticText(self, label="0")
        self.rreadB = wx.StaticText(self, label="0")

        hbox6.AddMany([(st6, 1, wx.EXPAND), (self.rreadA, 1, wx.EXPAND), (self.rreadB, 1, wx.EXPAND)])

        self.timer = wx.Timer(self, wx.ID_ANY)
        self.Bind(wx.EVT_TIMER, self.UpdateAutoMeasurement, self.timer)
        self.timer.Start(1000)


        vbox.AddMany([(hbox1, 1, wx.EXPAND), (hbox2, 1, wx.EXPAND), (hbox3, 0, wx.EXPAND),(hbox3_5, 0, wx.EXPAND), (hbox3_75, 0, wx.EXPAND), (hbox3_85, 1, wx.EXPAND), (hbox3_9, 0, wx.EXPAND), (hbox4, 1, wx.EXPAND), (hbox5, 0, wx.EXPAND), (hbox6, 0, wx.EXPAND)])


        sbSweep = wx.StaticBox(self, label='Sweep Settings');
        vboxSweep = wx.StaticBoxSizer(sbSweep, wx.VERTICAL)

        hbox1_2 = wx.BoxSizer(wx.HORIZONTAL)
        st1_1 = wx.StaticText(self, label='Select SMU Output')
        self.smua2sel = wx.CheckBox(self, label='A', pos=(20, 20))
        self.smua2sel.SetValue(False)
        self.smub2sel = wx.CheckBox(self, label='B', pos=(20, 20))
        self.smub2sel.SetValue(False)
        self.btn_outputtoggle = wx.Button(self, label='Set', size=(50, 20))
        self.btn_outputtoggle.Bind(wx.EVT_BUTTON, self.OnButton_outputTogglesweep)

        hbox1_2.AddMany([(st1_1, 1, wx.EXPAND), (self.smua2sel, 1, wx.EXPAND), (self.smub2sel, 1, wx.EXPAND), (self.btn_outputtoggle, 1, wx.EXPAND)])


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




        hbox4_3 = wx.BoxSizer(wx.HORIZONTAL)

        sc2 = wx.StaticText(self, label='Plot Selection')
        self.plotsel = wx.CheckBox(self, label='A', pos=(20, 20))
        self.plotsel.SetValue(False)
        self.plotsel.Bind(wx.EVT_CHECKBOX, self.PlotselectBtn)
        self.plot2sel = wx.CheckBox(self, label='B', pos=(20, 20))
        self.plot2sel.SetValue(False)
        self.plot2sel.Bind(wx.EVT_CHECKBOX, self.PlotselectBtn)

        hbox4_3.AddMany([(sc2, 1, wx.EXPAND), (self.plotsel, 1, wx.EXPAND), (self.plot2sel, 1, wx.EXPAND)])

        hbox4_4 = wx.BoxSizer(wx.HORIZONTAL)

        sh2 = wx.StaticText(self, label='Plot Type')
        self.typesel = wx.CheckBox(self, label='IV', pos=(20, 20))
        self.typesel.SetValue(False)
        self.typesel.Bind(wx.EVT_CHECKBOX, self.typeselectBtn)
        self.type2sel = wx.CheckBox(self, label='RV', pos=(20, 20))
        self.type2sel.SetValue(False)
        self.type2sel.Bind(wx.EVT_CHECKBOX, self.typeselectBtn)
        self.type3sel = wx.CheckBox(self, label='PV', pos=(20, 20))
        self.type3sel.SetValue(False)
        self.type3sel.Bind(wx.EVT_CHECKBOX, self.typeselectBtn)

        hbox4_4.AddMany([(sh2, 1, wx.EXPAND), (self.typesel, 1, wx.EXPAND), (self.type2sel, 1, wx.EXPAND), (self.type3sel, 1, wx.EXPAND)])



        hbox5_1 = wx.BoxSizer(wx.HORIZONTAL)

        self.sweepBtn = wx.Button(self, label='IV Sweep', size=(50, 20))
        self.sweepBtn.Bind(wx.EVT_BUTTON, self.OnButton_Sweep)

        hbox5_1.Add(self.sweepBtn, 1, wx.EXPAND)

        vboxSweep.AddMany([(hbox1_2, 1, wx.EXPAND), (hbox1_1, 1, wx.EXPAND), (hbox2_1, 0, wx.EXPAND), (hbox3_1, 0, wx.EXPAND), (hbox4_1, 0, wx.EXPAND), (hbox4_2, 0, wx.EXPAND), (hbox4_3, 0, wx.EXPAND), (hbox4_4, 0, wx.EXPAND), (hbox5_1, 0, wx.EXPAND)])

        vboxOuter.AddMany([(vbox, 0, wx.EXPAND), (vboxSweep, 0, wx.EXPAND)])

        self.SetSizer(vboxOuter)

    def OnButton_SelectOutputFolder(self, event):
        """ Opens a file dialog to select an output directory for automatic measurement. """
        dirDlg = wx.DirDialog(self, "Open", "", wx.DD_DEFAULT_STYLE)
        dirDlg.ShowModal()
        self.outputFolderTb.SetValue(dirDlg.GetPath())
        dirDlg.Destroy()


    def OnButton_Sweep(self, event):

        if self.outputFolderTb.GetValue()== '':
            print("Please select save file location")
            return

        print('Commencing Sweep...')

        self.smu.ivsweep(float(self.voltminset.GetValue()), float(self.voltmaxset.GetValue()), float(self.reso.GetValue()))


        savefile = self.outputFolderTb.GetValue()
        savefile = savefile + '/ivsweeptestresults.csv'

        headers = ["Voltage (V)", "Current (A)", "Resistance (Ω)", "Power (W)"]


        row = []
        for c in range(int(self.reso.GetValue())):
            row_2 = []
            row_2.append(str(self.smu.voltageresultA[c]))
            row_2.append(str(self.smu.currentresultA[c]))
            row_2.append(str(self.smu.resistanceresultA[c]))
            row_2.append(str(self.smu.powerresultA[c]))
            row_2.append(' ')
            row_2.append(str(self.smu.voltageresultB[c]))
            row_2.append(str(self.smu.currentresultB[c]))
            row_2.append(str(self.smu.resistanceresultB[c]))
            row_2.append(str(self.smu.powerresultB[c]))
            row.append(row_2)



        if self.smu.Aflag and self.smu.Bflag:
            with open(savefile, 'w', newline='') as f:
                f.write('Channel A Results,,,,,Channel B Results\n')
                f.write('Voltage (V), Current (A), Resistance (R), Power (W)')
                f.write(',,')
                f.write('Voltage (V), Current (A), Resistance (R), Power (W)\n')

                writer = csv.writer(f, delimiter=',')
                for c in range(int(self.reso.GetValue())):
                    writer.writerow(row[c])




                #f.write('Current (A),')
                #writer.writerow(self.smu.currentresultA)
                #f.write('Resistance (A),')
                #writer.writerow(self.smu.currentresultA)
                #f.write('Current (A),')
                #writer.writerow(self.smu.currentresultA)

                #f.write('\n')

                #f.write('Channel B Results\n')
                #f.write('Voltage (V),')
                #writer = csv.writer(f, delimiter=',')
                #writer.writerow(self.smu.voltageresultB)
                #f.write('Current (A),')
                #writer.writerow(self.smu.currentresultB)

        elif self.smu.Aflag:
            with open(savefile, 'w') as f:
                f.write('Channel A Results\n')
                f.write('Voltage (V),')
                writer = csv.writer(f, delimiter=',')
                writer.writerow(self.smu.voltageresultA)
                f.write('Current (A),')
                writer.writerow(self.smu.currentresultA)

        elif self.smu.Bflag:
            with open(savefile, 'w') as f:
                f.write('Channel B Results\n')
                f.write('Voltage (V),')
                writer = csv.writer(f, delimiter=',')
                writer.writerow(self.smu.voltageresultB)
                f.write('Current (A),')
                writer.writerow(self.smu.currentresultB)

        self.voltageA = self.smu.voltageresultA
        self.currentA = self.smu.currentresultA
        self.voltageB = self.smu.voltageresultB
        self.currentB = self.smu.currentresultB

        if self.plotflag == 'A':
            self.graphPanel.canvas.sweepResultDict = {}
            self.graphPanel.canvas.sweepResultDict['voltage'] = self.voltageA
            self.graphPanel.canvas.sweepResultDict['current'] = self.currentA
            self.drawGraph(self.voltageA, self.currentA)

        if self.plotflag == 'B':
            self.graphPanel.canvas.sweepResultDict = {}
            self.graphPanel.canvas.sweepResultDict['voltage'] = self.voltageA
            self.graphPanel.canvas.sweepResultDict['current'] = self.currentA
            self.drawGraph(self.voltageB, self.currentB)


    def drawGraph(self, voltage, current):
        self.graphPanel.axes.cla()
        self.graphPanel.axes.plot(voltage, current)
        self.graphPanel.axes.ticklabel_format(useOffset=False)
        self.graphPanel.canvas.draw()


    def UpdateAutoMeasurement(self, event):
        va = self.smu.getvoltageA()
        ia = self.smu.getcurrentA()
        va = float(va)
        ia = float(ia)
        self.voltreadA.SetLabel(str(va))
        self.currentreadA.SetLabel(str(ia))

        vb = self.smu.getvoltageB()
        ib = self.smu.getcurrentB()
        vb = float(vb)
        ib = float(ib)
        self.voltreadB.SetLabel(str(vb))
        self.currentreadB.SetLabel(str(ib))

        #self.voltread.SetLabel(str(int(v*1000)/1000))
        #self.currentread.SetLabel(str(int(i*1e6)/1000))
        ra = va/ia
        rb = vb/ia

        self.rreadA.SetLabel(str(int(ra*1000)/1000))
        self.rreadB.SetLabel(str(int(rb * 1000) / 1000))


    def OnButton_currentSet(self, event):
        self.smu.setCurrent((float(self.currentset.GetValue())/1e3),self.smuasel.GetValue(), self.smubsel.GetValue())
        self.voltset.SetValue('')


    def OnButton_voltageSet(self, event):
        self.smu.setVoltage((float(self.voltset.GetValue())), self.smuasel.GetValue(), self.smubsel.GetValue())
        self.currentset.SetValue('')


    def OnButton_currentlim(self, event):
        self.smu.setcurrentlimit(float(self.currentlim.GetValue()), self.smuasel.GetValue(), self.smubsel.GetValue())


    def OnButton_voltagelim(self, event):
        self.smu.setvoltagelimit(float(self.voltlim.GetValue()), self.smuasel.GetValue(), self.smubsel.GetValue())


    def OnButton_powerlim(self, event):
        self.smu.setpowerlimit(float(self.powerlim.GetValue()), self.smuasel.GetValue(), self.smubsel.GetValue())


    def OnButton_outputToggle(self, event):

        if self.smuasel.GetValue() == True:
            self.smu.turnchannelon(True, False)
        if self.smuasel.GetValue() == False:
            self.smu.turnchanneloff(True, False)
        if self.smubsel.GetValue() == True:
            self.smu.turnchannelon(False, True)
        if self.smubsel.GetValue() == False:
            self.smu.turnchanneloff(False, True)


    def OnButton_outputTogglesweep(self, event):

        if self.smua2sel.GetValue() == False and self.smub2sel.GetValue() == False:
            print("Please select an output")
        if self.smua2sel.GetValue() == True and self.smub2sel.GetValue() == True:
            self.smu.setoutputflag(True, True)
        if self.smua2sel.GetValue() == True and self.smub2sel.GetValue() == False:
            self.smu.setoutputflag(True, False)
        if self.smua2sel.GetValue() == False and self.smub2sel.GetValue() == True:
            self.smu.setoutputflag(False, True)


    def onChecked(self, e):
        cb = e.GetEventObject()

        label = cb.GetLabel()
        value = cb.GetValue()

        if label == 'A' and value:
            self.smu.turnchannelon(True, False)

        if label == 'A' and not value:
            self.smu.turnchanneloff(True, False)

        if label == 'B' and value:
            self.smu.turnchannelon(False, True)

        if label == 'B' and not value:
            self.smu.turnchanneloff(False, True)

        print(cb.GetLabel())
        print(cb.GetValue())
        #if cb.label is A


    def PlotselectBtn(self, event):

        c = event.GetEventObject()
        label = c.GetLabel()

        if self.dependantA==[] and self.dependantB==[]:
            print('Please select plot type')
            return

        if self.plotsel.GetValue() and self.plot2sel.GetValue():
            if label == "A":
                self.plot2sel.SetValue(False)
                self.plotflag = 'A'
                self.Plot(self.voltageA, self.dependantA)
            if label == "B":
                self.plotsel.SetValue(False)
                self.plotflag = 'B'
                self.Plot(self.voltageB, self.dependantB)

        elif self.plotsel.GetValue() and self.plot2sel.GetValue()==False:
            self.plot2sel.SetValue(False)
            self.plotflag = 'A'
            self.Plot(self.voltageA, self.dependantA)

        elif self.plot2sel.GetValue() and self.plotsel.GetValue()==False:
            self.plotsel.SetValue(False)
            self.plotflag = 'B'
            self.Plot(self.voltageB, self.dependantB)


    def Plot(self, voltage, dependant):

        self.graphPanel.canvas.sweepResultDict = {}
        self.graphPanel.canvas.sweepResultDict['xaxis'] = voltage
        self.graphPanel.canvas.sweepResultDict['yaxis'] = dependant

        self.drawGraph(voltage, dependant)


    def typeselectBtn(self, event):

        cb = event.GetEventObject()
        label = cb.GetLabel()
        value = cb.GetValue()

        if label=='RV' and value==True:
            self.typesel.SetValue(False)
            self.type3sel.SetValue(False)
            self.dependantA = self.smu.resistanceresultA
            self.dependantB = self.smu.resistanceresultB
            if self.plotflag=='A':
                self.Plot(self.voltageA, self.dependantA)
            if self.plotflag=='B':
                self.Plot(self.voltageB, self.dependantB)

        if label=='IV' and value==True:
            self.type2sel.SetValue(False)
            self.type3sel.SetValue(False)
            self.dependantA = self.smu.currentresultA
            self.dependantB = self.smu.currentresultB
            if self.plotflag=='A':
                self.Plot(self.voltageA, self.dependantA)
            if self.plotflag=='B':
                self.Plot(self.voltageB, self.dependantB)

        if label=='PV' and value==True:
            self.typesel.SetValue(False)
            self.type2sel.SetValue(False)
            self.dependantA = self.smu.powerresultA
            self.dependantB = self.smu.powerresultB
            if self.plotflag == 'A':
                self.Plot(self.voltageA, self.dependantA)
            if self.plotflag == 'B':
                self.Plot(self.voltageB, self.dependantB)


