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
import myMatplotlibPanel_pyplot
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
        """ Creates and compiles everything in electrical tab """


        #create boxsizer for entire electrical tab, label as SMU

        sb = wx.StaticBox(self, label='SMU')
        hbox = wx.StaticBoxSizer(sb, wx.HORIZONTAL)
        #vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)
        vbox = wx.BoxSizer(wx.VERTICAL)
        #vbox2 = wx.BoxSizer(wx.VERTICAL)

        self.graph = myMatplotlibPanel.myMatplotlibPanel(self) #use for regular mymatplotlib file
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
        self.plotflag = ''
        self.dependantA = []
        self.dependantB = []
        self.typeflag = 'IV'

    def InitUI(self):
        """ Creates SMU control panel layout """

        vboxOuter = wx.BoxSizer(wx.VERTICAL)

        smulabel = wx.StaticBox(self, label='SMU Control')

        vbox = wx.StaticBoxSizer(smulabel, wx.VERTICAL)

        #Select SMU output layout

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(self, label='Select SMU Output')
        selections = ['A','B', 'All']

        self.smusel = wx.ComboBox(self, choices=selections)



        #self.smuasel = wx.CheckBox(self, label='A', pos=(20, 20))
        #self.smuasel.SetValue(False)
        #self.smubsel = wx.CheckBox(self, label='B', pos=(20, 20))
        #self.smubsel.SetValue(False)
        self.btn_ontoggle = wx.Button(self, label='ON', size=(20, 20))
        self.btn_ontoggle.Bind(wx.EVT_BUTTON, self.OnButton_outputToggle)
        self.btn_offtoggle = wx.Button(self, label='OFF', size=(20, 20))
        self.btn_offtoggle.Bind(wx.EVT_BUTTON, self.OnButton_outputToggle)

        #hbox1.AddMany([(st1, 1, wx.EXPAND), (self.smuasel, 1, wx.EXPAND), (self.smubsel, 1, wx.EXPAND), (self.btn_outputtoggle, 1, wx.EXPAND)])
        hbox1.AddMany([(st1, 1, wx.EXPAND), (self.smusel, 1, wx.EXPAND), (self.btn_ontoggle, 1, wx.EXPAND), (self.btn_offtoggle, 1, wx.EXPAND)])
        #Set Voltage layout

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(self, label='Set Voltage (V)')
        self.voltset = wx.TextCtrl(self)
        self.voltset.SetValue('0')
        self.btn_voltageset = wx.Button(self, label='Set', size=(50, 20))
        self.btn_voltageset.Bind(wx.EVT_BUTTON, self.OnButton_voltageSet)

        hbox2.AddMany([(st2, 1, wx.EXPAND), (self.voltset, 1, wx.EXPAND),(self.btn_voltageset, 1, wx.EXPAND)])

        #Set current layout

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)

        st3 = wx.StaticText(self, label='Set Current (mA)')
        self.currentset = wx.TextCtrl(self)
        self.currentset.SetValue('0')
        self.btn_currentset = wx.Button(self, label='Set', size=(50, 20))
        self.btn_currentset.Bind(wx.EVT_BUTTON, self.OnButton_currentSet)

        hbox3.AddMany([(st3, 1, wx.EXPAND), (self.currentset, 1, wx.EXPAND), (self.btn_currentset, 1, wx.EXPAND)])

        #Set Voltage Limit layout

        hbox3_5 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(self, label='Set Voltage limit (V)')
        self.voltlim = wx.TextCtrl(self)
        self.voltlim.SetValue('0')
        self.btn_voltagelim = wx.Button(self, label='Set', size=(50, 20))
        self.btn_voltagelim.Bind(wx.EVT_BUTTON, self.OnButton_voltagelim)

        hbox3_5.AddMany([(st2, 1, wx.EXPAND), (self.voltlim, 1, wx.EXPAND), (self.btn_voltagelim, 1, wx.EXPAND)])

        #Set Current Limit Layout

        hbox3_75 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(self, label='Set Current limit (mA)')
        self.currentlim = wx.TextCtrl(self)
        self.currentlim.SetValue('0')
        self.btn_currentlim = wx.Button(self, label='Set', size=(50, 20))
        self.btn_currentlim.Bind(wx.EVT_BUTTON, self.OnButton_currentlim)

        hbox3_75.AddMany([(st2, 1, wx.EXPAND), (self.currentlim, 1, wx.EXPAND), (self.btn_currentlim, 1, wx.EXPAND)])

        #Set Power Limit layout

        hbox3_85 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(self, label='Set Power limit (mW)')
        self.powerlim = wx.TextCtrl(self)
        self.powerlim.SetValue('0')
        self.btn_powerlim = wx.Button(self, label='Set', size=(50, 20))
        self.btn_powerlim.Bind(wx.EVT_BUTTON, self.OnButton_powerlim)

        hbox3_85.AddMany([(st2, 1, wx.EXPAND), (self.powerlim, 1, wx.EXPAND), (self.btn_powerlim, 1, wx.EXPAND)])

        #Channel reading layout

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

        #Start new vbox for sweep settings

        sbSweep = wx.StaticBox(self, label='Sweep Settings');
        vboxSweep = wx.StaticBoxSizer(sbSweep, wx.VERTICAL)

        hbox11 = wx.BoxSizer(wx.HORIZONTAL)
        sq1_1 = wx.StaticText(self, label='Select Independant Variable')
        self.voltsel = wx.CheckBox(self, label='Voltage', pos=(20, 20))
        self.voltsel.SetValue(False)
        self.currentsel = wx.CheckBox(self, label='Current', pos=(20, 20))
        self.currentsel.SetValue(False)

        self.currentsel.Bind(wx.EVT_CHECKBOX, self.sweeptype)
        self.voltsel.Bind(wx.EVT_CHECKBOX, self.sweeptype)

        hbox11.AddMany([(sq1_1, 1, wx.EXPAND), (self.voltsel, 1, wx.EXPAND), (self.currentsel, 1, wx.EXPAND)])





        hbox1_2 = wx.BoxSizer(wx.HORIZONTAL)
        st1_1 = wx.StaticText(self, label='Select SMU Output')

        selections3 = ['A', 'B', 'All']

        self.smu2sel = wx.ComboBox(self, id=1, choices=selections3)
        self.smu2sel.Bind(wx.EVT_COMBOBOX, self.OnButton_outputTogglesweep)

        # self.smuasel = wx.CheckBox(self, label='A', pos=(20, 20))
        # self.smuasel.SetValue(False)
        # self.smubsel = wx.CheckBox(self, label='B', pos=(20, 20))
        # self.smubsel.SetValue(False


        #self.smua2sel = wx.CheckBox(self, label='A', pos=(20, 20))
        #self.smua2sel.SetValue(False)
        #self.smub2sel = wx.CheckBox(self, label='B', pos=(20, 20))
        #self.smub2sel.SetValue(False)
        #self.btn_outputtoggle = wx.Button(self, label='Set', size=(50, 20))
        #self.btn_outputtoggle.Bind(wx.EVT_BUTTON, self.OnButton_outputTogglesweep)

        hbox1_2.AddMany([(st1_1, 1, wx.EXPAND), (self.smu2sel, 1, wx.EXPAND)])


        hbox1_1 = wx.BoxSizer(wx.HORIZONTAL)

        sw1 = wx.StaticText(self, label='Set Max:')

        self.maxset = wx.TextCtrl(self)
        self.maxset.SetValue('0')
        self.maxunit = wx.StaticText(self, label="N/A")

        hbox1_1.AddMany([(sw1, 1, wx.EXPAND), (self.maxunit, 1, wx.EXPAND), (self.maxset, 1, wx.EXPAND)])

        hbox2_1 = wx.BoxSizer(wx.HORIZONTAL)

        sw2 = wx.StaticText(self, label='Set Min:')
        self.minset = wx.TextCtrl(self)
        self.minset.SetValue('0')
        self.minunit = wx.StaticText(self, label="N/A")

        hbox2_1.AddMany([(sw2, 1, wx.EXPAND), (self.minunit, 1, wx.EXPAND), (self.minset, 1, wx.EXPAND)])

        hbox3_1 = wx.BoxSizer(wx.HORIZONTAL)

        sw3 = wx.StaticText(self, label='Set Resolution')
        self.reso = wx.TextCtrl(self)
        self.reso.SetValue('0')
        self.resunit = wx.StaticText(self, label="N/A")

        hbox3_1.AddMany([(sw3, 1, wx.EXPAND), (self.resunit, 1, wx.EXPAND), (self.reso, 1, wx.EXPAND)])

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

        sc2 = wx.StaticText(self, label='Plot Selection:')
        selections2 = ['A', 'B']

        self.plotsel = wx.ComboBox(self, choices=selections2)
        self.plotsel.Bind(wx.EVT_COMBOBOX, self.PlotselectBtn)

        #self.plotsel = wx.CheckBox(self, label='A', pos=(20, 20))
        #self.plotsel.SetValue(False)
        #self.plotsel.Bind(wx.EVT_CHECKBOX, self.PlotselectBtn)
        #self.plot2sel = wx.CheckBox(self, label='B', pos=(20, 20))
        #self.plot2sel.SetValue(False)
        #self.plot2sel.Bind(wx.EVT_CHECKBOX, self.PlotselectBtn)

        hbox4_3.AddMany([(sc2, 1, wx.EXPAND), (self.plotsel, 1, wx.EXPAND)])

        hbox4_4 = wx.BoxSizer(wx.HORIZONTAL)

        sh2 = wx.StaticText(self, label='Plot Type:')
        self.typesel = wx.CheckBox(self, label='IV/VI', pos=(20, 20))
        self.typesel.SetValue(False)
        self.typesel.Bind(wx.EVT_CHECKBOX, self.typeselectBtn)
        self.type2sel = wx.CheckBox(self, label='RV/RI', pos=(20, 20))
        self.type2sel.SetValue(False)
        self.type2sel.Bind(wx.EVT_CHECKBOX, self.typeselectBtn)
        self.type3sel = wx.CheckBox(self, label='PV/PI', pos=(20, 20))
        self.type3sel.SetValue(False)
        self.type3sel.Bind(wx.EVT_CHECKBOX, self.typeselectBtn)

        hbox4_4.AddMany([(sh2, 1, wx.EXPAND), (self.typesel, 1, wx.EXPAND), (self.type2sel, 1, wx.EXPAND), (self.type3sel, 1, wx.EXPAND)])



        hbox5_1 = wx.BoxSizer(wx.HORIZONTAL)

        self.sweepBtn = wx.Button(self, label='IV Sweep', size=(50, 20))
        self.sweepBtn.Bind(wx.EVT_BUTTON, self.OnButton_Sweep)

        hbox5_1.Add(self.sweepBtn, 1, wx.EXPAND)

        vboxSweep.AddMany([(hbox11, 1, wx.EXPAND), (hbox1_2, 1, wx.EXPAND), (hbox2_1, 1, wx.EXPAND), (hbox1_1, 0, wx.EXPAND), (hbox3_1, 0, wx.EXPAND), (hbox4_1, 0, wx.EXPAND), (hbox4_2, 0, wx.EXPAND), (hbox4_3, 0, wx.EXPAND), (hbox4_4, 0, wx.EXPAND), (hbox5_1, 0, wx.EXPAND)])

        vboxOuter.AddMany([(vbox, 0, wx.EXPAND), (vboxSweep, 0, wx.EXPAND)])

        self.SetSizer(vboxOuter)

    def OnButton_SelectOutputFolder(self, event):
        """ Opens a file dialog to select an output directory for automatic measurement. """
        dirDlg = wx.DirDialog(self, "Open", "", wx.DD_DEFAULT_STYLE)
        dirDlg.ShowModal()
        self.outputFolderTb.SetValue(dirDlg.GetPath())
        dirDlg.Destroy()


    def OnButton_Sweep(self, event):
        """ Calls ivsweep function using SMU class, saves and formats data to a csv file in chosen savefile location """

        if self.sweeptypeflag == 'Voltage':
            if int(self.reso.GetValue()) / 1000 > (int(self.maxset.GetValue()) - int(self.minset.GetValue())):
                print("Error: Please enter valid resolution")
                return

        if self.sweeptypeflag == 'Current':
            if int(self.reso.GetValue()) > (int(self.maxset.GetValue()) - int(self.minset.GetValue())):
                print("Error: Please enter valid resolution")
                return

        print('Commencing Sweep...')
        print(self.sweeptypeflag)

        self.smu.ivsweep(float(self.minset.GetValue()), float(self.maxset.GetValue()), float(self.reso.GetValue()), self.sweeptypeflag)


        if self.outputFolderTb.GetValue() != '':

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

            if self.sweeptypeflag == 'Voltage':
                self.graphPanel.canvas.sweepResultDict = {}
                self.graphPanel.canvas.sweepResultDict['voltage'] = self.voltageA
                self.graphPanel.canvas.sweepResultDict['current'] = self.currentA
                self.drawGraph(self.voltageA, self.currentA, self.typeflag)
            if self.sweeptypeflag == 'Current':
                self.graphPanel.canvas.sweepResultDict = {}
                self.graphPanel.canvas.sweepResultDict['voltage'] = self.voltageA
                self.graphPanel.canvas.sweepResultDict['current'] = self.currentA
                self.drawGraph(self.currentA, self.voltageA, self.typeflag)

        if self.plotflag == 'B':

            if self.sweeptypeflag == 'Voltage':
                self.graphPanel.canvas.sweepResultDict = {}
                self.graphPanel.canvas.sweepResultDict['voltage'] = self.voltageB
                self.graphPanel.canvas.sweepResultDict['current'] = self.currentB
                self.drawGraph(self.voltageB, self.currentB, self.typeflag)
            if self.sweeptypeflag == 'Current':
                self.graphPanel.canvas.sweepResultDict = {}
                self.graphPanel.canvas.sweepResultDict['voltage'] = self.voltageB
                self.graphPanel.canvas.sweepResultDict['current'] = self.currentB
                self.drawGraph(self.currentB, self.voltageB, self.typeflag)


    def drawGraph(self, voltage, dependant, typeflag):
        self.graphPanel.axes.cla()
        self.graphPanel.axes.plot(voltage, dependant)
        self.graphPanel.axes.ticklabel_format(useOffset=False)
        if typeflag == 'IV':
            if self.sweeptypeflag == 'Voltage':
                self.graphPanel.axes.set_xlabel('Voltage (V)')
                self.graphPanel.axes.set_ylabel('Current (mA)')
            if self.sweeptypeflag == 'Current':
                self.graphPanel.axes.set_xlabel('Current (mA)')
                self.graphPanel.axes.set_ylabel('Voltage (V)')
        if typeflag == 'RV':
            if self.sweeptypeflag == 'Voltage':
                self.graphPanel.axes.set_xlabel('Voltage (V)')
                self.graphPanel.axes.set_ylabel('Resistance (R)')
            if self.sweeptypeflag == 'Current':
                self.graphPanel.axes.set_xlabel('Current (mA)')
                self.graphPanel.axes.set_ylabel('Resistance (R)')
        if typeflag == 'PV':
            if self.sweeptypeflag == 'Voltage':
                self.graphPanel.axes.set_xlabel('Voltage (V)')
                self.graphPanel.axes.set_ylabel('Power (mW)')
            if self.sweeptypeflag == 'Current':
                self.graphPanel.axes.set_xlabel('Current (mA)')
                self.graphPanel.axes.set_ylabel('Power (mW)')
        self.graphPanel.canvas.draw()


    def UpdateAutoMeasurement(self, event):
        va = self.smu.getvoltageA()
        ia = self.smu.getcurrentA()
        ra = self.smu.getresistanceA()
        va = float(va)
        ia = float(ia)*1000
        ra = float(ra)
        self.voltreadA.SetLabel(str(va))
        self.currentreadA.SetLabel(str(ia))
        self.rreadA.SetLabel(str(ra))

        vb = self.smu.getvoltageB()
        ib = self.smu.getcurrentB()
        rb = self.smu.getresistanceB()
        vb = float(vb)
        ib = float(ib)*1000
        rb = float(rb)
        self.voltreadB.SetLabel(str(vb))
        self.currentreadB.SetLabel(str(ib))
        self.rreadB.SetLabel(str(rb))

        #self.voltread.SetLabel(str(int(v*1000)/1000))
        #self.currentread.SetLabel(str(int(i*1e6)/1000))


    def OnButton_currentSet(self, event):
        self.smu.setCurrent((float(self.currentset.GetValue())/1e3), self.smusel.GetValue())#self.smuasel.GetValue(), self.smubsel.GetValue())
        self.voltset.SetValue('')


    def OnButton_voltageSet(self, event):
        self.smu.setVoltage((float(self.voltset.GetValue())), self.smusel.GetValue()) # self.smuasel.GetValue(), self.smubsel.GetValue())
        self.currentset.SetValue('')


    def OnButton_currentlim(self, event):
        self.smu.setcurrentlimit(float(self.currentlim.GetValue()), self.smusel.GetValue())# self.smuasel.GetValue(), self.smubsel.GetValue())


    def OnButton_voltagelim(self, event):
        self.smu.setvoltagelimit(float(self.voltlim.GetValue()), self.smusel.GetValue())# self.smuasel.GetValue(), self.smubsel.GetValue())


    def OnButton_powerlim(self, event):
        self.smu.setpowerlimit(float(self.powerlim.GetValue()), self.smusel.GetValue())# self.smuasel.GetValue(), self.smubsel.GetValue())


    def OnButton_outputToggle(self, event):

        c = event.GetEventObject()
        flag = c.GetLabel()

        if self.smusel.GetValue() == 'A' and flag == 'ON':
            self.smu.turnchannelon(self.smusel.GetValue())
        if self.smusel.GetValue() == 'A' and flag == 'OFF':
            self.smu.turnchanneloff(self.smusel.GetValue())
        if self.smusel.GetValue() == 'B' and flag == 'ON':
            self.smu.turnchannelon(self.smusel.GetValue())
        if self.smusel.GetValue() == 'B' and flag == 'OFF':
            self.smu.turnchanneloff(self.smusel.GetValue())
        if self.smusel.GetValue() == 'All' and flag == 'ON':
            self.smu.turnchannelon(self.smusel.GetValue())
        if self.smusel.GetValue() == 'All' and flag == 'OFF':
            self.smu.turnchanneloff(self.smusel.GetValue())


    def OnButton_outputTogglesweep(self, event):

        c = event.GetEventObject()
        iden = c.GetId()
        if iden == 1:
            print(self.smu2sel.GetValue())

            if self.smu2sel.GetValue() == '':
                print("Please select an output")
                self.smu.setoutputflagoff('A')
                self.smu.setoutputflagoff('B')

            if self.smu2sel.GetValue() == 'A':
                self.smu.setoutputflagon(self.smu2sel.GetValue())
                self.smu.setoutputflagoff('B')

            if self.smu2sel.GetValue() == 'B':
                self.smu.setoutputflagon(self.smu2sel.GetValue())
                self.smu.setoutputflagoff('A')

            if self.smu2sel.GetValue() == 'All':
                self.smu.setoutputflagon('A')
                self.smu.setoutputflagon('B')


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
        label = self.plotsel.GetValue()


        a = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        b = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


        if self.dependantA==[] and self.dependantB==[]:

            if label == 'A':
                self.plotflag = 'A'

            if label == 'B':
                self.plotflag = 'B'

            return

        if self.dependantB == []:

            if label == 'A':
                self.plotflag = 'A'
                if self.sweeptypeflag == 'Voltage':
                    self.Plot(self.voltageA, self.dependantA)
                if self.sweeptypeflag == 'Current':
                    self.Plot(self.currentA, self.dependantA)

            if label == 'B':
                self.plotflag = 'B'
                self.Plot(a, b)

            return

        if self.dependantA == []:

            if label == 'A':
                self.plotflag = 'A'
                self.Plot(a, b)


            if label == 'B':
                self.plotflag = 'B'
                if self.sweeptypeflag == 'Voltage':
                    self.Plot(self.voltageB, self.dependantB)
                if self.sweeptypeflag == 'Current':
                    self.Plot(self.currentB, self.dependantB)

            return

        if label == 'A':
            self.plotflag = 'A'
            if self.sweeptypeflag == 'Voltage':
                self.Plot(self.voltageA, self.dependantA)
            if self.sweeptypeflag == 'Current':
                self.Plot(self.currentA, self.dependantA)

        if label == 'B':
            self.plotflag = 'B'
            if self.sweeptypeflag == 'Voltage':
                self.Plot(self.voltageB, self.dependantB)
            if self.sweeptypeflag == 'Current':
                self.Plot(self.currentB, self.dependantB)


    def Plot(self, independant, dependant):

        self.graphPanel.canvas.sweepResultDict = {}
        self.graphPanel.canvas.sweepResultDict['xaxis'] = independant
        self.graphPanel.canvas.sweepResultDict['yaxis'] = dependant

        self.drawGraph(independant, dependant, self.typeflag)


    def typeselectBtn(self, event):

        cb = event.GetEventObject()
        label = cb.GetLabel()
        value = cb.GetValue()


        if value==False:
            self.typeflag = ''
            self.dependantA = [0]
            self.dependantB = [0]
            self.Plot(self.dependantA, self.dependantB)


        if label=='RV/RI' and value==True:
            self.typesel.SetValue(False)
            self.type3sel.SetValue(False)
            self.typeflag = 'RV'
            self.dependantA = self.smu.resistanceresultA
            self.dependantB = self.smu.resistanceresultB
            if self.plotflag == 'A':
                if self.sweeptypeflag == 'Voltage':
                    self.Plot(self.voltageA, self.dependantA)
                if self.sweeptypeflag == 'Current':
                    self.Plot(self.currentA, self.dependantA)
            if self.plotflag == 'B':
                if self.sweeptypeflag == 'Voltage':
                    self.Plot(self.voltageB, self.dependantB)
                if self.sweeptypeflag == 'Current':
                    self.Plot(self.currentB, self.dependantB)

        if label=='IV/VI' and value==True:
            self.type2sel.SetValue(False)
            self.type3sel.SetValue(False)
            self.typeflag = 'IV'

            if self.sweeptypeflag == 'Voltage':
                self.dependantA = self.smu.currentresultA
                self.dependantB = self.smu.currentresultB
            if self.sweeptypeflag == 'Current':
                self.dependantA = self.smu.voltageresultA
                self.dependantB = self.smu.voltageresultB

            if self.plotflag=='A':
                if self.sweeptypeflag == 'Voltage':
                    self.Plot(self.voltageA, self.dependantA)
                if self.sweeptypeflag == 'Current':
                    self.Plot(self.currentA, self.dependantA)
            if self.plotflag=='B':
                if self.sweeptypeflag == 'Voltage':
                    self.Plot(self.voltageB, self.dependantB)
                if self.sweeptypeflag == 'Current':
                    self.Plot(self.currentB, self.dependantB)

        if label=='PV/PI' and value==True:
            self.typesel.SetValue(False)
            self.type2sel.SetValue(False)
            self.typeflag = 'PV'
            self.dependantA = self.smu.powerresultA
            self.dependantB = self.smu.powerresultB
            if self.plotflag == 'A':
                if self.sweeptypeflag == 'Voltage':
                    self.Plot(self.voltageA, self.dependantA)
                if self.sweeptypeflag == 'Current':
                    self.Plot(self.currentA, self.dependantA)
            if self.plotflag == 'B':
                if self.sweeptypeflag == 'Voltage':
                    self.Plot(self.voltageB, self.dependantB)
                if self.sweeptypeflag == 'Current':
                    self.Plot(self.currentB, self.dependantB)


    def sweeptype(self, event):

        c = event.GetEventObject()
        label = c.GetLabel()

        if self.voltsel.GetValue() and self.currentsel.GetValue():
            if label == "Voltage":
                self.currentsel.SetValue(False)
                self.sweeptypeflag = 'Voltage'
                self.minunit.SetLabel('V')
                self.maxunit.SetLabel('V')
                self.resunit.SetLabel('mV')
                print('Set to Voltage sweep')

            if label == "Current":
                self.voltsel.SetValue(False)
                self.sweeptypeflag = 'Current'
                self.minunit.SetLabel('mA')
                self.maxunit.SetLabel('mA')
                self.resunit.SetLabel('mA')
                print('Set to Current sweep')

        elif self.voltsel.GetValue() and self.currentsel.GetValue()==False:
            self.sweeptypeflag = 'Voltage'
            self.minunit.SetLabel('V')
            self.maxunit.SetLabel('V')
            self.resunit.SetLabel('mV')

            print('Set to Voltage sweep')

        elif self.currentsel.GetValue() and self.voltsel.GetValue()==False:
            self.sweeptypeflag = 'Current'
            self.minunit.SetLabel('mA')
            self.maxunit.SetLabel('mA')
            self.resunit.SetLabel('mA')
            print('Set to Current sweep')

