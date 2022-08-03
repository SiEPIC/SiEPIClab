
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
import re
import csv
import shutil
from outputlogPanel import outputlogPanel
from logWriter import logWriter, logWriterError
import sys
from ElectroOpticDevice import ElectroOpticDevice
from config import ROOT_DIR
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
        self.setflag = False
        self.deviceListset = []
        self.data = {'index': [], 'device': [], 'ELECflag': [], 'OPTICflag': [], 'setwflag': [], 'setvflag': [], 'Voltsel': [],
                     'Currentsel': [], 'VoltMin': [], 'VoltMax': [], 'CurrentMin': [], 'CurrentMax': [],
                     'VoltRes': [], 'CurrentRes': [], 'IV': [], 'RV': [], 'PV': [], 'ChannelA': [], 'ChannelB': [],
                     'Start': [], 'Stop': [], 'Stepsize': [], 'Sweeppower': [], 'Sweepspeed': [], 'Laseroutput': [],
                     'Numscans': [], 'InitialRange': [], 'RangeDec': [] ,'setwVoltsel': [],'setwCurrentsel': [],
                     'setwVoltMin': [], 'setwVoltMax': [], 'setwCurrentMin': [], 'setwCurrentMax': [],
                     'setwVoltRes': [], 'setwCurrentRes': [], 'setwIV': [], 'setwRV': [], 'setwPV': [],
                     'setwChannelA': [], 'setwChannelB': [], 'Wavelengths': [], 'setvStart': [], 'setvStop': [],
                     'setvStepsize': [], 'setvSweeppower': [], 'setvSweepspeed': [], 'setvLaseroutput': [],
                     'setvNumscans': [], 'setvInitialRange': [], 'setvRangeDec': [], 'setvChannelA': [],
                     'setvChannelB': [], 'Voltages': []}
        self.dataimport = {'index': [], 'device': [], 'ELECflag': [], 'OPTICflag': [], 'setwflag': [], 'setvflag': [], 'Voltsel': [],
                     'Currentsel': [], 'VoltMin': [], 'VoltMax': [], 'CurrentMin': [], 'CurrentMax': [],
                     'VoltRes': [], 'CurrentRes': [], 'IV': [], 'RV': [], 'PV': [], 'ChannelA': [], 'ChannelB': [],
                     'Start': [], 'Stop': [], 'Stepsize': [], 'Sweeppower': [], 'Sweepspeed': [], 'Laseroutput': [],
                     'Numscans': [], 'InitialRange': [], 'RangeDec': [] ,'setwVoltsel': [],'setwCurrentsel': [],
                     'setwVoltMin': [], 'setwVoltMax': [], 'setwCurrentMin': [], 'setwCurrentMax': [],
                     'setwVoltRes': [], 'setwCurrentRes': [], 'setwIV': [], 'setwRV': [], 'setwPV': [],
                     'setwChannelA': [], 'setwChannelB': [], 'Wavelengths': [], 'setvStart': [], 'setvStop': [],
                     'setvStepsize': [], 'setvSweeppower': [], 'setvSweepspeed': [], 'setvLaseroutput': [],
                     'setvNumscans': [], 'setvInitialRange': [], 'setvRangeDec': [], 'setvChannelA': [],
                     'setvChannelB': [], 'Voltages': []}
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
        self.searchFile = wx.TextCtrl(self)
        self.searchFile.SetValue('')
        self.searchFile.Bind(wx.EVT_TEXT, self.highlight)
        self.searchBtn = wx.Button(self, label='Select keyword', size=(100, 20))
        self.searchBtn.Bind(wx.EVT_BUTTON, self.SearchDevices)
        self.unsearchBtn = wx.Button(self, label='Unselect keyword', size=(100, 20))
        self.unsearchBtn.Bind(wx.EVT_BUTTON, self.unSearchDevices)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.AddMany([(self.checkAllBtn, 0, wx.EXPAND), (self.uncheckAllBtn, 0, wx.EXPAND), (self.searchFile, 0, wx.EXPAND), (self.searchBtn, 0, wx.EXPAND), (self.unsearchBtn, 0, wx.EXPAND)])
        ##
        self.checkList = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        self.checkList.InsertColumn(0, 'Device', width=100)
        self.checkList.Bind(wx.EVT_LIST_ITEM_CHECKED, self.checkListchecked)
        self.checkList.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.checkListunchecked)
        #self.checkListset = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        #self.checkListset.InsertColumn(0, 'Device', width=100)
        #self.checkListset.Bind(wx.EVT_LIST_ITEM_CHECKED, self.checkListcheckedset)
        #self.checkListset.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.checkListuncheckedset)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        vboxdevices = wx.BoxSizer(wx.VERTICAL)
        vboxset = wx.BoxSizer(wx.VERTICAL)

        vboxdevices.Add(self.checkList, proportion=1, flag=wx.EXPAND)
        #vboxset.Add(self.checkListset, proportion=1, flag=wx.EXPAND)

        hbox3.AddMany([(vboxdevices, 1, wx.EXPAND)])#,(vboxset, 1, wx.EXPAND)])


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

        hbox6_5 = wx.BoxSizer(wx.HORIZONTAL)

        st10 = wx.StaticText(self, label='Import file:')
        # Add Save folder Option
        self.importFolderTb = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.importFolderBtn = wx.Button(self, wx.ID_OPEN, size=(50, 20))
        self.importFolderBtn.Bind(wx.EVT_BUTTON, self.OnButton_SelectImportFolder)

        hbox6_5.AddMany([(st10, 1, wx.EXPAND), (self.importFolderTb, 1, wx.EXPAND), (self.importFolderBtn, 0, wx.EXPAND)])



        hbox7 = wx.BoxSizer(wx.HORIZONTAL)

        self.setBtn = wx.Button(self, label='Set', size=(50, 20))
        self.setBtn.Bind(wx.EVT_BUTTON, self.SetButton)

        self.importBtn = wx.Button(self, label='Import', size=(50, 20))
        self.importBtn.Bind(wx.EVT_BUTTON, self.ImportButton)

        self.exportBtn = wx.Button(self, label='Export', size=(50, 20))
        self.exportBtn.Bind(wx.EVT_BUTTON, self.ExportButton)

        hbox7.AddMany([(self.setBtn, 0, wx.EXPAND), (self.importBtn, 0, wx.EXPAND), (self.exportBtn, 0, wx.EXPAND)])


        vboxOuter.AddMany([(hbox, 0, wx.EXPAND), (hbox2, 0, wx.EXPAND), (hbox3, 0, wx.EXPAND), (hbox5, 0, wx.EXPAND),
                           (hbox6, 0, wx.ALIGN_LEFT), (hbox6_5, 0, wx.ALIGN_LEFT), (hbox7, 0, wx.ALIGN_RIGHT)])

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
        self.set = [False] * self.checkList.GetItemCount()

        for ii in range(self.checkList.GetItemCount()):
            self.data['index'] = ii

            #electrical parameters of data
        self.data['device'] = [] #* self.checkList.GetItemCount()
        self.data['Voltsel'] = [] #* self.checkList.GetItemCount()
        self.data['Currentsel'] = []# * self.checkList.GetItemCount()
        self.data['VoltMin'] = [] #* self.checkList.GetItemCount()
        self.data['VoltMax'] = [] #* self.checkList.GetItemCount()
        self.data['CurrentMin'] = []# * self.checkList.GetItemCount()
        self.data['CurrentMax'] = [] #* self.checkList.GetItemCount()
        self.data['VoltRes'] = [] #* self.checkList.GetItemCount()
        self.data['CurrentRes'] = [] #* self.checkList.GetItemCount()
        self.data['IV'] = [] #* self.checkList.GetItemCount()
        self.data['RV'] = [] #* self.checkList.GetItemCount()
        self.data['PV'] = [] #* self.checkList.GetItemCount()
        self.data['ChannelA'] = [] #* self.checkList.GetItemCount()
        self.data['ChannelB'] = [] #* self.checkList.GetItemCount()

            #optical parameters of data
        self.data['Start'] = [] #* self.checkList.GetItemCount()
        self.data['Stop'] = [] #* self.checkList.GetItemCount()
        self.data['Stepsize'] = [] #* self.checkList.GetItemCount()
        self.data['Sweeppower'] = [] #* self.checkList.GetItemCount()
        self.data['Sweepspeed'] = [] #* self.checkList.GetItemCount()
        self.data['Laseroutput'] = [] #* self.checkList.GetItemCount()
        self.data['Numscans'] = [] #* self.checkList.GetItemCount()
        self.data['InitialRange'] = [] #* self.checkList.GetItemCount()
        self.data['RangeDec'] = [] #* self.checkList.GetItemCount()

            #set wavelength parameters of data
        self.data['setwVoltsel'] = [] #* self.checkList.GetItemCount()
        self.data['setwCurrentsel'] = [] #* self.checkList.GetItemCount()
        self.data['setwVoltMin'] = [] #* self.checkList.GetItemCount()
        self.data['setwVoltMax'] = [] #* self.checkList.GetItemCount()
        self.data['setwCurrentMin'] = [] #* self.checkList.GetItemCount()
        self.data['setwCurrentMax'] = [] #* self.checkList.GetItemCount()
        self.data['setwVoltRes'] = [] #* self.checkList.GetItemCount()
        self.data['setwCurrentRes'] = [] #* self.checkList.GetItemCount()
        self.data['setwIV'] = [] #* self.checkList.GetItemCount()
        self.data['setwRV'] = [] #* self.checkList.GetItemCount()
        self.data['setwPV'] = [] #* self.checkList.GetItemCount()
        self.data['setwChannelA'] = [] #* self.checkList.GetItemCount()
        self.data['setwChannelB'] = [] #* self.checkList.GetItemCount()
        self.data['Wavelengths'] = [] #* self.checkList.GetItemCount()

            #set voltage parameters of data
        self.data['setvStart'] = [] #* self.checkList.GetItemCount()
        self.data['setvStop'] = [] #* self.checkList.GetItemCount()
        self.data['setvStepsize'] = [] #* self.checkList.GetItemCount()
        self.data['setvSweeppower'] = [] #* self.checkList.GetItemCount()
        self.data['setvSweepspeed'] = [] #* self.checkList.GetItemCount()
        self.data['setvLaseroutput'] = [] #* self.checkList.GetItemCount()
        self.data['setvNumscans'] = [] #* self.checkList.GetItemCount()
        self.data['setvInitialRange'] = [] #* self.checkList.GetItemCount()
        self.data['setvRangeDec'] = [] #* self.checkList.GetItemCount()
        self.data['setvChannelA'] = [] #* self.checkList.GetItemCount()
        self.data['setvChannelB'] = []# * self.checkList.GetItemCount()
        self.data['Voltages'] = []# * self.checkList.GetItemCount()


        global fileLoaded
        fileLoaded = True
        self.Refresh()


    def OnButton_CheckAll(self, event):
        # self.checkList.CheckAll()
        for ii in range(self.checkList.GetItemCount()):
            if self.set[ii] == False:
                self.checkList.CheckItem(ii, True)


    def OnButton_UncheckAll(self, event):

        for ii in range(self.checkList.GetItemCount()):
            self.checkList.CheckItem(ii, False)


    def highlight(self, event):

        #for c in range(len(self.data['device'])):
        for c in range(self.checkList.GetItemCount()):
            if self.set[c] != True and self.searchFile.GetValue() != None and self.searchFile.GetValue() in self.checkList.GetItemText(c, 0):
                self.checkList.SetItemBackgroundColour(c, wx.Colour(255, 255, 0))
            else:
                self.checkList.SetItemBackgroundColour(c, wx.Colour(255,255,255))

            if self.searchFile.GetValue() == '':
                self.checkList.SetItemBackgroundColour(c, wx.Colour(255,255,255))


    def SearchDevices(self, event):

        for c in range(len(self.set)):
            #print(self.checkList.GetItemText(c, 0))
            #print(self.searchFile.GetValue())
            if self.set[c] != True and self.searchFile.GetValue() != '' and self.searchFile.GetValue() in self.checkList.GetItemText(c, 0):
                self.checkList.CheckItem(c, True)
                #self.checkList.SetItemBackgroundColour(c, wx.Colour(255, 0, 0))

            #if self.checkList.GetItemText(c, 0) == self.searchFile.GetValue():
              #  self.checkList.CheckItem(c, True)


    def unSearchDevices(self, event):

        #for c in range(len(self.data['device'])):
        for c in range(len(self.set)):
                # print(self.checkList.GetItemText(c, 0))
                # print(self.searchFile.GetValue())
            if self.set[c] != True and self.searchFile.GetValue() != '' and self.searchFile.GetValue() in self.checkList.GetItemText(c, 0):
                self.checkList.CheckItem(c, False)
            #print(self.checkList.GetItemText(c, 0))
            #print(self.searchFile.GetValue())
            #if self.checkList.GetItemText(c, 0) == self.searchFile.GetValue():
               # self.checkList.CheckItem(c, False)


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


    def checkListcheckedmanual(self, Index):
        self.checkList.CheckItem(Index, True)
        self.selected.append(Index)


    def checkListunchecked(self, event):
        x = event.GetIndex()
        if self.setflag == False:
            self.selected.remove(x)


    def OnButton_SelectOutputFolder(self, event):
        """ Opens a file dialog to select an output directory for automatic measurement. """
        dirDlg = wx.DirDialog(self, "Open", "", wx.DD_DEFAULT_STYLE)
        dirDlg.ShowModal()
        self.outputFolderTb.SetValue(dirDlg.GetPath())
        dirDlg.Destroy()


    def OnButton_SelectImportFolder(self, event):
        """ Opens a file dialog to select an output directory for automatic measurement. """
        fileDlg = wx.FileDialog(self, "Open", "")
        fileDlg.ShowModal()
        self.importFolderTb.SetValue(fileDlg.GetPath())
        fileDlg.Destroy()


    def changeColour(self, index):
        self.checkList.SetItemTextColour(index, wx.Colour(255, 0, 0))


    def SetButton(self, event):

        list.sort(self.selected, reverse=True)
        self.setflag = True

        #self.findbiggest(self.panel.elecroutine.GetValue(), self.panel.optroutine.GetValue(), self.panel.setwroutine.GetValue(), self.panel.setvroutine.GetValue())

        self.big = max([self.panel.elecroutine.GetValue(), self.panel.optroutine.GetValue(), self.panel.setwroutine.GetValue(), self.panel.setvroutine.GetValue()])

        #to ensure all lists are the same length we find the largest list and append blank strings to the other lists until they match the largest string

        while len(self.panel.elecvolt) < int(self.big):
            self.panel.elecvolt.append('')
            self.panel.eleccurrent.append('')
            self.panel.elecvmin.append('')
            self.panel.elecvmax.append('')
            self.panel.elecimin.append('')
            self.panel.elecimax.append('')
            self.panel.elecvres.append('')
            self.panel.elecires.append('')
            self.panel.eleciv.append('')
            self.panel.elecrv.append('')
            self.panel.elecpv.append('')
            self.panel.elecchannelA.append('')
            self.panel.elecchannelB.append('')
            self.panel.elecflagholder.append('')

        while len(self.panel.start) < int(self.big):
            self.panel.start.append('')
            self.panel.stop.append('')
            self.panel.step.append('')
            self.panel.sweeppow.append('')
            self.panel.sweepsped.append('')
            self.panel.laserout.append('')
            self.panel.numscans.append('')
            self.panel.initialran.append('')
            self.panel.rangedecre.append('')
            self.panel.opticflagholder.append('')

        while len(self.panel.setwvolt) < int(self.big):
            self.panel.setwvolt.append('')
            self.panel.setwcurrent.append('')
            self.panel.setwvmin.append('')
            self.panel.setwvmax.append('')
            self.panel.setwimin.append('')
            self.panel.setwimax.append('')
            self.panel.setwvres.append('')
            self.panel.setwires.append('')
            self.panel.setwiv.append('')
            self.panel.setwrv.append('')
            self.panel.setwpv.append('')
            self.panel.setwchannelA.append('')
            self.panel.setwchannelB.append('')
            self.panel.setwwavelengths.append('')
            self.panel.setwflagholder.append('')

        while len(self.panel.setvstart) < int(self.big):
            self.panel.setvstart.append('')
            self.panel.setvstop.append('')
            self.panel.setvstep.append('')
            self.panel.setvsweeppow.append('')
            self.panel.setvsweepsped.append('')
            self.panel.setvlaserout.append('')
            self.panel.setvnumscans.append('')
            self.panel.setvinitialran.append('')
            self.panel.setvrangedecre.append('')
            self.panel.setvchannelA.append('')
            self.panel.setvchannelB.append('')
            self.panel.setvvoltages.append('')
            self.panel.setvflagholder.append('')


        for c in range(len(self.selected)):

            for i in range(int(self.big)):
                self.data['device'].append(self.checkList.GetItemText(int(self.selected[c]), 0))


            for i in range(int(self.big)):

                #self.data['Voltsel'][int(self.selected[c + i])] = self.panel.elecvolt[i]
                self.data['Voltsel'].append(self.panel.elecvolt[i])
                    #self.data['Currentsel'][int(self.selected[c + i])] = self.panel.eleccurrent[i]
                self.data['Currentsel'].append(self.panel.eleccurrent[i])
                    #self.data['VoltMin'][int(self.selected[c + i])] = self.panel.elecvmin[i]
                self.data['VoltMin'].append(self.panel.elecvmin[i])
                    #self.data['VoltMax'][int(self.selected[c + i])] = self.panel.elecvmax[i]
                self.data['VoltMax'].append(self.panel.elecvmax[i])
                    #self.data['CurrentMin'][int(self.selected[c + i])] = self.panel.elecimin[i]
                self.data['CurrentMin'].append(self.panel.elecimin[i])
                    #self.data['CurrentMax'][int(self.selected[c + i])] = self.panel.elecimax[i]
                self.data['CurrentMax'].append(self.panel.elecimax[i])
                    #self.data['VoltRes'][int(self.selected[c + i])] = self.panel.elecvres[i]
                self.data['VoltRes'].append(self.panel.elecvres[i])
                    #self.data['CurrentRes'][int(self.selected[c + i])] = self.panel.elecires[i]
                self.data['CurrentRes'].append(self.panel.elecires[i])
                    #self.data['IV'][int(self.selected[c + i])] = self.panel.eleciv[i]
                self.data['IV'].append(self.panel.eleciv[i])
                    #self.data['RV'][int(self.selected[c + i])] = self.panel.elecrv[i]
                self.data['RV'].append(self.panel.elecrv[i])
                #self.data['PV'][int(self.selected[c + i])] = self.panel.elecpv[i]
                self.data['PV'].append(self.panel.elecpv[i])
                # self.data['ChannelA'][int(self.selected[c + i])] = self.panel.elecchannelA[i]
                self.data['ChannelA'].append(self.panel.elecchannelA[i])
                #self.data['ChannelB'][int(self.selected[c + i])] = self.panel.elecchannelB[i]
                self.data['ChannelB'].append(self.panel.elecchannelB[i])
                self.data['ELECflag'].append(self.panel.elecflagholder[i])


            for i in range(int(self.big)):

                #self.data['Start'][self.selected[c + i]] = self.panel.start[i]
                self.data['Start'].append(self.panel.start[i])
                #self.data['Stop'][self.selected[c + i]] = self.panel.stop[i]
                self.data['Stop'].append(self.panel.stop[i])
                #self.data['Stepsize'][self.selected[c + i]] = self.panel.step[i]
                self.data['Stepsize'].append(self.panel.step[i])
                #self.data['Sweeppower'][self.selected[c + i]] = self.panel.sweeppow[i]
                self.data['Sweeppower'].append(self.panel.sweeppow[i])
                #self.data['Sweepspeed'][self.selected[c + i]] = self.panel.sweepsped[i]
                self.data['Sweepspeed'].append(self.panel.sweepsped[i])
                #self.data['Laseroutput'][self.selected[c + i]] = self.panel.laserout[i]
                self.data['Laseroutput'].append(self.panel.laserout[i])
                #self.data['Numscans'][self.selected[c + i]] = self.panel.numscans[i]
                self.data['Numscans'].append(self.panel.numscans[i])
                #self.data['InitialRange'][self.selected[c + i]] = self.panel.initialran[i]
                self.data['InitialRange'].append(self.panel.initialran[i])
                #self.data['RangeDec'][self.selected[c + i]] = self.panel.rangedecre[i]
                self.data['RangeDec'].append(self.panel.rangedecre[i])
                self.data['OPTICflag'].append(self.panel.opticflagholder[i])



            for i in range(int(self.big)):

                #self.data['setwVoltsel'][self.selected[c + i]] = self.panel.setwvolt[i]
                self.data['setwVoltsel'].append(self.panel.setwvolt[i])
                #self.data['setwCurrentsel'][self.selected[c + i]] = self.panel.setwcurrent[i]
                self.data['setwCurrentsel'].append(self.panel.setwcurrent[i])
                #self.data['setwVoltMin'][self.selected[c + i]] = self.panel.setwvmin[i]
                self.data['setwVoltMin'].append(self.panel.setwvmin[i])
                #self.data['setwVoltMax'][self.selected[c + i]] = self.panel.setwvmax[i]
                self.data['setwVoltMax'].append(self.panel.setwvmax[i])
                #self.data['setwCurrentMin'][self.selected[c + i]] = self.panel.setwimin[i]
                self.data['setwCurrentMin'].append(self.panel.setwimin[i])
                #self.data['setwCurrentMax'][self.selected[c + i]] = self.panel.setwimax[i]
                self.data['setwCurrentMax'].append(self.panel.setwimax[i])
                #self.data['setwVoltRes'][self.selected[c + i]] = self.panel.setwvres[i]
                self.data['setwVoltRes'].append(self.panel.setwvres[i])
                #self.data['setwCurrentRes'][self.selected[c + i]] = self.panel.setwires[i]
                self.data['setwCurrentRes'].append(self.panel.setwires[i])
                #self.data['setwIV'][self.selected[c + i]] = self.panel.setwiv[i]
                self.data['setwIV'].append(self.panel.setwiv[i])
                #self.data['setwRV'][self.selected[c + i]] = self.panel.setwrv[i]
                self.data['setwRV'].append(self.panel.setwrv[i])
                #self.data['setwPV'][self.selected[c + i]] = self.panel.setwpv[i]
                self.data['setwPV'].append(self.panel.setwpv[i])
                #self.data['setwChannelA'][self.selected[c + i]] = self.panel.setwchannelA[i]
                self.data['setwChannelA'].append(self.panel.setwchannelA[i])
                #self.data['setwChannelB'][self.selected[c + i]] = self.panel.setwchannelB[i]
                self.data['setwChannelB'].append(self.panel.setwchannelB[i])
                #self.data['Wavelengths'][self.selected[c + i]] = self.panel.setwwavelengths[i]
                self.data['Wavelengths'].append(self.panel.setwwavelengths[i])
                self.data['setwflag'].append(self.panel.setwflagholder[i])



            #if self.panel.setvroutine.GetValue() != '0':

            for i in range(int(self.big)):

                #self.data['setvStart'][self.selected[c + i]] = self.panel.setvstart[i]
                self.data['setvStart'].append(self.panel.setvstart[i])
                #self.data['setvStop'][self.selected[c + i]] = self.panel.setvstop[i]
                self.data['setvStop'].append(self.panel.setvstop[i])
                #self.data['setvStepsize'][self.selected[c + i]] = self.panel.setvstep[i]
                self.data['setvStepsize'].append(self.panel.setvstep[i])
                #self.data['setvSweeppower'][self.selected[c + i]] = self.panel.setvsweeppow[i]
                self.data['setvSweeppower'].append(self.panel.setvsweeppow[i])
                #self.data['setvSweepspeed'][self.selected[c + i]] = self.panel.setvsweepsped[i]
                self.data['setvSweepspeed'].append(self.panel.setvsweepsped[i])
                #self.data['setvLaseroutput'][self.selected[c + i]] = self.panel.setvlaserout[i]
                self.data['setvLaseroutput'].append(self.panel.setvlaserout[i])
                #self.data['setvNumscans'][self.selected[c + i]] = self.panel.setvnumscans[i]
                self.data['setvNumscans'].append(self.panel.setvnumscans[i])
                #self.data['setvInitialRange'][self.selected[c + i]] = self.panel.setvinitialran[i]
                self.data['setvInitialRange'].append(self.panel.setvinitialran[i])
                #self.data['setvRangeDec'][self.selected[c + i]] = self.panel.setvrangedecre[i]
                self.data['setvRangeDec'].append(self.panel.setvrangedecre[i])
                #self.data['setvChannelA'][self.selected[c + i]] = self.panel.setvchannelA[i]
                self.data['setvChannelA'].append(self.panel.setvchannelA[i])
                #self.data['setvChannelB'][self.selected[c + i]] = self.panel.setvchannelB[i]
                self.data['setvChannelB'].append(self.panel.setvchannelB[i])
                #self.data['voltages'][self.selected[c + i]] = self.panel.setvvoltages[i]
                self.data['Voltages'].append(self.panel.setvvoltages[i])
                self.data['setvflag'].append(self.panel.setvflagholder[i])

            self.checkList.SetItemTextColour(self.selected[c], wx.Colour(211, 211, 211))
            self.checkList.SetItemBackgroundColour(c, wx.Colour(255, 255, 255))
            self.checkList.CheckItem(self.selected[c], False)
            self.set[self.selected[c]] = True

            print('Testing parameters for ' + self.checkList.GetItemText(self.selected[c], 0) + ' set')

        self.selected = []
        self.setflag = False
        self.panel.elecvolt = []
        self.panel.eleccurrent = []
        self.panel.elecvmax = []
        self.panel.elecvmin = []
        self.panel.elecimin = []
        self.panel.elecimax = []
        self.panel.elecires = []
        self.panel.elecvres = []
        self.panel.eleciv = []
        self.panel.elecrv = []
        self.panel.elecpv = []
        self.panel.elecchannelA = []
        self.panel.elecchannelB = []
        self.panel.elecflagholder = []

        self.panel.start = []
        self.panel.stop = []
        self.panel.step = []
        self.panel.sweeppow = []
        self.panel.sweepsped = []
        self.panel.laserout = []
        self.panel.numscans = []
        self.panel.initialran = []
        self.panel.rangedecre = []
        self.panel.opticflagholder = []

        self.panel.setwvolt = []
        self.panel.setwcurrent = []
        self.panel.setwvmax = []
        self.panel.setwvmin = []
        self.panel.setwimin = []
        self.panel.setwimax = []
        self.panel.setwires = []
        self.panel.setwvres = []
        self.panel.setwiv = []
        self.panel.setwrv = []
        self.panel.setwpv = []
        self.panel.setwchannelA = []
        self.panel.setwchannelB = []
        self.panel.setwwavelengths = []
        self.panel.setwflagholder = []

        self.panel.setvstart = []
        self.panel.setvstop = []
        self.panel.setvstep = []
        self.panel.setvsweeppow = []
        self.panel.setvsweepsped = []
        self.panel.setvlaserout = []
        self.panel.setvnumscans = []
        self.panel.setvinitialran = []
        self.panel.setvrangedecre = []
        self.panel.setvvoltages = []
        self.panel.setvchannelA = []
        self.panel.setvchannelB = []
        self.panel.setvflagholder = []

        optionsblank = []

        self.panel.routineselectelec.SetItems(optionsblank)
        self.panel.routineselectopt.SetItems(optionsblank)
        self.panel.routineselectsetw.SetItems(optionsblank)
        self.panel.routineselectsetv.SetItems(optionsblank)

        self.panel.elecroutine.SetValue('')
        self.panel.optroutine.SetValue('')
        self.panel.setwroutine.SetValue('')
        self.panel.setvroutine.SetValue('')


        #reset electrical panel parameters
        self.panel.voltsel.SetValue(False)
        self.panel.currentsel.SetValue(False)
        self.panel.maxsetvoltage.SetValue('')
        self.panel.maxsetcurrent.SetValue('')
        self.panel.minsetvoltage.SetValue('')
        self.panel.minsetcurrent.SetValue('')
        self.panel.resovoltage.SetValue('')
        self.panel.resocurrent.SetValue('')
        self.panel.typesel.SetValue(False)
        self.panel.type2sel.SetValue(False)
        self.panel.type3sel.SetValue(False)
        self.panel.Asel.SetValue(True)
        self.panel.Bsel.SetValue(False)

        self.panel.startWvlTc.SetValue('')
        self.panel.stopWvlTc.SetValue('')
        self.panel.stepWvlTc.SetValue('')
        self.panel.sweepPowerTc.SetValue('')
        self.panel.sweepinitialrangeTc.SetValue('')
        self.panel.rangedecTc.SetValue('')

        self.panel.startWvlTc2.SetValue('')
        self.panel.stopWvlTc2.SetValue('')
        self.panel.stepWvlTc2.SetValue('')
        self.panel.sweepPowerTc2.SetValue('')
        self.panel.sweepinitialrangeTc2.SetValue('')
        self.panel.rangedecTc2.SetValue('')

        self.panel.voltsel2.SetValue(False)
        self.panel.currentsel2.SetValue(False)
        self.panel.maxsetvoltage2.SetValue('')
        self.panel.maxsetcurrent2.SetValue('')
        self.panel.minsetvoltage2.SetValue('')
        self.panel.minsetcurrent2.SetValue('')
        self.panel.resovoltage2.SetValue('')
        self.panel.resocurrent2.SetValue('')
        self.panel.typesel2.SetValue(False)
        self.panel.type2sel2.SetValue(False)
        self.panel.type3sel2.SetValue(False)
        self.panel.Asel2.SetValue(True)
        self.panel.Bsel2.SetValue(False)






        for keys, values in self.data.items():
            print(keys)
            print(values)



            #index = self.checkList.GetFirstSelected()
            #device = self.checkList.GetItem(index, 0)
            #self.data['device'] = device.device_id
            #print(self.data['device'])


    def ImportButton(self, event):

        ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname('TestingParametersTemplate.csv'), '..'))
        originalfile = os.path.join(ROOT_DIR, 'pyOptomip', 'TestingParameters.csv')
        originalfile = self.importFolderTb.GetValue()

        if originalfile == '':
            print('Please select a file to import')
            return

        with open(originalfile, 'r') as file:
            rows = []
            for row in file:
                rows.append(row)

            rows.pop(2)
            rows.pop(1)
            rows.pop(0)

            for c in range(len(rows)):
                x = rows[c].split(',')

                self.dataimport['device'].append(x[0])
                self.dataimport['ELECflag'].append(x[1])
                self.dataimport['OPTICflag'].append(x[2])
                self.dataimport['setwflag'].append(x[3])
                self.dataimport['setvflag'].append(x[4])
                self.dataimport['Voltsel'].append(x[5])
                self.dataimport['Currentsel'].append(x[6])
                self.dataimport['VoltMin'].append(x[7])
                self.dataimport['VoltMax'].append(x[8])
                self.dataimport['CurrentMin'].append(x[9])
                self.dataimport['CurrentMax'].append(x[10])
                self.dataimport['VoltRes'].append(x[11])
                self.dataimport['CurrentRes'].append(x[12])
                self.dataimport['IV'].append(x[13])
                self.dataimport['RV'].append(x[14])
                self.dataimport['PV'].append(x[15])
                self.dataimport['ChannelA'].append(x[16])
                self.dataimport['ChannelB'].append(x[17])
                self.dataimport['Start'].append(x[18])
                self.dataimport['Stop'].append(x[19])
                self.dataimport['Stepsize'].append(x[20])
                self.dataimport['Sweeppower'].append(x[21])
                self.dataimport['Sweepspeed'].append(x[22])
                self.dataimport['Laseroutput'].append(x[23])
                self.dataimport['Numscans'].append(x[24])
                self.dataimport['InitialRange'].append(x[25])
                self.dataimport['RangeDec'].append(x[26])
                self.dataimport['setwVoltsel'].append(x[27])
                self.dataimport['setwCurrentsel'].append(x[28])
                self.dataimport['setwVoltMin'].append(x[29])
                self.dataimport['setwVoltMax'].append(x[30])
                self.dataimport['setwCurrentMin'].append(x[31])
                self.dataimport['setwCurrentMax'].append(x[32])
                self.dataimport['setwVoltRes'].append(x[33])
                self.dataimport['setwCurrentRes'].append(x[34])
                self.dataimport['setwIV'].append(x[35])
                self.dataimport['setwRV'].append(x[36])
                self.dataimport['setwPV'].append(x[37])
                self.dataimport['setwChannelA'].append(x[38])
                self.dataimport['setwChannelB'].append(x[39])
                self.dataimport['Wavelengths'].append(x[40])
                self.dataimport['setvStart'].append(x[41])
                self.dataimport['setvStop'].append(x[42])
                self.dataimport['setvStepsize'].append(x[43])
                self.dataimport['setvSweeppower'].append(x[44])
                self.dataimport['setvSweepspeed'].append(x[45])
                self.dataimport['setvLaseroutput'].append(x[46])
                self.dataimport['setvNumscans'].append(x[47])
                self.dataimport['setvInitialRange'].append(x[48])
                self.dataimport['setvRangeDec'].append(x[49])
                self.dataimport['setvChannelA'].append(x[50])
                self.dataimport['setvChannelB'].append(x[51])
                self.dataimport['Voltages'].append(x[52])


        for keys, values in self.dataimport.items():
            print(keys)
            print(values)



    def ExportButton(self, event):


        if self.outputFolderTb.GetValue() != '':
            #ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname('TestingParametersTemplate.csv'), '..'))
            #originalfile = os.path.join(ROOT_DIR, 'pyOptomip', 'TestingParametersTemplate.csv')
            #print(originalfile)
            savelocation = self.outputFolderTb.GetValue()
            savefile = savelocation + '/TestingParameters.csv'
            print(str(self.data['device']))
            #shutil.copyfile(originalfile, savefile)
            with open(savefile, 'w', newline='') as f:
                f.write(',,,,,,,,,,,,,,,,\n')
                f.write(',,,,,IV Sweep,,,,,,,,,,,,,Optical Sweep,,,,,,,,,Set Wavelength,,,,,,,,,,,,,,SetVoltage\n')
                f.write('Device ID, ELECFlag, OPTICflag, setwflag, setvflag, Volt Select, Current Select, Volt Min,Volt Max,Current Min,Current Max,Volt Resolution,Current Resolution,IV/VI,RV/RI,PV/PI, Channel A, Channel B,Start,Stop,Stepsize,Sweep power,Sweep speed,Laser Output,Number of scans, Initial Range, Range Dec, Volt Select, Current Select, Volt Min,Volt Max,Current Min,Current Max,Volt Resolution,Current Resolution,IV/VI,RV/RI,PV/PI, Channel A, Channel B, Wavelength, Start, Stop, Stepsize, Sweep power,Sweep speed,Laser Output,Number of scans, Initial Range, Range Dec, Channel A, Channel B, Voltages \n')

                for c in range(len(self.data['device'])):

                    f.write(str(self.data['device'][c]) + ',' + str(self.data['ELECflag'][c]) + ',' + str(self.data['OPTICflag'][c]) + ',' + str(self.data['setwflag'][c]) + ',' + str(self.data['setvflag'][c]) + ',' + str(self.data['Voltsel'][c]) + ',' + str(self.data['Currentsel'][c]) + ',' + str(self.data['VoltMin'][c]) + ',' + str(self.data['VoltMax'][c])
                            + ',' + str(self.data['CurrentMin'][c]) + ',' + str(self.data['CurrentMax'][c]) + ',' +
                            str(self.data['VoltRes'][c]) + ',' + str(self.data['CurrentRes'][c]) + ',' + str(self.data['IV'][c]) + ','
                            + str(self.data['RV'][c]) + ',' + str(self.data['PV'][c]) + ',' + str(self.data['ChannelA'][c]) + ',' + str(self.data['ChannelB'][c]) + ',' + str(self.data['Start'][c]) + ','
                            + str(self.data['Stop'][c]) + ',' + str(self.data['Stepsize'][c]) + ',' + str(self.data['Sweeppower'][c])
                            + ',' + str(self.data['Sweepspeed'][c]) + ',' + str(self.data['Laseroutput'][c]) + ','
                            + str(self.data['Numscans'][c]) + ',' + str(self.data['InitialRange'][c]) + ',' + str(self.data['RangeDec'][c]) + ',' + str(self.data['setwVoltsel'][c]) + ',' + str(self.data['setwCurrentsel'][c]) + ',' + str(self.data['setwVoltMin'][c]) + ',' + str(self.data['setwVoltMax'][c])
                            + ',' + str(self.data['setwCurrentMin'][c]) + ',' + str(self.data['setwCurrentMax'][c]) + ',' +
                            str(self.data['setwVoltRes'][c]) + ',' + str(self.data['setwCurrentRes'][c]) + ',' + str(self.data['setwIV'][c]) + ','
                            + str(self.data['setwRV'][c]) + ',' + str(self.data['setwPV'][c]) + ',' + str(self.data['setwChannelA'][c]) + ',' + str(self.data['setwChannelB'][c]) + ',' + str(self.data['Wavelengths'][c]) + ',' + str(self.data['setvStart'][c]) + ','
                            + str(self.data['setvStop'][c]) + ',' + str(self.data['setvStepsize'][c]) + ',' + str(self.data['setvSweeppower'][c])
                            + ',' + str(self.data['setvSweepspeed'][c]) + ',' + str(self.data['setvLaseroutput'][c]) + ','
                            + str(self.data['setvNumscans'][c]) + ',' + str(self.data['setvInitialRange'][c]) + ',' + str(self.data['setvRangeDec'][c]) + ',' + str(self.data['setvChannelA'][c]) + ',' + str(self.data['setvChannelB'][c]) + ',' + str(self.data['Voltages'][c]) + ',' + '\n')

        else:
            print('Please select savefile location')
            return




            #with open(savefile, 'w', newline='') as f:
             #   f.write('Channel A Results,,,,,Channel B Results\n')
              #  f.write('Voltage (V), Current (A), Resistance (R), Power (W)')
               # f.write(',,')
                #f.write('Voltage (V), Current (A), Resistance (R), Power (W)\n')

                #writer = csv.writer(f, delimiter=',')
                #for c in range(int(self.reso.GetValue())):
                 #   writer.writerow(row[c])



class SetPanel(wx.Panel):

    def __init__(self, parent):
        super(SetPanel, self).__init__(parent)
        self.elecvolt = []
        self.eleccurrent = []
        self.elecvmax = []
        self.elecvmin = []
        self.elecimin = []
        self.elecimax = []
        self.elecires = []
        self.elecvres = []
        self.eleciv = []
        self.elecrv = []
        self.elecpv = []
        self.elecchannelA = []
        self.elecchannelB = []
        self.elecflagholder = []

        self.start = []
        self.stop = []
        self.step = []
        self.sweeppow = []
        self.sweepsped = []
        self.laserout = []
        self.numscans = []
        self.initialran = []
        self.rangedecre = []
        self.opticflagholder = []

        self.setwvolt = []
        self.setwcurrent = []
        self.setwvmax = []
        self.setwvmin = []
        self.setwimin = []
        self.setwimax = []
        self.setwires = []
        self.setwvres = []
        self.setwiv = []
        self.setwrv = []
        self.setwpv = []
        self.setwchannelA = []
        self.setwchannelB = []
        self.setwwavelengths = []
        self.setwflagholder = []

        self.setvstart = []
        self.setvstop = []
        self.setvstep = []
        self.setvsweeppow = []
        self.setvsweepsped = []
        self.setvlaserout = []
        self.setvnumscans = []
        self.setvinitialran = []
        self.setvrangedecre = []
        self.setvvoltages = []
        self.setvchannelA = []
        self.setvchannelB = []
        self.setvflagholder = []
        self.InitUI()

    def InitUI(self):

        sb1_3 = wx.StaticBox(self, label='Routine Select')
        routineselect = wx.StaticBoxSizer(sb1_3, wx.VERTICAL)
        electricalroutine = wx. BoxSizer(wx.HORIZONTAL)

        #create instructions for creating test parameters document

        sbw = wx.StaticBox(self, label='Instructions')
        instructions = wx.StaticBoxSizer(sbw, wx.VERTICAL)

        steps = wx.BoxSizer(wx.VERTICAL)
        step1 = wx.BoxSizer(wx.HORIZONTAL)
        stp1 = wx.StaticText(self, label='1. Upload GDS file')

        step1.Add(stp1, 1, wx.EXPAND)

        step2 = wx.BoxSizer(wx.HORIZONTAL)
        stp2 = wx.StaticText(self, label='2. Select devices you wish to create routines for')

        step2.Add(stp2, 1, wx.EXPAND)

        step3 = wx.BoxSizer(wx.HORIZONTAL)
        stp3 = wx.StaticText(self, label='3. Select number of routines per type of routine')

        step3.Add(stp3, 1, wx.EXPAND)

        step4 = wx.BoxSizer(wx.HORIZONTAL)
        stp4 = wx.StaticText(self, label='4. Fill in routine data')

        step4.Add(stp4, 1, wx.EXPAND)

        step5 = wx.BoxSizer(wx.HORIZONTAL)
        stp5 = wx.StaticText(self, label='5. Click set button')

        step5.Add(stp5, 1, wx.EXPAND)

        step6 = wx.BoxSizer(wx.HORIZONTAL)
        stp6 = wx.StaticText(self, label='6. Repeat from step 2')

        step6.Add(stp6, 1, wx.EXPAND)


        steps.AddMany([(step1, 1, wx.EXPAND), (step2, 1, wx.EXPAND), (step3, 1, wx.EXPAND), (step4, 1, wx.EXPAND), (step5, 1, wx.EXPAND), (step6, 1, wx.EXPAND)])

        instructions.Add(steps, 1, wx.EXPAND)


        st10_2 = wx.StaticText(self, label='Electrical Routine')

        self.elecroutine = wx.TextCtrl(self, size= (40,20))
        self.elecroutine.name = 'elecroutine'
        self.elecroutine.SetValue('0')
        self.elecroutine.Bind(wx.EVT_TEXT, self.setnumroutine)

        electricalroutine.AddMany([(st10_2, 1, wx.EXPAND), (self.elecroutine, 0)])


        opticalroutine = wx.BoxSizer(wx.HORIZONTAL)

        st11_2 = wx.StaticText(self, label='Optical Routine')

        self.optroutine = wx.TextCtrl(self, size = (40,20))
        self.optroutine.name = 'optroutine'
        self.optroutine.SetValue('0')
        self.optroutine.Bind(wx.EVT_TEXT, self.setnumroutine)

        opticalroutine.AddMany([(st11_2, 1, wx.EXPAND), (self.optroutine, 0)])

        setvwsweeproutine = wx.BoxSizer(wx.HORIZONTAL)

        st12_2 = wx.StaticText(self, label='Set Voltage, Wavelength Sweep Routine')

        self.setvroutine = wx.TextCtrl(self, size = (40,20))
        self.setvroutine.name = 'setvroutine'
        self.setvroutine.SetValue('0')
        self.setvroutine.Bind(wx.EVT_TEXT, self.setnumroutine)

        setvwsweeproutine.AddMany([(st12_2, 1, wx.EXPAND), (self.setvroutine, 0)])



        setwvsweeproutine = wx.BoxSizer(wx.HORIZONTAL)

        st13_2 = wx.StaticText(self, label='Set Wavelength, Voltage Sweep Routine')

        self.setwroutine = wx.TextCtrl(self, size = (40,20))
        self.setwroutine.name = 'setwroutine'
        self.setwroutine.SetValue('0')
        self.setwroutine.Bind(wx.EVT_TEXT, self.setnumroutine)

        setwvsweeproutine.AddMany([(st13_2, 1, wx.EXPAND), (self.setwroutine)])


        sb = wx.StaticBox(self, label='Electrical')
        elecvbox = wx.StaticBoxSizer(sb, wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        evbox = wx.BoxSizer(wx.VERTICAL)
        tophbox = wx.BoxSizer(wx.HORIZONTAL)

        sb1 = wx.StaticBox(self, label='Optical')
        opticvbox = wx.StaticBoxSizer(sb1, wx.VERTICAL)
        opvbox = wx.BoxSizer(wx.VERTICAL)
        opvbox2 = wx.BoxSizer(wx.VERTICAL)
        ophbox = wx.BoxSizer(wx.HORIZONTAL)

        #create electrical box

        hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        sq0_1 = wx.StaticText(self, label='Select Routine ')
        options = []

        self.routineselectelec = wx.ComboBox(self, choices=options, style=wx.CB_READONLY, value='1')
        self.routineselectelec.name = 'routineselectelec'
        self.routineselectelec.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.routinepanel)
        self.routineselectelec.Bind(wx.EVT_COMBOBOX, self.swaproutine)


        hbox0.AddMany([(sq0_1, 1, wx.EXPAND), (self.routineselectelec, 1, wx.EXPAND)])

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        sq1_1 = wx.StaticText(self, label='Select Independent Variable: ')
        self.voltsel = wx.CheckBox(self, label='Voltage', pos=(20, 20))
        self.voltsel.SetValue(False)
        #self.voltsel.name = 'routineselectelec'
        self.voltsel.Bind(wx.EVT_CHECKBOX, self.trueorfalse)
        #self.voltsel.Bind(wx.EVT_CHECKBOX, self.routinepanel)
        self.currentsel = wx.CheckBox(self, label='Current', pos=(20, 20))
        self.currentsel.SetValue(False)
        #self.currentsel.name = 'routineselectelec'
        self.currentsel.Bind(wx.EVT_CHECKBOX, self.trueorfalse)
        #self.currentsel.Bind(wx.EVT_CHECKBOX, self.routinepanel)

        hbox1.AddMany([(sq1_1, 1, wx.EXPAND), (self.voltsel, 1, wx.EXPAND), (self.currentsel, 1, wx.EXPAND)])

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        sw1 = wx.StaticText(self, label='Set Max:')

        self.maxsetvoltage = wx.TextCtrl(self)
        self.maxsetvoltage.SetValue('V')
        self.maxsetvoltage.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        #self.maxsetvoltage.name = 'routineselectelec'
        self.maxsetvoltage.SetForegroundColour(wx.Colour(211, 211, 211))
        #self.maxsetvoltage.Bind(wx.EVT_TEXT, self.routinepanel)
        self.maxsetcurrent = wx.TextCtrl(self)
        self.maxsetcurrent.SetValue('mA')
        self.maxsetcurrent.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        #self.maxsetcurrent.name = 'routineselectelec'
        self.maxsetcurrent.SetForegroundColour(wx.Colour(211,211,211))
        #self.maxsetcurrent.Bind(wx.EVT_TEXT, self.routinepanel)

        hbox2.AddMany([(sw1, 1, wx.EXPAND), (self.maxsetvoltage, 1, wx.EXPAND), (self.maxsetcurrent, 1, wx.EXPAND)])

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)

        sw2 = wx.StaticText(self, label='Set Min:')
        self.minsetcurrent = wx.TextCtrl(self)
        self.minsetcurrent.SetValue('mA')
        self.minsetcurrent.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        #self.minsetcurrent.name = 'routineselectelec'
        self.minsetcurrent.SetForegroundColour(wx.Colour(211, 211, 211))
        #self.minsetcurrent.Bind(wx.EVT_TEXT, self.routinepanel)
        self.minsetvoltage = wx.TextCtrl(self)
        self.minsetvoltage.SetValue('V')
        self.minsetvoltage.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        #self.minsetvoltage.name = 'routineselectelec'
        self.minsetvoltage.SetForegroundColour(wx.Colour(211, 211, 211))
        #self.minsetvoltage.Bind(wx.EVT_TEXT, self.routinepanel)

        hbox3.AddMany([(sw2, 1, wx.EXPAND), (self.minsetvoltage, 1, wx.EXPAND), (self.minsetcurrent, 1, wx.EXPAND)])

        hbox4 = wx.BoxSizer(wx.HORIZONTAL)

        sw3 = wx.StaticText(self, label='Set Resolution:')
        self.resovoltage = wx.TextCtrl(self)
        self.resovoltage.SetValue('V')
        self.resovoltage.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        #self.resovoltage.name = 'routineselectelec'
        self.resovoltage.SetForegroundColour(wx.Colour(211, 211, 211))
        #self.resovoltage.Bind(wx.EVT_TEXT, self.routinepanel)
        self.resocurrent = wx.TextCtrl(self)
        self.resocurrent.SetValue('mA')
        self.resocurrent.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        #self.resocurrent.name = 'routineselectelec'
        self.resocurrent.SetForegroundColour(wx.Colour(211, 211, 211))
        #self.resocurrent.Bind(wx.EVT_TEXT, self.routinepanel)

        hbox4.AddMany([(sw3, 1, wx.EXPAND), (self.resovoltage, 1, wx.EXPAND), (self.resocurrent, 1, wx.EXPAND)])

        hbox5 = wx.BoxSizer(wx.HORIZONTAL)

        sh2 = wx.StaticText(self, label='Plot Type:')
        self.typesel = wx.CheckBox(self, label='IV/VI', pos=(20, 20))
        self.typesel.SetValue(False)
        #self.typesel.name = 'routineselectelec'
        #self.typesel.Bind(wx.EVT_CHECKBOX, self.typeselectBtn)
        self.type2sel = wx.CheckBox(self, label='RV/RI', pos=(20, 20))
        self.type2sel.SetValue(False)
        #self.type2sel.name = 'routineselectelec'
        #self.type2sel.Bind(wx.EVT_CHECKBOX, self.typeselectBtn)
        self.type3sel = wx.CheckBox(self, label='PV/PI', pos=(20, 20))
        self.type3sel.SetValue(False)
        #self.type3sel.name = 'routineselectelec'
        #self.typesel.Bind(wx.EVT_CHECKBOX, self.routinepanel)
        #self.type2sel.Bind(wx.EVT_CHECKBOX, self.routinepanel)
        #self.type3sel.Bind(wx.EVT_CHECKBOX, self.routinepanel)
        #self.type3sel.Bind(wx.EVT_CHECKBOX, self.typeselectBtn)

        hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        sq6_1 = wx.StaticText(self, label='Select SMU Channel: ')
        self.Asel = wx.CheckBox(self, label='A', pos=(20, 20))
        self.Asel.SetValue(False)
        #self.Asel.name = 'routineselectelec'
        self.Bsel = wx.CheckBox(self, label='B', pos=(20, 20))
        self.Bsel.SetValue(False)
        #self.Bsel.name = 'routineselectelec'
        self.Asel.Bind(wx.EVT_CHECKBOX, self.trueorfalse)
        self.Bsel.Bind(wx.EVT_CHECKBOX, self.trueorfalse)
        #self.Asel.Bind(wx.EVT_CHECKBOX, self.routinepanel)
        #self.Bsel.Bind(wx.EVT_CHECKBOX, self.routinepanel)

        self.elecsave = wx.Button(self, label='Save', size=(50, 20))
        self.elecsave.Bind(wx.EVT_BUTTON, self.routinesaveelec)

        hbox6.AddMany([(sq6_1, 1, wx.EXPAND), (self.Asel, 1, wx.EXPAND), (self.Bsel, 1, wx.EXPAND), (self.elecsave, 1, wx.EXPAND)])



        hbox5.AddMany([(sh2, 1, wx.EXPAND), (self.typesel, 1, wx.EXPAND), (self.type2sel, 1, wx.EXPAND), (self.type3sel, 1, wx.EXPAND)])

        evbox.AddMany([(hbox0, 1, wx.EXPAND), (hbox1, 1, wx.EXPAND), (hbox2, 1, wx.EXPAND), (hbox3, 1, wx.EXPAND), (hbox4, 1, wx.EXPAND), (hbox5, 1, wx.EXPAND), (hbox6, 1, wx.EXPAND)])

        hbox.AddMany([(evbox, 1, wx.EXPAND)])

        elecvbox.Add(hbox, 1, wx.EXPAND)

        #create optical box

        opt_hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        sq0_2 = wx.StaticText(self, label='Select Routine ')

        self.routineselectopt = wx.ComboBox(self, choices=options, style=wx.CB_READONLY, value='1')
        self.routineselectopt.name = 'routineselectopt'
        self.routineselectopt.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.routinepanel)
        self.routineselectopt.Bind(wx.EVT_COMBOBOX, self.swaproutine)

        opt_hbox0.AddMany([(sq0_2, 1, wx.EXPAND), (self.routineselectopt, 1, wx.EXPAND)])

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




        opt_hbox4_5 = wx.BoxSizer(wx.HORIZONTAL)

        sweepinitialrangeSt = wx.StaticText(self, label='Initial Range (dBm)')

        self.sweepinitialrangeTc = wx.TextCtrl(self)
        self.sweepinitialrangeTc.SetValue('0')

        opt_hbox4_5.AddMany([(sweepinitialrangeSt, 1, wx.EXPAND), (self.sweepinitialrangeTc, 1, wx.EXPAND)])

        opt_hbox4_6 = wx.BoxSizer(wx.HORIZONTAL)

        rangedecSt = wx.StaticText(self, label='Range Decrement (dBm)')

        self.rangedecTc = wx.TextCtrl(self)
        self.rangedecTc.SetValue('0')

        opt_hbox4_6.AddMany([(rangedecSt, 1, wx.EXPAND), (self.rangedecTc, 0, wx.EXPAND)])


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

        optsavebox = wx.BoxSizer(wx.HORIZONTAL)

        self.optsave = wx.Button(self, label='Save', size=(120, 25))
        #self.optsave.name = 'routineselectopt'
        self.optsave.Bind(wx.EVT_BUTTON, self.routinesaveopt)

        optsavebox.AddMany([((1,1),1), (self.optsave, 0, wx.EXPAND)])

        opvbox0 = wx.BoxSizer(wx.HORIZONTAL)

        opvbox0.AddMany([(opt_hbox0, 1, wx.EXPAND)])

        opvbox.AddMany([(opt_hbox, 1, wx.EXPAND), (opt_hbox2, 1, wx.EXPAND), (opt_hbox3, 1, wx.EXPAND), (opt_hbox4, 1, wx.EXPAND), (opt_hbox4_5, 1, wx.EXPAND)])

        opvbox2.AddMany([(opt_hbox5, 1, wx.EXPAND), (opt_hbox6, 1, wx.EXPAND), (opt_hbox7, 1, wx.EXPAND), (opt_hbox4_6, 1, wx.EXPAND)])

        ophbox.AddMany([(opvbox, 0, wx.EXPAND), (opvbox2, 0, wx.EXPAND)])

        opticvbox.AddMany([(opvbox0, 0, wx.EXPAND), ((0,0),1), (ophbox, 0, wx.EXPAND), ((1,1), 1), (optsavebox, 0, wx.EXPAND)])

        # create set wavelength, voltage sweep box


        #initialize boxes
        sb_2 = wx.StaticBox(self, label='Set Wavelength, Electrical sweep')
        elecvbox2 = wx.StaticBoxSizer(sb_2, wx.VERTICAL)
        hboxsetw = wx.BoxSizer(wx.HORIZONTAL)
        evbox2 = wx.BoxSizer(wx.VERTICAL)
        tophbox2 = wx.BoxSizer(wx.HORIZONTAL)

        hbox0_2 = wx.BoxSizer(wx.HORIZONTAL)
        sq0_1_2 = wx.StaticText(self, label='Select Routine ')

        self.routineselectsetw = wx.ComboBox(self, choices=options, style=wx.CB_READONLY, value='1')
        self.routineselectsetw.name = 'routineselectsetw'
        self.routineselectsetw.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.routinepanel)
        self.routineselectsetw.Bind(wx.EVT_COMBOBOX, self.swaproutine)

        hbox0_2.AddMany([(sq0_1_2, 1, wx.EXPAND), (self.routineselectsetw, 1, wx.EXPAND)])

        hbox1_2 = wx.BoxSizer(wx.HORIZONTAL)
        sq1_1_2 = wx.StaticText(self, label='Select Independant Variable: ')
        self.voltsel2 = wx.CheckBox(self, label='Voltage', pos=(20, 20))
        self.voltsel2.SetValue(False)
        self.currentsel2 = wx.CheckBox(self, label='Current', pos=(20, 20))
        self.currentsel2.SetValue(False)
        self.voltsel2.Bind(wx.EVT_CHECKBOX, self.trueorfalse)
        self.currentsel2.Bind(wx.EVT_CHECKBOX, self.trueorfalse)

        hbox1_2.AddMany([(sq1_1_2, 1, wx.EXPAND), (self.voltsel2, 1, wx.EXPAND), (self.currentsel2, 1, wx.EXPAND)])

        hbox2_2 = wx.BoxSizer(wx.HORIZONTAL)

        sw1_2 = wx.StaticText(self, label='Set Max:')

        self.maxsetvoltage2 = wx.TextCtrl(self)
        self.maxsetvoltage2.SetValue('V')
        self.maxsetvoltage2.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        self.maxsetvoltage2.SetForegroundColour(wx.Colour(211, 211, 211))
        self.maxsetcurrent2 = wx.TextCtrl(self)
        self.maxsetcurrent2.SetValue('mA')
        self.maxsetcurrent2.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        self.maxsetcurrent2.SetForegroundColour(wx.Colour(211, 211, 211))

        hbox2_2.AddMany([(sw1_2, 1, wx.EXPAND), (self.maxsetvoltage2, 1, wx.EXPAND), (self.maxsetcurrent2, 1, wx.EXPAND)])

        hbox3_2 = wx.BoxSizer(wx.HORIZONTAL)

        sw2_2 = wx.StaticText(self, label='Set Min:')
        self.minsetcurrent2 = wx.TextCtrl(self)
        self.minsetcurrent2.SetValue('mA')
        self.minsetcurrent2.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        self.minsetcurrent2.SetForegroundColour(wx.Colour(211, 211, 211))
        self.minsetvoltage2 = wx.TextCtrl(self)
        self.minsetvoltage2.SetValue('V')
        self.minsetvoltage2.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        self.minsetvoltage2.SetForegroundColour(wx.Colour(211, 211, 211))

        hbox3_2.AddMany([(sw2_2, 1, wx.EXPAND), (self.minsetvoltage2, 1, wx.EXPAND), (self.minsetcurrent2, 1, wx.EXPAND)])

        hbox4_2 = wx.BoxSizer(wx.HORIZONTAL)

        sw3_2 = wx.StaticText(self, label='Set Resolution:')
        self.resovoltage2 = wx.TextCtrl(self)
        self.resovoltage2.SetValue('V')
        self.resovoltage2.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        self.resovoltage2.SetForegroundColour(wx.Colour(211, 211, 211))
        self.resocurrent2 = wx.TextCtrl(self)
        self.resocurrent2.SetValue('mA')
        self.resocurrent2.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        self.resocurrent2.SetForegroundColour(wx.Colour(211, 211, 211))

        hbox4_2.AddMany([(sw3_2, 1, wx.EXPAND), (self.resovoltage2, 1, wx.EXPAND), (self.resocurrent2, 1, wx.EXPAND)])

        hbox5_2 = wx.BoxSizer(wx.HORIZONTAL)

        sh2_2 = wx.StaticText(self, label='Plot Type:')
        self.typesel2 = wx.CheckBox(self, label='IV/VI', pos=(20, 20))
        self.typesel2.SetValue(False)
        #self.typesel.Bind(wx.EVT_CHECKBOX, self.typeselectBtn)
        self.type2sel2 = wx.CheckBox(self, label='RV/RI', pos=(20, 20))
        self.type2sel2.SetValue(False)
        #self.type2sel.Bind(wx.EVT_CHECKBOX, self.typeselectBtn)
        self.type3sel2 = wx.CheckBox(self, label='PV/PI', pos=(20, 20))
        self.type3sel2.SetValue(False)
        #self.type3sel.Bind(wx.EVT_CHECKBOX, self.typeselectBtn)

        hbox6_2 = wx.BoxSizer(wx.HORIZONTAL)
        sq6_2 = wx.StaticText(self, label='Select SMU Channel: ')
        self.Asel2 = wx.CheckBox(self, label='A', pos=(20, 20))
        self.Asel2.SetValue(False)
        self.Bsel2 = wx.CheckBox(self, label='B', pos=(20, 20))
        self.Bsel2.SetValue(False)
        self.Asel2.Bind(wx.EVT_CHECKBOX, self.trueorfalse)
        self.Bsel2.Bind(wx.EVT_CHECKBOX, self.trueorfalse)

        self.setwsave = wx.Button(self, label='Save', size=(50, 20))
        #self.setwsave.name = 'routineselectsetw'
        self.setwsave.Bind(wx.EVT_BUTTON, self.routinesavesetw)

        hbox6_2.AddMany([(sq6_2, 1, wx.EXPAND), (self.Asel2, 1, wx.EXPAND), (self.Bsel2, 1, wx.EXPAND), (self.setwsave, 1, wx.EXPAND)])



        hbox7_2 = wx.BoxSizer(wx.HORIZONTAL)

        wavesetst = wx.StaticText(self, label='Wavelengths (nm)')

        self.wavesetTc2 = wx.TextCtrl(self)
        self.wavesetTc2.SetValue('0')

        hbox7_2.AddMany([(wavesetst, 1, wx.EXPAND), (self.wavesetTc2, 1, wx.EXPAND)])




        hbox5_2.AddMany([(sh2_2, 1, wx.EXPAND), (self.typesel2, 1, wx.EXPAND), (self.type2sel2, 1, wx.EXPAND),
                       (self.type3sel2, 1, wx.EXPAND)])

        evbox2.AddMany([(hbox0_2, 1, wx.EXPAND), (hbox1_2, 1, wx.EXPAND), (hbox2_2, 1, wx.EXPAND), (hbox3_2, 1, wx.EXPAND), (hbox4_2, 1, wx.EXPAND),
                       (hbox5_2, 1, wx.EXPAND), (hbox7_2, 1, wx.EXPAND), (hbox6_2, 1, wx.EXPAND)])

        hboxsetw.AddMany([(evbox2, 1, wx.EXPAND)])

        elecvbox2.Add(hboxsetw, 1, wx.EXPAND)


        #create set voltage, sweep wavelength

        sb1_2 = wx.StaticBox(self, label='Set Electrical, Wavelength Sweep')
        opticvbox_2 = wx.StaticBoxSizer(sb1_2, wx.VERTICAL)
        opvbox_2 = wx.BoxSizer(wx.VERTICAL)
        opvbox2_2 = wx.BoxSizer(wx.VERTICAL)
        ophbox_2 = wx.BoxSizer(wx.HORIZONTAL)

        hbox0_2_2 = wx.BoxSizer(wx.HORIZONTAL)
        sq0_1_2_2 = wx.StaticText(self, label='Select Routine ')

        self.routineselectsetv = wx.ComboBox(self, choices=options, style=wx.CB_READONLY, value='1')
        self.routineselectsetv.name = 'routineselectsetv'
        self.routineselectsetv.SetItems(options)
        self.routineselectsetv.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.routinepanel)
        self.routineselectsetv.Bind(wx.EVT_COMBOBOX, self.swaproutine)

        hbox0_2_2.AddMany([(sq0_1_2_2, 1, wx.EXPAND), (self.routineselectsetv, 1, wx.EXPAND)])

        opt_hbox_2 = wx.BoxSizer(wx.HORIZONTAL)

        st4_2 = wx.StaticText(self, label='Start (nm)')

        self.startWvlTc2 = wx.TextCtrl(self)
        self.startWvlTc2.SetValue('0')

        opt_hbox_2.AddMany([(st4_2, 1, wx.EXPAND), (self.startWvlTc2, 1, wx.EXPAND)])

        opt_hbox2_2 = wx.BoxSizer(wx.HORIZONTAL)
        st5_2 = wx.StaticText(self, label='Stop (nm)')

        self.stopWvlTc2 = wx.TextCtrl(self)
        self.stopWvlTc2.SetValue('0')

        opt_hbox2_2.AddMany([(st5_2, 1, wx.EXPAND), (self.stopWvlTc2, 1, wx.EXPAND)])

        opt_hbox3_2 = wx.BoxSizer(wx.HORIZONTAL)

        st6_2 = wx.StaticText(self, label='Step (nm)')

        self.stepWvlTc2 = wx.TextCtrl(self)
        self.stepWvlTc2.SetValue('0')

        opt_hbox3_2.AddMany([(st6_2, 1, wx.EXPAND), (self.stepWvlTc2, 1, wx.EXPAND)])

        opt_hbox4_2 = wx.BoxSizer(wx.HORIZONTAL)

        sweepPowerSt2 = wx.StaticText(self, label='Sweep power (dBm)')

        self.sweepPowerTc2 = wx.TextCtrl(self)
        self.sweepPowerTc2.SetValue('0')

        opt_hbox4_2.AddMany([(sweepPowerSt2, 1, wx.EXPAND), (self.sweepPowerTc2, 1, wx.EXPAND)])

        opt_hbox4_5_2 = wx.BoxSizer(wx.HORIZONTAL)

        sweepinitialrangeSt2 = wx.StaticText(self, label='Initial Range (dBm)')

        self.sweepinitialrangeTc2 = wx.TextCtrl(self)
        self.sweepinitialrangeTc2.SetValue('0')

        opt_hbox4_5_2.AddMany([(sweepinitialrangeSt2, 1, wx.EXPAND), (self.sweepinitialrangeTc2, 1, wx.EXPAND)])

        opt_hbox4_6_2 = wx.BoxSizer(wx.HORIZONTAL)

        rangedecSt2 = wx.StaticText(self, label='Range Decrement (dBm)')

        self.rangedecTc2 = wx.TextCtrl(self)
        self.rangedecTc2.SetValue('0')

        opt_hbox4_6_2.AddMany([(rangedecSt2, 1, wx.EXPAND), (self.rangedecTc2, 1, wx.EXPAND)])



        opt_hbox5_2 = wx.BoxSizer(wx.HORIZONTAL)

        st7_2 = wx.StaticText(self, label='Sweep speed')

        sweepSpeedOptions2 = ['80 nm/s', '40 nm/s', '20 nm/s', '10 nm/s', '5 nm/s', '0.5 nm/s', 'auto']
        self.sweepSpeedCb2 = wx.ComboBox(self, choices=sweepSpeedOptions2, style=wx.CB_READONLY, value='auto')
        opt_hbox5_2.AddMany([(st7_2, 1, wx.EXPAND), (self.sweepSpeedCb2, 1, wx.EXPAND)])

        opt_hbox6_2 = wx.BoxSizer(wx.HORIZONTAL)

        st8_2 = wx.StaticText(self, label='Laser output')

        laserOutputOptions2 = ['High power', 'Low SSE']
        self.laserOutputCb2 = wx.ComboBox(self, choices=laserOutputOptions2, style=wx.CB_READONLY, value='High power')
        opt_hbox6_2.AddMany([(st8_2, 1, wx.EXPAND), (self.laserOutputCb2, 1, wx.EXPAND)])

        opt_hbox7_2 = wx.BoxSizer(wx.HORIZONTAL)

        st9_2 = wx.StaticText(self, label='Number of scans')

        numSweepOptions2 = ['1', '2', '3']
        self.numSweepCb2 = wx.ComboBox(self, choices=numSweepOptions2, style=wx.CB_READONLY, value='1')
        opt_hbox7_2.AddMany([(st9_2, 1, wx.EXPAND), (self.numSweepCb2, 1, wx.EXPAND)])

        opt_hbox8_2 = wx.BoxSizer(wx.HORIZONTAL)

        voltagesetst = wx.StaticText(self, label='Voltages (V)')

        self.voltagesetTc2 = wx.TextCtrl(self)
        self.voltagesetTc2.SetValue('0')

        opt_hbox8_2.AddMany([(voltagesetst, 1, wx.EXPAND), (self.voltagesetTc2, 1, wx.EXPAND)])

        opt_hbox9_2 = wx.BoxSizer(wx.HORIZONTAL)
        sq9_2 = wx.StaticText(self, label='Select SMU Channel: ')
        self.Asel3 = wx.CheckBox(self, label='A', pos=(20, 20))
        self.Asel3.SetValue(False)
        self.Bsel3 = wx.CheckBox(self, label='B', pos=(20, 20))
        self.Bsel3.SetValue(False)
        self.Asel3.Bind(wx.EVT_CHECKBOX, self.trueorfalse)
        self.Bsel3.Bind(wx.EVT_CHECKBOX, self.trueorfalse)



        opt_hbox9_2.AddMany([(sq9_2, 1, wx.EXPAND), (self.Asel3, 1, wx.EXPAND), (self.Bsel3, 1, wx.EXPAND)])

        opt_hbox10_2 = wx.BoxSizer(wx.HORIZONTAL)

        self.setvsave = wx.Button(self, label='Save', size=(120, 25))
        #self.setvsave.name = 'routineselectsetv'
        self.setvsave.Bind(wx.EVT_BUTTON, self.routinesavesetv)

        opt_hbox10_2.AddMany([((1, 1), 1), (self.setvsave, 0, wx.EXPAND)])



        opvbox_2.AddMany([(opt_hbox_2, 1, wx.EXPAND), (opt_hbox2_2, 1, wx.EXPAND), (opt_hbox3_2, 1, wx.EXPAND), (opt_hbox4_2, 1, wx.EXPAND), (opt_hbox4_5_2, 1, wx.EXPAND)])

        opvbox2_2.AddMany([(opt_hbox5_2, 1, wx.EXPAND), (opt_hbox6_2, 1, wx.EXPAND), (opt_hbox7_2, 1, wx.EXPAND), (opt_hbox8_2, 0, wx.EXPAND), (opt_hbox4_6_2, 0, wx.EXPAND)])

        ophbox_2.AddMany([(opvbox_2, 1, wx.EXPAND), (opvbox2_2, 1, wx.EXPAND)])

        ophbox_2_2 = wx.BoxSizer(wx.HORIZONTAL)

        ophbox_2_2.AddMany([(hbox0_2_2, 1, wx.EXPAND)])

        opticvbox_2.AddMany([(ophbox_2_2, 0, wx.EXPAND), (ophbox_2, 0, wx.EXPAND), (opt_hbox9_2, 0, wx.EXPAND), (opt_hbox10_2, 0, wx.EXPAND)])

        routineselect.AddMany([(instructions, 0, wx.EXPAND), (electricalroutine, 0, wx.EXPAND), (opticalroutine, 0, wx.EXPAND), (setvwsweeproutine, 0, wx.EXPAND), (setwvsweeproutine, 0, wx.EXPAND)])

        tophbox.AddMany([(elecvbox, 0, wx.EXPAND), (opticvbox, 0, wx.EXPAND)])
        tophbox2.AddMany([(elecvbox2, 0, wx.EXPAND), (opticvbox_2, 1, wx.EXPAND)])

        highestvbox = wx.BoxSizer(wx.VERTICAL)
        highesthbox = wx.BoxSizer(wx.HORIZONTAL)

        highestvbox.AddMany([(tophbox, 1, wx.EXPAND), (tophbox2, 1, wx.EXPAND)])

        highesthbox.AddMany([(routineselect, 0, wx.EXPAND), (highestvbox, 1, wx.EXPAND)])

        self.SetSizer(highesthbox)
        #self.SetSizer(tophbox)


    def cleartext(self, event):
        e = event.GetEventObject()
        if e.GetValue() == 'mA' or e.GetValue() == 'mV' or e.GetValue() == 'V':
            e.SetValue('')
            e.SetForegroundColour(wx.Colour(0, 0, 0))
        if e.GetValue() == '':
            e.SetForegroundColour(wx.Colour(0, 0, 0))
        event.Skip()


    def setnumroutine(self, event):
        c = event.GetEventObject()

        optionsblank = []
        #if c == self.elecroutine:

        if c.GetValue() != '':
            options = []
            for x in range(int(c.GetValue())):
                x = x + 1
                options.append(str(x))

            print(c.name)
            if c.name == 'elecroutine':
                self.routineselectelec.SetItems(options)
                self.elecvolt = [''] * int(c.GetValue())
                self.eleccurrent = [''] * int(c.GetValue())
                self.elecvmax = [''] * int(c.GetValue())
                self.elecvmin = ['']* int(c.GetValue())
                self.elecimin = [''] * int(c.GetValue())
                self.elecimax = [''] * int(c.GetValue())
                self.elecires = [''] * int(c.GetValue())
                self.elecvres = [''] * int(c.GetValue())
                self.eleciv = [''] * int(c.GetValue())
                self.elecrv = [''] * int(c.GetValue())
                self.elecpv = [''] * int(c.GetValue())
                self.elecchannelA = [''] * int(c.GetValue())
                self.elecchannelB = [''] * int(c.GetValue())
                self.elecflagholder = [''] * int(c.GetValue())

            if c.name == 'optroutine':
                self.routineselectopt.SetItems(options)
                self.start = [''] * int(c.GetValue())
                self.stop = [''] * int(c.GetValue())
                self.step = [''] * int(c.GetValue())
                self.sweeppow = [''] * int(c.GetValue())
                self.sweepsped = [''] * int(c.GetValue())
                self.laserout = [''] * int(c.GetValue())
                self.numscans = [''] * int(c.GetValue())
                self.initialran = [''] * int(c.GetValue())
                self.rangedecre = [''] * int(c.GetValue())
                self.opticflagholder = [''] * int(c.GetValue())

            if c.name == 'setwroutine':
                self.routineselectsetw.SetItems(options)
                self.setwvolt = [''] * int(c.GetValue())
                self.setwcurrent = [''] * int(c.GetValue())
                self.setwvmax = [''] * int(c.GetValue())
                self.setwvmin = [''] * int(c.GetValue())
                self.setwimin = [''] * int(c.GetValue())
                self.setwimax = [''] * int(c.GetValue())
                self.setwires = [''] * int(c.GetValue())
                self.setwvres = [''] * int(c.GetValue())
                self.setwiv = [''] * int(c.GetValue())
                self.setwrv = [''] * int(c.GetValue())
                self.setwpv = [''] * int(c.GetValue())
                self.setwchannelA = [''] * int(c.GetValue())
                self.setwchannelB = [''] * int(c.GetValue())
                self.setwwavelengths = [''] * int(c.GetValue())
                self.setwflagholder = [''] * int(c.GetValue())

            if c.name == 'setvroutine':
                self.routineselectsetv.SetItems(options)
                self.setvstart = [''] * int(c.GetValue())
                self.setvstop = [''] * int(c.GetValue())
                self.setvstep = [''] * int(c.GetValue())
                self.setvsweeppow = [''] * int(c.GetValue())
                self.setvsweepsped = [''] * int(c.GetValue())
                self.setvlaserout = [''] * int(c.GetValue())
                self.setvnumscans = [''] * int(c.GetValue())
                self.setvinitialran = [''] * int(c.GetValue())
                self.setvrangedecre = [''] * int(c.GetValue())
                self.setvchannelA = [''] * int(c.GetValue())
                self.setvchannelB = [''] * int(c.GetValue())
                self.setvvoltages = [''] * int(c.GetValue())
                self.setvflagholder = [''] * int(c.GetValue())

        if c.GetValue() == '':
            if c.name == 'elecroutine':
                self.routineselectelec.SetItems(optionsblank)
            if c.name == 'optroutine':
                self.routineselectopt.SetItems(optionsblank)
            if c.name == 'setwroutine':
                self.routineselectsetw.SetItems(optionsblank)
            if c.name == 'setvroutine':
                self.routineselectsetv.SetItems(optionsblank)


    def trueorfalse(self, event):
        e = event.GetEventObject()

        if e == self.Asel and self.Asel.GetValue() == True:
            self.Bsel.SetValue(False)

        if e == self.Asel2 and self.Asel2.GetValue() == True:
            self.Bsel2.SetValue(False)

        if e == self.Asel3 and self.Asel3.GetValue() == True:
            self.Bsel3.SetValue(False)

        if e == self.Bsel and self.Bsel.GetValue() == True:
            self.Asel.SetValue(False)

        if e == self.Bsel2 and self.Bsel2.GetValue() == True:
            self.Asel2.SetValue(False)

        if e == self.Bsel3 and self.Bsel3.GetValue() == True:
            self.Asel3.SetValue(False)

        if e == self.voltsel and self.voltsel.GetValue() == True:
            self.currentsel.SetValue(False)

        if e == self.currentsel and self.currentsel.GetValue() == True:
            self.voltsel.SetValue(False)

        if e == self.voltsel2 and self.voltsel2.GetValue() == True:
            self.currentsel2.SetValue(False)

        if e == self.currentsel2 and self.currentsel2.GetValue() == True:
            self.voltsel2.SetValue(False)

        event.Skip()


    def routinesaveelec(self, event):

        if self.routineselectelec.GetValue() != '':
            value = int(self.routineselectelec.GetValue()) - 1
            self.elecvolt[value] = self.voltsel.GetValue()
            self.eleccurrent[value] = self.currentsel.GetValue()
            self.elecvmax[value] = self.maxsetvoltage.GetValue()
            self.elecvmin[value] = self.minsetvoltage.GetValue()
            self.elecimin[value] = self.minsetcurrent.GetValue()
            self.elecimax[value] = self.maxsetcurrent.GetValue()
            self.elecires[value] = self.resocurrent.GetValue()
            self.elecvres[value] = self.resovoltage.GetValue()
            self.eleciv[value] = self.typesel.GetValue()
            self.elecrv[value] = self.type2sel.GetValue()
            self.elecpv[value] = self.type3sel.GetValue()
            self.elecchannelA[value] = self.Asel.GetValue()
            self.elecchannelB[value] = self.Bsel.GetValue()
            self.elecflagholder[value] = True


    def routinesaveopt(self, event):

        if self.routineselectopt.GetValue() != '':
            value = int(self.routineselectopt.GetValue()) - 1
            self.start[value] = self.startWvlTc.GetValue()
            self.stop[value] = self.stopWvlTc.GetValue()
            self.step[value] = self.stepWvlTc.GetValue()
            self.sweeppow[value] = self.sweepPowerTc.GetValue()
            self.sweepsped[value] = self.sweepSpeedCb.GetValue()
            self.laserout[value] = self.laserOutputCb.GetValue()
            self.numscans[value] = self.numSweepCb.GetValue()
            self.initialran[value] = self.sweepinitialrangeTc.GetValue()
            self.rangedecre[value] = self.rangedecTc.GetValue()
            self.opticflagholder[value] = True


    def routinesavesetw(self, event):

        if self.routineselectsetw.GetValue() != '':
            value = int(self.routineselectsetw.GetValue()) - 1
            self.setwvolt[value] = self.voltsel2.GetValue()
            self.setwcurrent[value] = self.currentsel2.GetValue()
            self.setwvmax[value] = self.maxsetvoltage2.GetValue()
            self.setwvmin[value] = self.minsetvoltage2.GetValue()
            self.setwimin[value] = self.minsetcurrent2.GetValue()
            self.setwimax[value] = self.maxsetcurrent2.GetValue()
            self.setwires[value] = self.resocurrent2.GetValue()
            self.setwvres[value] = self.resovoltage2.GetValue()
            self.setwiv[value] = self.typesel2.GetValue()
            self.setwrv[value] = self.type2sel2.GetValue()
            self.setwpv[value] = self.type3sel2.GetValue()
            self.setwchannelA[value] = self.Asel2.GetValue()
            self.setwchannelB[value] = self.Bsel2.GetValue()
            self.setwwavelengths[value] = self.wavesetTc2.GetValue()
            self.setwflagholder[value] = True


    def routinesavesetv(self, event):

        if self.routineselectsetv.GetValue() != '':
            value = int(self.routineselectsetv.GetValue()) - 1
            self.setvstart[value] = self.startWvlTc2.GetValue()
            self.setvstop[value] = self.stopWvlTc2.GetValue()
            self.setvstep[value] = self.stepWvlTc2.GetValue()
            self.setvsweeppow[value] = self.sweepPowerTc2.GetValue()
            self.setvsweepsped[value] = self.sweepSpeedCb2.GetValue()
            self.setvlaserout[value] = self.laserOutputCb2.GetValue()
            self.setvnumscans[value] = self.numSweepCb2.GetValue()
            self.setvinitialran[value] = self.sweepinitialrangeTc2.GetValue()
            self.setvrangedecre[value] = self.rangedecTc2.GetValue()
            self.setvvoltages[value] = self.voltagesetTc2.GetValue()
            self.setvchannelA[value] = self.Asel3.GetValue()
            self.setvchannelB[value] = self.Bsel3.GetValue()
            self.setvflagholder[value] = True



    def routinepanel(self, event):
        """ When the user opens the routine select dropdown this function saves the data in the panel to a list with a size equal to the number of routines
                                    Arguments:

                                    Returns:

                                    """
        e = event.GetEventObject()
        name = e.name


        if name == 'routineselectelec':

            if self.routineselectelec.GetValue() != '':
                value = int(self.routineselectelec.GetValue()) - 1
                self.elecvolt[value] = self.voltsel.GetValue()
                self.eleccurrent[value] = self.currentsel.GetValue()
                self.elecvmax[value] = self.maxsetvoltage.GetValue()
                self.elecvmin[value] = self.minsetvoltage.GetValue()
                self.elecimin[value] = self.minsetcurrent.GetValue()
                self.elecimax[value] = self.maxsetcurrent.GetValue()
                self.elecires[value] = self.resocurrent.GetValue()
                self.elecvres[value] = self.resovoltage.GetValue()
                self.eleciv[value] = self.typesel.GetValue()
                self.elecrv[value] = self.type2sel.GetValue()
                self.elecpv[value] = self.type3sel.GetValue()
                self.elecchannelA[value] = self.Asel.GetValue()
                self.elecchannelB[value] = self.Bsel.GetValue()
                self.elecflagholder[value] = True

        if name == 'routineselectopt':

            if self.routineselectopt.GetValue() != '':
                value = int(self.routineselectopt.GetValue()) - 1
                self.start[value] = self.startWvlTc.GetValue()
                self.stop[value] = self.stopWvlTc.GetValue()
                self.step[value] = self.stepWvlTc.GetValue()
                self.sweeppow[value] = self.sweepPowerTc.GetValue()
                self.sweepsped[value] = self.sweepSpeedCb.GetValue()
                self.laserout[value] = self.laserOutputCb.GetValue()
                self.numscans[value] = self.numSweepCb.GetValue()
                self.initialran[value] = self.sweepinitialrangeTc.GetValue()
                self.rangedecre[value] = self.rangedecTc.GetValue()
                self.opticflagholder[value] = True


        if name == 'routineselectsetw':

            if self.routineselectsetw.GetValue() != '':
                value = int(self.routineselectsetw.GetValue()) - 1
                self.setwvolt[value] = self.voltsel2.GetValue()
                self.setwcurrent[value] = self.currentsel2.GetValue()
                self.setwvmax[value] = self.maxsetvoltage2.GetValue()
                self.setwvmin[value] = self.minsetvoltage2.GetValue()
                self.setwimin[value] = self.minsetcurrent2.GetValue()
                self.setwimax[value] = self.maxsetcurrent2.GetValue()
                self.setwires[value] = self.resocurrent2.GetValue()
                self.setwvres[value] = self.resovoltage2.GetValue()
                self.setwiv[value] = self.typesel2.GetValue()
                self.setwrv[value] = self.type2sel2.GetValue()
                self.setwpv[value] = self.type3sel2.GetValue()
                self.setwchannelA[value] = self.Asel2.GetValue()
                self.setwchannelB[value] = self.Bsel2.GetValue()
                self.setwwavelengths[value] = self.wavesetTc2.GetValue()
                self.setwflagholder[value] = True

        if name == 'routineselectsetv':

            if self.routineselectsetv.GetValue() != '':
                value = int(self.routineselectsetv.GetValue()) - 1
                self.setvstart[value] = self.startWvlTc2.GetValue()
                self.setvstop[value] = self.stopWvlTc2.GetValue()
                self.setvstep[value] = self.stepWvlTc2.GetValue()
                self.setvsweeppow[value] = self.sweepPowerTc2.GetValue()
                self.setvsweepsped[value] = self.sweepSpeedCb2.GetValue()
                self.setvlaserout[value] = self.laserOutputCb2.GetValue()
                self.setvnumscans[value] = self.numSweepCb2.GetValue()
                self.setvinitialran[value] = self.sweepinitialrangeTc2.GetValue()
                self.setvrangedecre[value] = self.rangedecTc2.GetValue()
                self.setvvoltages[value] = self.voltagesetTc2.GetValue()
                self.setvchannelA[value] = self.Asel3.GetValue()
                self.setvchannelB[value] = self.Bsel3.GetValue()
                self.setvflagholder[value] = True

        event.Skip()


    def swaproutine(self, event):
        """ When the user selects a new routine number in the dropdown menu of the routine panels, this function swaps the saved routine values shown
                                            Arguments:

                                            Returns:

                                            """

        c = event.GetEventObject()
        name = c.name
        print(name)

        if name == 'routineselectelec':

            if self.routineselectelec.GetValue() != '':
                value = int(self.routineselectelec.GetValue()) - 1
                self.voltsel.SetValue(bool(self.elecvolt[value]))# = self.elecvolt[value]
                self.currentsel.SetValue(bool(self.eleccurrent[value]))
                self.maxsetvoltage.SetValue(self.elecvmax[value])
                self.minsetvoltage.SetValue(self.elecvmin[value])
                self.minsetcurrent.SetValue(self.elecimin[value])
                self.maxsetcurrent.SetValue(self.elecimax[value])
                self.resocurrent.SetValue(self.elecires[value])
                self.resovoltage.SetValue(self.elecvres[value])
                self.typesel.SetValue(bool(self.eleciv[value]))
                self.type2sel.SetValue(bool(self.elecrv[value]))
                self.type3sel.SetValue(bool(self.elecpv[value]))
                self.Asel.SetValue(bool(self.elecchannelA[value]))
                self.Bsel.SetValue(bool(self.elecchannelB[value]))
                print(self.maxsetvoltage.GetValue())

        if name == 'routineselectopt':

            if self.routineselectopt.GetValue() != '':
                value = int(self.routineselectopt.GetValue()) - 1
                self.startWvlTc.SetValue(self.start[value])
                self.stopWvlTc.SetValue(self.stop[value])
                self.stepWvlTc.SetValue(self.step[value])
                self.sweepPowerTc.SetValue(self.sweeppow[value])
                self.sweepSpeedCb.SetValue(self.sweepsped[value])
                self.laserOutputCb.SetValue(self.laserout[value])
                self.numSweepCb.SetValue(self.numscans[value])
                self.sweepinitialrangeTc.SetValue(self.initialran[value])
                self.rangedecTc.SetValue(self.rangedecre[value])

        if name == 'routineselectsetw':

            if self.routineselectsetw.GetValue() != '':
                value = int(self.routineselectsetw.GetValue()) - 1
                #self.startWvlTc.SetValue(self.)
                self.voltsel2.SetValue(bool(self.setwvolt[value]))# = self.elecvolt[value]
                self.currentsel2.SetValue(bool(self.setwcurrent[value]))
                self.maxsetvoltage2.SetValue(self.setwvmax[value])
                self.minsetvoltage2.SetValue(self.setwvmin[value])
                self.minsetcurrent2.SetValue(self.setwimin[value])
                self.maxsetcurrent2.SetValue(self.setwimax[value])
                self.resocurrent2.SetValue(self.setwires[value])
                self.resovoltage2.SetValue(self.setwvres[value])
                self.typesel2.SetValue(bool(self.setwiv[value]))
                self.type2sel2.SetValue(bool(self.setwrv[value]))
                self.type3sel2.SetValue(bool(self.setwpv[value]))
                self.Asel2.SetValue(bool(self.setwchannelA[value]))
                self.Bsel2.SetValue(bool(self.setwchannelB[value]))
                self.wavesetTc2.SetValue(self.setwwavelengths[value])

        if name == 'routineselectsetv':

            if self.routineselectsetv.GetValue() != '':
                value = int(self.routineselectsetv.GetValue()) - 1
                self.startWvlTc2.SetValue(self.setvstart[value])
                self.stopWvlTc2.SetValue(self.setvstop[value])
                self.stepWvlTc2.SetValue(self.setvstep[value])
                self.sweepPowerTc2.SetValue(self.setvsweeppow[value])
                self.sweepSpeedCb2.SetValue(self.setvsweepsped[value])
                self.laserOutputCb2.SetValue(self.setvlaserout[value])
                self.numSweepCb2.SetValue(self.setvnumscans[value])
                self.sweepinitialrangeTc2.SetValue(self.setvinitialran[value])
                self.rangedecTc2.SetValue(self.setvrangedecre[value])
                self.Asel3.SetValue(bool(self.setvchannelA[value]))
                self.Bsel3.SetValue(bool(self.setvchannelB[value]))
                self.voltagesetTc2.SetValue(self.setvvoltages[value])


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