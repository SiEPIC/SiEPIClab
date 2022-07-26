
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
import re
import csv
from outputlogPanel import outputlogPanel
from logWriter import logWriter, logWriterError
import sys
from ElectroOpticDevice import ElectroOpticDevice
import numpy as np
from keithley2600 import Keithley2600
from SMU import SMUClass


class testParameters(wx.Frame):

    def __init__(self):

        displaySize = wx.DisplaySize()
        super(testParameters, self).__init__(None, title='Instrument Control', size=(int(displaySize[0] * 5 / 8.0), int(displaySize[1] * 3 / 4.0)))

        try:
            self.InitUI()
        except Exception as e:
            self.Destroy()
            raise
        self.Centre()
        self.Show()

    def InitUI(self):
        self.Bind(wx.EVT_CLOSE, self.OnExitApp)
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        panel = TopPanel(self)

        vbox.Add(panel, proportion=1, border=0, flag=wx.EXPAND)

        #vbox.Add(hbox, 3, wx.EXPAND)
        self.log = outputlogPanel(self)
        vbox.Add(self.log, 1, wx.EXPAND)
        self.SetSizer(vbox)

        sys.stdout = logWriter(self.log)
        sys.stderr = logWriterError(self.log)

    def OnExitApp(self, event):
        self.Destroy()


class TopPanel(wx.Panel):
    # Panel which contains the panels used for controlling the laser and detectors. It also
    # contains the graph.
    def __init__(self, parent):
        super(TopPanel, self).__init__(parent)
        self.routineflag = ""
        self.panel = SetPanel(self)#BlankPanel(self)
        self.autoMeasure = autoMeasure()
        self.selected = []
        self.data = {'index': [], 'device': [], 'VoltMin': [], 'VoltMax': [], 'CurrentMin': [], 'CurrentMax': [],
                     'VoltRes': [], 'CurrentRes': [], 'IV': [], 'RV': [], 'PV': [], 'Start': [], 'Stop': [],
                     'Stepsize': [], 'Sweeppower': [], 'Sweepspeed': [], 'Laseroutput': [], 'Numscans': []}
        self.InitUI()

    def InitUI(self):

        sbOuter = wx.StaticBox(self, label='Test Parameter Creation')
        vboxOuter = wx.StaticBoxSizer(sbOuter, wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.coordFileTb = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.coordFileTb.SetValue('No file selected')
        self.coordFileSelectBtn = wx.Button(self, wx.ID_OPEN, size=(50, 20))
        self.coordFileSelectBtn.Bind(wx.EVT_BUTTON, self.OnButton_ChooseCoordFile)
        hbox.AddMany([(self.coordFileTb, 1, wx.EXPAND), (self.coordFileSelectBtn, 0, wx.EXPAND)])

        self.checkAllBtn = wx.Button(self, label='Select All', size=(80, 20))
        self.checkAllBtn.Bind(wx.EVT_BUTTON, self.OnButton_CheckAll)
        self.uncheckAllBtn = wx.Button(self, label='Unselect All', size=(80, 20))
        self.uncheckAllBtn.Bind(wx.EVT_BUTTON, self.OnButton_UncheckAll)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.AddMany([(self.checkAllBtn, 0, wx.EXPAND), (self.uncheckAllBtn, 0, wx.EXPAND)])
        ##
        self.checkList = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        self.checkList.InsertColumn(0, 'Device', width=100)
        self.checkList.Bind(wx.EVT_LIST_ITEM_CHECKED, self.checkListchecked)
        self.checkList.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.checkListunchecked)
        self.checkListset = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        self.checkListset.InsertColumn(0, 'Device', width=100)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        vboxdevices = wx.BoxSizer(wx.VERTICAL)
        vboxset = wx.BoxSizer(wx.VERTICAL)

        vboxdevices.Add(self.checkList, proportion=1, flag=wx.EXPAND)
        vboxset.Add(self.checkListset, proportion=1, flag=wx.EXPAND)

        hbox3.AddMany([(vboxdevices, 1, wx.EXPAND),(vboxset, 1, wx.EXPAND)])


        ##
        #self.autoMeasure = autoMeasure
        #self.coordMapPanel = autoMeasure.coordinateMapPanel(self, self.autoMeasure, 3)
        #hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        #hbox4.Add(self.coordMapPanel, proportion=1, flag=wx.EXPAND)

        #hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        #t1 = wx.StaticText(self, label='Select Routine: ')
        #selections = ['Electrical', 'Optical', 'Set Voltage, Wavelength sweep', 'Set Wavelength, Voltage sweep']

        #self.routinesel = wx.ComboBox(self, choices=selections)
        #self.routinesel.Bind(wx.EVT_COMBOBOX, self.routineSet)

        #hbox4.AddMany([(st1, 0, wx.EXPAND), (self.routinesel, 0, wx.EXPAND)])

        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        #self.panel = ElectricalPanel(self)

        hbox5.Add(self.panel, 0, wx.EXPAND)

        hbox6 = wx.BoxSizer(wx.HORIZONTAL)

        st2 = wx.StaticText(self, label='Save folder:')
        # Add Save folder Option
        self.outputFolderTb = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.outputFolderBtn = wx.Button(self, wx.ID_OPEN, size=(50, 20))
        self.outputFolderBtn.Bind(wx.EVT_BUTTON, self.OnButton_SelectOutputFolder)

        hbox6.AddMany([(st2, 1, wx.EXPAND), (self.outputFolderTb, 1, wx.EXPAND), (self.outputFolderBtn, 0, wx.EXPAND)])



        hbox7 = wx.BoxSizer(wx.HORIZONTAL)

        self.setBtn = wx.Button(self, label='Set', size=(50, 20))
        self.setBtn.Bind(wx.EVT_BUTTON, self.SetButton)

        self.importBtn = wx.Button(self, label='Import', size=(50, 20))
        #self.importBtn.Bind(wx.EVT_BUTTON, self.ImportButton)

        self.exportBtn = wx.Button(self, label='Export', size=(50, 20))
        #self.exportBtn.Bind(wx.EVT_BUTTON, self.ExportButton)

        hbox7.AddMany([(self.setBtn, 0, wx.EXPAND), (self.importBtn, 0, wx.EXPAND), (self.exportBtn, 0, wx.EXPAND)])



        vboxOuter.AddMany([(hbox, 0, wx.EXPAND), (hbox2, 0, wx.EXPAND), (hbox3, 0, wx.EXPAND), (hbox5, 0, wx.EXPAND), (hbox6, 0, wx.ALIGN_LEFT), (hbox7, 0, wx.ALIGN_RIGHT)])



        self.SetSizer(vboxOuter)

    def OnButton_ChooseCoordFile(self, event):
        """ Opens a file dialog to select a coordinate file. """
        fileDlg = wx.FileDialog(self, "Open", "", "",
                                "Text Files (*.txt)|*.txt",
                                wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        fileDlg.ShowModal()
        self.coordFileTb.SetValue(fileDlg.GetFilenames()[0])
        # fileDlg.Destroy()
        self.autoMeasure.readCoordFile(fileDlg.GetPath())
        global deviceListAsObjects
        deviceListAsObjects = self.autoMeasure.devices
        self.device_list = deviceListAsObjects
        global deviceList
        deviceList = []
        for device in deviceListAsObjects:
            deviceList.append(device.getDeviceID())
        # Adds items to the check list
        self.checkList.DeleteAllItems()
        for ii, device in enumerate(deviceList):
            self.checkList.InsertItem(ii, device)
            for dev in deviceListAsObjects:
                if dev.getDeviceID() == device:
                    index = deviceListAsObjects.index(dev)  # Stores index of device in list
            self.checkList.SetItemData(ii, index)
        self.checkList.SortItems(self.checkListSort)  # Make sure items in list are sorted
        self.checkList.EnableCheckBoxes()

        for ii in range(self.checkList.GetItemCount()):
            self.data['index'] = ii

        self.data['device'] = ['Empty'] * self.checkList.GetItemCount()
        self.data['VoltMin'] = ['Empty'] * self.checkList.GetItemCount()
        self.data['VoltMax'] = ['Empty'] * self.checkList.GetItemCount()
        self.data['CurrentMin'] = ['Empty'] * self.checkList.GetItemCount()
        self.data['CurrentMax'] = ['Empty'] * self.checkList.GetItemCount()
        self.data['VoltRes'] = ['Empty'] * self.checkList.GetItemCount()
        self.data['CurrentRes'] = ['Empty'] * self.checkList.GetItemCount()
        self.data['IV'] = ['Empty'] * self.checkList.GetItemCount()
        self.data['RV'] = ['Empty'] * self.checkList.GetItemCount()
        self.data['PV'] = ['Empty'] * self.checkList.GetItemCount()
        self.data['Start'] = ['Empty'] * self.checkList.GetItemCount()
        self.data['Stop'] = ['Empty'] * self.checkList.GetItemCount()
        self.data['Stepsize'] = ['Empty'] * self.checkList.GetItemCount()
        self.data['Sweeppower'] = ['Empty'] * self.checkList.GetItemCount()
        self.data['Sweepspeed'] = ['Empty'] * self.checkList.GetItemCount()
        self.data['Laseroutput'] = ['Empty'] * self.checkList.GetItemCount()
        self.data['Numscans'] = ['Empty'] * self.checkList.GetItemCount()





        global fileLoaded
        fileLoaded = True
        self.Refresh()

    def OnButton_CheckAll(self, event):
        # self.checkList.CheckAll()
        for ii in range(self.checkList.GetItemCount()):
            self.checkList.CheckItem(ii, True)

    def OnButton_UncheckAll(self, event):
        # self.checkList.UncheckAll()
        for ii in range(self.checkList.GetItemCount()):
            self.checkList.CheckItem(ii, False)

    #def routineSet(self, event):
        #cb = event.GetEventObject()
        #label = cb.GetLabel()

        #if label == "Electrical":
        #    self.routineflag = "ELEC"
         #   self.panel = ElectricalPanel(self)
          #  print("self panel should change")
        #if label == "Optical":
        #    self.routineflag = "OPTIC"
         #   self.panel = ElectricalPanel(self)
         #   print("self panel should change")
        #if label == "Set Voltage, Wavelength sweep":
         #   self.routineflag = "setvolt"
          #  self.panel = ElectricalPanel(self)
          #  print("self panel should change")
        #if label == "Set Wavelength, Voltage sweep":
         #   self.routineflag = "setwave"
         #   self.panel = ElectricalPanel(self)
        #  print("self panel should change")
        #if label == "":
         #   self.routineflag = "blank"
          #  self.panel = BlankPanel(self)
           # print("self panel should change")

    def checkListSort(self, item1, item2):
        # Items are the client data associated with each entry
        if item2 < item2:
            return -1
        elif item1 > item2:
            return 1
        else:
            return 0


    def checkListchecked(self, event):
        c = event.GetIndex()
        self.selected.append(c)
        print(self.selected)

    def checkListunchecked(self, event):
        x = event.GetIndex()
        self.selected.remove(x)
        print(self.selected)


    def OnButton_SelectOutputFolder(self, event):
        """ Opens a file dialog to select an output directory for automatic measurement. """
        dirDlg = wx.DirDialog(self, "Open", "", wx.DD_DEFAULT_STYLE)
        dirDlg.ShowModal()
        self.outputFolderTb.SetValue(dirDlg.GetPath())
        dirDlg.Destroy()

    def SetButton(self, event):

        for c in range(len(self.selected)):

            self.data['device'][self.selected[c]] = self.checkList.GetItemText(self.selected[c], 0)
            self.data['VoltMin'][self.selected[c]] = '0'
            self.data['VoltMax'][self.selected[c]] = '0'
            self.data['CurrentMin'][self.selected[c]] = '0'
            self.data['CurrentMax'][self.selected[c]] = '0'
            self.data['VoltRes'][self.selected[c]] = '0'
            self.data['CurrentRes'][self.selected[c]] = '0'
            self.data['IV'][self.selected[c]] = self.panel.typesel.GetValue()
            self.data['RV'][self.selected[c]] = self.panel.type2sel.GetValue()
            self.data['PV'][self.selected[c]] = self.panel.type3sel.GetValue()
            self.data['Start'][self.selected[c]] = self.panel.startWvlTc.GetValue()
            self.data['Stop'][self.selected[c]] = self.panel.stopWvlTc.GetValue()
            self.data['Stepsize'][self.selected[c]] = self.panel.stepWvlTc.GetValue()
            self.data['Sweeppower'][self.selected[c]] = self.panel.sweepPowerTc.GetValue()
            self.data['Sweepspeed'][self.selected[c]] = self.panel.sweepSpeedCb.GetValue()
            self.data['Laseroutput'][self.selected[c]] = self.panel.laserOutputCb.GetValue()
            self.data['Numscans'][self.selected[c]] = self.panel.numSweepCb.GetValue()

        print(self.data['device'])
        print(self.data['IV'])
        print('set')





            #index = self.checkList.GetFirstSelected()
            #device = self.checkList.GetItem(index, 0)
            #self.data['device'] = device.device_id
            #print(self.data['device'])

    # def ImportButton(self, event):

    # def ExportButton(self, event):


class SetPanel(wx.Panel):

    def __init__(self, parent):
        super(SetPanel, self).__init__(parent)
        self.InitUI()

    def InitUI(self):
        sb = wx.StaticBox(self, label='Electrical')
        elecvbox = wx.StaticBoxSizer(sb, wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        evbox = wx.BoxSizer(wx.VERTICAL)
        tophbox = wx.BoxSizer(wx.HORIZONTAL)

        sb = wx.StaticBox(self, label='Optical')
        opticvbox = wx.StaticBoxSizer(sb, wx.VERTICAL)
        opvbox = wx.BoxSizer(wx.VERTICAL)
        opvbox2 = wx.BoxSizer(wx.VERTICAL)
        ophbox = wx.BoxSizer(wx.HORIZONTAL)

        othervbox = wx.BoxSizer(wx.VERTICAL)
        sb = wx.StaticBox(self, label='Set Voltage, wavelength sweep')
        setvoltvbox = wx.StaticBoxSizer(sb, wx.VERTICAL)
        sb = wx.StaticBox(self, label='Set Wavelength, voltage sweep')
        setwavevbox = wx.StaticBoxSizer(sb, wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        sq1_1 = wx.StaticText(self, label='Select Independant Variable: ')
        self.voltsel = wx.CheckBox(self, label='Voltage', pos=(20, 20))
        self.voltsel.SetValue(False)
        self.currentsel = wx.CheckBox(self, label='Current', pos=(20, 20))
        self.currentsel.SetValue(False)

        hbox1.AddMany([(sq1_1, 1, wx.EXPAND), (self.voltsel, 1, wx.EXPAND), (self.currentsel, 1, wx.EXPAND)])

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        sw1 = wx.StaticText(self, label='Set Max:')

        self.maxset = wx.TextCtrl(self)
        self.maxset.SetValue('0')
        self.maxunit = wx.StaticText(self, label="N/A")

        hbox2.AddMany([(sw1, 1, wx.EXPAND), (self.maxunit, 1, wx.EXPAND), (self.maxset, 1, wx.EXPAND)])

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)

        sw2 = wx.StaticText(self, label='Set Min:')
        self.minset = wx.TextCtrl(self)
        self.minset.SetValue('0')
        self.minunit = wx.StaticText(self, label="N/A")

        hbox3.AddMany([(sw2, 1, wx.EXPAND), (self.minunit, 1, wx.EXPAND), (self.minset, 1, wx.EXPAND)])

        hbox4 = wx.BoxSizer(wx.HORIZONTAL)

        sw3 = wx.StaticText(self, label='Set Resolution:')
        self.reso = wx.TextCtrl(self)
        self.reso.SetValue('0')
        self.resunit = wx.StaticText(self, label="N/A")

        hbox4.AddMany([(sw3, 1, wx.EXPAND), (self.resunit, 1, wx.EXPAND), (self.reso, 1, wx.EXPAND)])

        hbox5 = wx.BoxSizer(wx.HORIZONTAL)

        sh2 = wx.StaticText(self, label='Plot Type:')
        self.typesel = wx.CheckBox(self, label='IV/VI', pos=(20, 20))
        self.typesel.SetValue(False)
        #self.typesel.Bind(wx.EVT_CHECKBOX, self.typeselectBtn)
        self.type2sel = wx.CheckBox(self, label='RV/RI', pos=(20, 20))
        self.type2sel.SetValue(False)
        #self.type2sel.Bind(wx.EVT_CHECKBOX, self.typeselectBtn)
        self.type3sel = wx.CheckBox(self, label='PV/PI', pos=(20, 20))
        self.type3sel.SetValue(False)
        #self.type3sel.Bind(wx.EVT_CHECKBOX, self.typeselectBtn)

        hbox5.AddMany([(sh2, 1, wx.EXPAND), (self.typesel, 1, wx.EXPAND), (self.type2sel, 1, wx.EXPAND),
                         (self.type3sel, 1, wx.EXPAND)])

        evbox.AddMany([(hbox1, 1, wx.EXPAND), (hbox2, 1, wx.EXPAND), (hbox3, 1, wx.EXPAND), (hbox4, 1, wx.EXPAND), (hbox5, 1, wx.EXPAND)])

        hbox.AddMany([(evbox, 1, wx.EXPAND)])

        elecvbox.Add(hbox, 1, wx.EXPAND)


        opt_hbox = wx.BoxSizer(wx.HORIZONTAL)

        st4 = wx.StaticText(self, label='Start (nm)')

        self.startWvlTc = wx.TextCtrl(self)
        self.startWvlTc.SetValue('0')

        opt_hbox.AddMany([(st4, 1, wx.EXPAND), (self.startWvlTc, 1, wx.EXPAND)])

        opt_hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st5 = wx.StaticText(self, label='Stop (nm)')

        self.stopWvlTc = wx.TextCtrl(self)
        self.stopWvlTc.SetValue('0')

        opt_hbox2.AddMany([(st5, 1, wx.EXPAND), (self.stopWvlTc, 1, wx.EXPAND)])

        opt_hbox3 = wx.BoxSizer(wx.HORIZONTAL)

        st6 = wx.StaticText(self, label='Step (nm)')

        self.stepWvlTc = wx.TextCtrl(self)
        self.stepWvlTc.SetValue('0')

        opt_hbox3.AddMany([(st6, 1, wx.EXPAND), (self.stepWvlTc, 1, wx.EXPAND)])

        opt_hbox4 = wx.BoxSizer(wx.HORIZONTAL)

        sweepPowerSt = wx.StaticText(self, label='Sweep power (dBm)')

        self.sweepPowerTc = wx.TextCtrl(self)
        self.sweepPowerTc.SetValue('0')

        opt_hbox4.AddMany([(sweepPowerSt, 1, wx.EXPAND), (self.sweepPowerTc, 1, wx.EXPAND)])

        opt_hbox5 = wx.BoxSizer(wx.HORIZONTAL)

        st7 = wx.StaticText(self, label='Sweep speed')

        sweepSpeedOptions = ['80 nm/s', '40 nm/s', '20 nm/s', '10 nm/s', '5 nm/s', '0.5 nm/s', 'auto']
        self.sweepSpeedCb = wx.ComboBox(self, choices=sweepSpeedOptions, style=wx.CB_READONLY, value='auto')
        opt_hbox5.AddMany([(st7, 1, wx.EXPAND), (self.sweepSpeedCb, 1, wx.EXPAND)])

        opt_hbox6 = wx.BoxSizer(wx.HORIZONTAL)

        st8 = wx.StaticText(self, label='Laser output')

        laserOutputOptions = ['High power', 'Low SSE']
        self.laserOutputCb = wx.ComboBox(self, choices=laserOutputOptions, style=wx.CB_READONLY, value='High power')
        opt_hbox6.AddMany([(st8, 1, wx.EXPAND), (self.laserOutputCb, 1, wx.EXPAND)])

        opt_hbox7 = wx.BoxSizer(wx.HORIZONTAL)

        st9 = wx.StaticText(self, label='Number of scans')

        numSweepOptions = ['1', '2', '3']
        self.numSweepCb = wx.ComboBox(self, choices=numSweepOptions, style=wx.CB_READONLY, value='1')
        opt_hbox7.AddMany([(st9, 1, wx.EXPAND), (self.numSweepCb, 1, wx.EXPAND)])

        opvbox.AddMany([(opt_hbox, 1, wx.EXPAND), (opt_hbox2, 1, wx.EXPAND), (opt_hbox3, 1, wx.EXPAND), (opt_hbox4, 1, wx.EXPAND), (opt_hbox5, 1, wx.EXPAND)])

        opvbox2.AddMany([(opt_hbox6, 1, wx.EXPAND), (opt_hbox7, 1, wx.EXPAND)])

        ophbox.AddMany([(opvbox, 1, wx.EXPAND), (opvbox2, 1, wx.EXPAND)])

        opticvbox.Add(ophbox, 1, wx.EXPAND)

        sv_hbox = wx.BoxSizer(wx.HORIZONTAL)

        setvoltage2St = wx.StaticText(self, label='Set Voltage')

        self.setvoltage2Tc = wx.TextCtrl(self)
        self.setvoltage2Tc.SetValue('')

        sv_hbox.AddMany([(setvoltage2St, 1, wx.EXPAND), (self.setvoltage2Tc, 1, wx.EXPAND)])

        sv_hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        setwavevolt2St = wx.StaticText(self, label='Set Wavelength')

        self.setwavevolt2Tc = wx.TextCtrl(self)
        self.setwavevolt2Tc.SetValue('')

        sv_hbox2.AddMany([(setwavevolt2St, 1, wx.EXPAND), (self.setwavevolt2Tc, 1, wx.EXPAND)])

        setvoltvbox.AddMany([(sv_hbox, 1, wx.EXPAND), (sv_hbox2, 1, wx.EXPAND)])



        sw_hbox = wx.BoxSizer(wx.HORIZONTAL)

        setwave2St = wx.StaticText(self, label='Set Wavelength')

        self.setwave2Tc = wx.TextCtrl(self)
        self.setwave2Tc.SetValue('')

        sw_hbox.AddMany([(setwave2St, 1, wx.EXPAND), (self.setwave2Tc, 1, wx.EXPAND)])

        sw_hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        setvoltwave2St = wx.StaticText(self, label='Set Voltage')

        self.setvoltwave2Tc = wx.TextCtrl(self)
        self.setvoltwave2Tc.SetValue('')

        sw_hbox2.AddMany([(setvoltwave2St, 1, wx.EXPAND), (self.setvoltwave2Tc, 1, wx.EXPAND)])

        setwavevbox.AddMany([(sw_hbox, 1, wx.EXPAND), (sw_hbox2, 1, wx.EXPAND)])

        othervbox.AddMany([(setvoltvbox, 1, wx.EXPAND), (setwavevbox, 1, wx.EXPAND)])



        tophbox.AddMany([(elecvbox, 1, wx.EXPAND), (opticvbox, 1, wx.EXPAND),(othervbox, 1, wx.EXPAND)])

        self.SetSizer(tophbox)


class autoMeasure(object):

    def __init__(self):
        self.saveFolder = os.getcwd()

    def readCoordFile(self, fileName):

        with open(fileName, 'r') as f:
            data = f.readlines()

        # Remove the first line since it is the header and remove newline char
        dataStrip = [line.strip() for line in data[1:]]
        dataStrip2 = []
        for x in dataStrip:
            j = x.replace(" ", "")
            dataStrip2.append(j)
        # x,y,polarization,wavelength,type,deviceid,params
        reg = re.compile(r'(.*),(.*),(.*),([0-9]+),(.+),(.+),(.*)')
        # x,y,deviceid,padname,params
        regElec = re.compile(r'(.*),(.*),(.+),(.*),(.*)')

        self.devices = []

        # Parse the data in each line and put it into a list of devices
        for ii, line in enumerate(dataStrip2):
            if reg.match(line):
                matchRes = reg.findall(line)[0]
                devName = matchRes[5]
                device = ElectroOpticDevice(devName, matchRes[3], matchRes[2], float(matchRes[0]), float(matchRes[1]))
                self.devices.append(device)
            else:
                if regElec.match(line):
                    matchRes = reg.findall(line)[0]
                    devName = matchRes[2]
                    for device in self.devices:
                        if device.getDeviceID() == devName:
                            device.addElectricalCoordinates(matchRes[3], float(matchRes[0]), float(matchRes[1]))
                else:
                    print('Warning: The entry\n%s\nis not formatted correctly.' % line)



if __name__ == '__main__':
    app = wx.App(redirect=False)
    testParameters()
    app.MainLoop()
    app.Destroy()
    del app