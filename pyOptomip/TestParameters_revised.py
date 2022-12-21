
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
import re
import yaml
from outputlogPanel import outputlogPanel
from logWriter import logWriter, logWriterError
import sys
from ElectroOpticDevice import ElectroOpticDevice
from informationframes import infoFrame
import traceback


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
        """
        Creates the highest level formatting for the testing parameters frame
        Returns
        -------

        """
        self.Bind(wx.EVT_CLOSE, self.OnExitApp)
        vbox = wx.BoxSizer(wx.VERTICAL)
        panel = TopPanel(self)
        vbox.Add(panel, proportion=1, border=0, flag=wx.EXPAND)
        self.log = outputlogPanel(self)
        vbox.Add(self.log, 1, wx.EXPAND)
        self.SetSizer(vbox)
        sys.stdout = logWriter(self.log)
        sys.stderr = logWriterError(self.log)


    def OnExitApp(self, event):
        """
        Terminates the window on close
        Parameters
        ----------
        event :

        Returns
        -------

        """
        self.Destroy()


# Panel which contains the panels used for controlling the laser and detectors. It also
# contains the graph.
class TopPanel(wx.Panel):

    def __init__(self, parent, automeasurePanel):
        super(TopPanel, self).__init__(parent)
        self.routineflag = ""
        self.parameterPanel = ParameterPanel(self)
        self.autoMeasurePanel = automeasurePanel
        self.autoMeasure = automeasurePanel.autoMeasure
        self.selected = []
        self.groupselected = []
        self.devicesselected = []
        self.routineselected = []
        self.retrievedataselected = []
        self.subroutineselected = False
        self.routineselected = False
        self.setflag = False
        self.highlightchecked = []
        self.beginning = False
        self.end = False
        self.routinenum = 0
        self.retrievedataflag = False
        self.deviceListset = []
        self.InitUI()


    def InitUI(self):

        sbOuter = wx.StaticBox(self, label='Test Parameter Creation')
        vboxOuter = wx.StaticBoxSizer(sbOuter, wx.VERTICAL)

        #Coordinate file select
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.coordFileTb = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.coordFileTb.SetValue('No file selected')
        self.coordFileSelectBtn = wx.Button(self, wx.ID_OPEN, size=(50, 20))
        self.coordFileSelectBtn.Bind(wx.EVT_BUTTON, self.OnButton_ChooseCoordFile)
        hbox.AddMany([(self.coordFileTb, 1, wx.EXPAND), (self.coordFileSelectBtn, 0, wx.EXPAND)])

        vboxOuter.Add(hbox, 0, wx.EXPAND)

        hboxmain = wx.BoxSizer(wx.HORIZONTAL)
        sbroutine = wx.StaticBox(self, label='Routine Creation')
        vboxroutine = wx.StaticBoxSizer(sbroutine, wx.VERTICAL)
        hboxroutine = wx.BoxSizer(wx.HORIZONTAL)

        self.routinecheckList = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        self.routinecheckList.InsertColumn(0, 'Routine', width=200)
        self.routinecheckList.Bind(wx.EVT_LIST_ITEM_CHECKED, self.routinechecklistchecked)
        #self.routinecheckList.Bind(wx.EVT_LIST_ITEM_CHECKED, self.reorganizeparameters)
        self.routinecheckList.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.routinechecklistunchecked)
        self.subroutinecheckList = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        self.subroutinecheckList.InsertColumn(0, 'Subroutine', width=150)
        self.subroutinecheckList.Bind(wx.EVT_LIST_ITEM_CHECKED, self.subroutinechecked)
        self.subroutinecheckList.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.subroutineunchecked)

        vboxparameters = wx.BoxSizer(wx.VERTICAL)

        # optical save box, to save parameters to temporary list
        optsavebox = wx.BoxSizer(wx.HORIZONTAL)
        self.subsave = wx.Button(self, label='Save as Subroutine', size=(120, 25))
        self.subsave.Bind(wx.EVT_BUTTON, self.subroutinesavebutton)

        #self.routinesave = wx.Button(self, label='Save as Routine', size=(120, 25))
        #self.routinesave.Bind(wx.EVT_BUTTON, self.routinesavebutton)
        optsavebox.AddMany([((1, 1), 1), (self.subsave, 0, wx.EXPAND)]) #(self.routinesave, 0, wx.EXPAND),

        vboxparameters.AddMany([(self.parameterPanel, 0, wx.EXPAND), (optsavebox, 0, wx.EXPAND)])
        hboxroutine.AddMany([(self.routinecheckList, 0, wx.EXPAND), (self.subroutinecheckList, 0, wx.EXPAND), (vboxparameters, 0, wx.EXPAND)])



        vboxroutine.Add(hboxroutine, 1, wx.EXPAND)

        sbdevices = wx.StaticBox(self, label='Device Linking')
        vboxdevices = wx.StaticBoxSizer(sbdevices, wx.VERTICAL)
        hboxdevices = wx.BoxSizer(wx.HORIZONTAL)

        hboxfilter = wx.BoxSizer(wx.HORIZONTAL)
        hboxfilter2 = wx.BoxSizer(wx.HORIZONTAL)
        hboxfilter3 = wx.BoxSizer(wx.HORIZONTAL)
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

        hboxfilter.AddMany(
            [(self.checkAllBtn, 0, wx.EXPAND), (self.uncheckAllBtn, 0, wx.EXPAND), (self.searchFile, 0, wx.EXPAND),
             (self.searchBtn, 0, wx.EXPAND), (self.unsearchBtn, 0, wx.EXPAND)])

        setwaves = wx.StaticText(self, label='Select Wavelength: ')
        self.wav1 = wx.CheckBox(self, label='1310 nm', pos=(20, 20), size=(40, -1))
        self.wav1.SetValue(True)
        self.wav1.Bind(wx.EVT_CHECKBOX, self.wavelengthcheck)

        self.wav2 = wx.CheckBox(self, label='1550 nm', pos=(20, 20), size=(40, -1))
        self.wav2.SetValue(True)
        self.wav2.Bind(wx.EVT_CHECKBOX, self.wavelengthcheck)


        setalign = wx.StaticText(self, label='Select Polarization: ')
        self.te = wx.CheckBox(self, label='TE', pos=(20, 20), size=(40, -1))
        self.te.SetValue(True)
        self.te.Bind(wx.EVT_CHECKBOX, self.wavelengthcheck)

        self.tm = wx.CheckBox(self, label='TM', pos=(20, 20), size=(40, -1))
        self.tm.SetValue(True)
        self.tm.Bind(wx.EVT_CHECKBOX, self.wavelengthcheck)


        hboxfilter2.AddMany([(setwaves, 0, wx.EXPAND), (self.wav1, 0, wx.EXPAND), (self.wav2, 0, wx.EXPAND)])
        hboxfilter3.AddMany([(setalign, 0, wx.EXPAND), (self.te, 0, wx.EXPAND), (self.tm, 0, wx.EXPAND)])

        self.groupcheckList = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        self.groupcheckList.InsertColumn(0, 'Group', width=100)
        self.groupcheckList.Bind(wx.EVT_LIST_ITEM_CHECKED, self.groupchecklistcheckuncheck)
        self.groupcheckList.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.groupchecklistcheckuncheck)
        self.devicecheckList = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        self.devicecheckList.InsertColumn(0, 'Devices', width=175)
        self.devicecheckList.Bind(wx.EVT_LIST_ITEM_CHECKED, self.checkListchecked)
        self.devicecheckList.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.checkListunchecked)
        self.devicedatacheckList = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        self.devicedatacheckList.InsertColumn(0, 'Device Data', width=200)

        self.deviceroutinecheckList = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        self.deviceroutinecheckList.InsertColumn(0, 'Associated Routines', width=200)

        self.removeroutineBtn = wx.Button(self, label='Remove Routine', size=(50, 20))
        self.removeroutineBtn.Bind(wx.EVT_BUTTON, self.removeRoutine)

        vboxchecklist = wx.BoxSizer(wx.VERTICAL)
        vboxchecklist.AddMany([(self.devicedatacheckList, 1, wx.EXPAND), (self.deviceroutinecheckList, 1, wx.EXPAND), (self.removeroutineBtn, 0, wx.EXPAND)])

        hboxset = wx.BoxSizer(wx.HORIZONTAL)
        self.setdeviceBtn = wx.Button(self, label='Set', size=(50, 20))
        self.setdeviceBtn.Bind(wx.EVT_BUTTON, self.deviceset)
        hboxset.Add(self.setdeviceBtn, 1, wx.EXPAND)

        hboxdevices.AddMany([(self.groupcheckList, 1, wx.EXPAND), (self.devicecheckList, 1, wx.EXPAND), (vboxchecklist, 1, wx.EXPAND)])
        vboxdevices.AddMany([(hboxfilter, 0, wx.EXPAND), (hboxfilter2, 0, wx.EXPAND), (hboxfilter3, 0, wx.EXPAND), (hboxdevices, 1, wx.EXPAND), (hboxset, 0, wx.EXPAND)])

        hboxmain.AddMany([(vboxroutine, 0, wx.EXPAND), (vboxdevices, 1, wx.EXPAND)])
        vboxOuter.Add(hboxmain, 1, wx.EXPAND)

        # create output folder selection box
        hboxsave = wx.BoxSizer(wx.HORIZONTAL)
        hboxsave2 = wx.BoxSizer(wx.HORIZONTAL)
        vboxsave = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(self, label='Save folder:')
        self.outputFolderTb = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.outputFolderBtn = wx.Button(self, wx.ID_OPEN, size=(50, 20))
        self.outputFolderBtn.Bind(wx.EVT_BUTTON, self.OnButton_SelectOutputFolder)
        hboxsave.AddMany([(st2, 0, wx.EXPAND), (self.outputFolderTb, 0, wx.EXPAND), (self.outputFolderBtn, 0, wx.EXPAND)])
        vboxsave.Add(hboxsave, 1, wx.EXPAND)
        hboxsave2.Add(vboxsave, 1, wx.EXPAND)


        vboxOuter.Add(hboxsave2, 0, wx.EXPAND)

        hboxexport = wx.BoxSizer(wx.HORIZONTAL)
        self.setBtn = wx.Button(self, label='Send to Automeasure', size=(150, 20))
        self.setBtn.Bind(wx.EVT_BUTTON, self.SetButton)
        self.importBtn = wx.Button(self, label='Import', size=(50, 20))
        self.importBtn.Bind(wx.EVT_BUTTON, self.ImportButton)
        self.exportBtn = wx.Button(self, label='Export', size=(50, 20))
        self.exportBtn.Bind(wx.EVT_BUTTON, self.ExportButton)
        hboxexport.AddMany([((1,1),1), (self.setBtn, 0, wx.EXPAND), (self.importBtn, 0, wx.EXPAND), (self.exportBtn, 0, wx.EXPAND)])

        vboxOuter.AddMany([(hboxexport, 0, wx.EXPAND)])

        self.SetSizer(vboxOuter)

    def OnButton_ChooseCoordFile(self, event):
        """
        When event is triggered this function opens the chosen coordinate file and displays the devices in a checklist
        Parameters
        ----------
        event : the event triggered by clicking the open button to choose the auto-coordinate file

        Returns
        -------

        """
        """ Opens a file dialog to select a coordinate file. """
        try:
            fileDlg = wx.FileDialog(self, "Open", "", "",
                                "Text Files (*.txt)|*.txt",
                                wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            fileDlg.ShowModal()
            self.filter = []
            self.coordFileTb.SetValue(fileDlg.GetFilenames()[0])
        # fileDlg.Destroy()
            self.autoMeasure.readCoordFile(fileDlg.GetPath())
        except:
            return

        self.devicesselected = []

        self.devicedict = {}
        self.devnames = []

        for dev in self.autoMeasure.devices:
            self.devnames.append(dev.getDeviceID())

        a = 1

        for index, dev in enumerate(self.autoMeasure.devices):
            for num in range(index):
                if dev.getDeviceID() == self.autoMeasure.devices[num].getDeviceID():
                    dev.device_id = dev.device_id + str(a)
                    a = a + 1


        for device in self.autoMeasure.devices:
            self.devicedict[device.device_id] = {}
            self.devicedict[device.device_id]['DeviceID'] = device.device_id
            self.devicedict[device.device_id]['Wavelength'] = device.wavelength
            self.devicedict[device.device_id]['Polarization'] = device.polarization
            self.devicedict[device.device_id]['Optical Coordinates'] = device.opticalCoordinates
            self.devicedict[device.device_id]['Type'] = device.type
            self.devicedict[device.device_id]['RoutineCheck'] = device.hasRoutines()
            self.devicedict[device.device_id]['Routines'] = device.routines
            if len(device.electricalCoordinates) != 0:
                self.devicedict[device.device_id]['Electrical Coordinates'] = [device.electricalCoordinates[0][1], device.electricalCoordinates[0][2], device.electricalCoordinates[0][0]]
            else:
                self.devicedict[device.device_id]['Electrical Coordinates'] = []

        global deviceList
        global groupList
        groupList = []
        deviceList = []

        check = True

        for group in self.devicedict.keys():
            for c in groupList:
                if self.devicedict[group]['Type'] == c:
                    check = False
            if check:
                groupList.append(self.devicedict[group]['Type'])
            check = True

        for device in self.devicedict.keys():
            deviceList.append(self.devicedict[device]['DeviceID'])
            self.filter.append(self.devicedict[device]['DeviceID'])


        #for group in deviceListAsObjects:
          #  for c in groupList:
           #     if group.getDeviceType() == c:
           #         check = False
           # if check:
            #    groupList.append(group.getDeviceType())
           # check = True

        # Adds items to the check list
        self.devicecheckList.DeleteAllItems()
        self.groupcheckList.DeleteAllItems()

        for ii, group in enumerate(groupList):
            self.groupcheckList.InsertItem(ii, group)
            #for gro in deviceListAsObjects:
              #  if gro.getDeviceType() == group:
               #     index = deviceListAsObjects.index(gro)  # Stores index of device in list
            #self.groupcheckList.SetItemData(ii, index)
        self.groupcheckList.SortItems(self.checkListSort)  # Make sure items in list are sorted
        self.groupcheckList.EnableCheckBoxes()
        #self.set = [False] * self.groupcheckList.GetItemCount()

        for ii, device in enumerate(deviceList):
            self.devicecheckList.InsertItem(ii, device)
            #for dev in deviceListAsObjects:
             #   if dev.getDeviceID() == device:
              #      index = deviceListAsObjects.index(dev)  # Stores index of device in list
            #self.devicecheckList.SetItemData(ii, index)
        self.devicecheckList.SortItems(self.checkListSort)  # Make sure items in list are sorted
        self.devicecheckList.EnableCheckBoxes()

        


        
        
        
        
        
        

        #self.routineList = ['config', 'align', 'Wavelength Sweep', 'IV Sweep', 'Fixed Wavelength, IV Sweep', 'Fixed Voltage, Wavelength Sweep']

        self.set = [False] * self.devicecheckList.GetItemCount()

        self.routineList = ['Wavelength Sweep', 'Voltage Sweep', 'Current Sweep', 'Set Wavelength Voltage Sweep',
                            'Set Wavelength Current Sweep', 'Set Voltage Wavelength Sweep']

        self.subroutineList = {}

        for routine in self.routineList:

            self.subroutineList[routine] = ['Default']


        self.routinedict = {}
        for routine in self.routineList:
            self.routinedict[routine] = {}
            sublist = self.subroutineList[routine]
            for x in sublist:
                if routine == 'Wavelength Sweep':
                    self.routinedict[routine][x] = {}
                    self.routinedict[routine][x]['ELECflag'] = False
                    self.routinedict[routine][x]['OPTICflag'] = True
                    self.routinedict[routine][x]['setwflag'] = False
                    self.routinedict[routine][x]['setvflag'] = False
                    self.routinedict[routine][x]['Min'] = ''
                    self.routinedict[routine][x]['Max'] = ''
                    self.routinedict[routine][x]['Res'] = ''
                    self.routinedict[routine][x]['IV'] = False
                    self.routinedict[routine][x]['RV'] = False
                    self.routinedict[routine][x]['PV'] = False
                    self.routinedict[routine][x]['Channel A'] = False
                    self.routinedict[routine][x]['Channel B'] = False
                    self.routinedict[routine][x]['Start'] = '1480'
                    self.routinedict[routine][x]['Stop'] = '1580'
                    self.routinedict[routine][x]['Stepsize'] = '1'
                    self.routinedict[routine][x]['Sweeppower'] = '0'
                    self.routinedict[routine][x]['Sweepspeed'] = 'auto'
                    self.routinedict[routine][x]['Laseroutput'] = 'High power'
                    self.routinedict[routine][x]['Numscans'] = '1'
                    self.routinedict[routine][x]['Initialrange'] = '-20'
                    self.routinedict[routine][x]['RangeDec'] = '20'
                    self.routinedict[routine][x]['Wavelengths'] = ''
                    self.routinedict[routine][x]['Voltages'] = ''

                if routine == 'Voltage Sweep':
                    self.routinedict[routine][x] = {}
                    self.routinedict[routine][x]['ELECflag'] = True
                    self.routinedict[routine][x]['OPTICflag'] = False
                    self.routinedict[routine][x]['setwflag'] = False
                    self.routinedict[routine][x]['setvflag'] = False
                    self.routinedict[routine][x]['Min'] = '0'
                    self.routinedict[routine][x]['Max'] = '1'
                    self.routinedict[routine][x]['Res'] = '100'
                    self.routinedict[routine][x]['IV'] = True
                    self.routinedict[routine][x]['RV'] = True
                    self.routinedict[routine][x]['PV'] = True
                    self.routinedict[routine][x]['Channel A'] = True
                    self.routinedict[routine][x]['Channel B'] = False
                    self.routinedict[routine][x]['Start'] = ''
                    self.routinedict[routine][x]['Stop'] = ''
                    self.routinedict[routine][x]['Stepsize'] = ''
                    self.routinedict[routine][x]['Sweeppower'] = ''
                    self.routinedict[routine][x]['Sweepspeed'] = 'auto'
                    self.routinedict[routine][x]['Laseroutput'] = 'High power'
                    self.routinedict[routine][x]['Numscans'] = '1'
                    self.routinedict[routine][x]['Initialrange'] = ''
                    self.routinedict[routine][x]['RangeDec'] = ''
                    self.routinedict[routine][x]['Wavelengths'] = ''
                    self.routinedict[routine][x]['Voltages'] = ''


                if routine == 'Current Sweep':
                    self.routinedict[routine][x] = {}
                    self.routinedict[routine][x]['ELECflag'] = True
                    self.routinedict[routine][x]['OPTICflag'] = False
                    self.routinedict[routine][x]['setwflag'] = False
                    self.routinedict[routine][x]['setvflag'] = False
                    self.routinedict[routine][x]['Min'] = '0'
                    self.routinedict[routine][x]['Max'] = '1'
                    self.routinedict[routine][x]['Res'] = '1'
                    self.routinedict[routine][x]['IV'] = True
                    self.routinedict[routine][x]['RV'] = True
                    self.routinedict[routine][x]['PV'] = True
                    self.routinedict[routine][x]['Channel A'] = True
                    self.routinedict[routine][x]['Channel B'] = False
                    self.routinedict[routine][x]['Start'] = ''
                    self.routinedict[routine][x]['Stop'] = ''
                    self.routinedict[routine][x]['Stepsize'] = ''
                    self.routinedict[routine][x]['Sweeppower'] = ''
                    self.routinedict[routine][x]['Sweepspeed'] = 'auto'
                    self.routinedict[routine][x]['Laseroutput'] = 'High power'
                    self.routinedict[routine][x]['Numscans'] = '1'
                    self.routinedict[routine][x]['Initialrange'] = ''
                    self.routinedict[routine][x]['RangeDec'] = ''
                    self.routinedict[routine][x]['Wavelengths'] = ''
                    self.routinedict[routine][x]['Voltages'] = ''


                if routine == 'Set Wavelength Voltage Sweep':
                    self.routinedict[routine][x] = {}
                    self.routinedict[routine][x]['ELECflag'] = False
                    self.routinedict[routine][x]['OPTICflag'] = False
                    self.routinedict[routine][x]['setwflag'] = True
                    self.routinedict[routine][x]['setvflag'] = False
                    self.routinedict[routine][x]['Min'] = '0'
                    self.routinedict[routine][x]['Max'] = '1'
                    self.routinedict[routine][x]['Res'] = '1'
                    self.routinedict[routine][x]['IV'] = True
                    self.routinedict[routine][x]['RV'] = True
                    self.routinedict[routine][x]['PV'] = True
                    self.routinedict[routine][x]['Channel A'] = True
                    self.routinedict[routine][x]['Channel B'] = False
                    self.routinedict[routine][x]['Start'] = ''
                    self.routinedict[routine][x]['Stop'] = ''
                    self.routinedict[routine][x]['Stepsize'] = ''
                    self.routinedict[routine][x]['Sweeppower'] = ''
                    self.routinedict[routine][x]['Sweepspeed'] = 'auto'
                    self.routinedict[routine][x]['Laseroutput'] = 'High power'
                    self.routinedict[routine][x]['Numscans'] = '1'
                    self.routinedict[routine][x]['Initialrange'] = ''
                    self.routinedict[routine][x]['RangeDec'] = ''
                    self.routinedict[routine][x]['Wavelengths'] = ''
                    self.routinedict[routine][x]['Voltages'] = ''

                if routine == 'Set Wavelength Current Sweep':
                    self.routinedict[routine][x] = {}
                    self.routinedict[routine][x]['ELECflag'] = False
                    self.routinedict[routine][x]['OPTICflag'] = False
                    self.routinedict[routine][x]['setwflag'] = True
                    self.routinedict[routine][x]['setvflag'] = False
                    self.routinedict[routine][x]['Min'] = '0'
                    self.routinedict[routine][x]['Max'] = '5'
                    self.routinedict[routine][x]['Res'] = '0.1'
                    self.routinedict[routine][x]['IV'] = False
                    self.routinedict[routine][x]['RV'] = False
                    self.routinedict[routine][x]['PV'] = False
                    self.routinedict[routine][x]['Channel A'] = True
                    self.routinedict[routine][x]['Channel B'] = False
                    self.routinedict[routine][x]['Start'] = ''
                    self.routinedict[routine][x]['Stop'] = ''
                    self.routinedict[routine][x]['Stepsize'] = ''
                    self.routinedict[routine][x]['Sweeppower'] = ''
                    self.routinedict[routine][x]['Sweepspeed'] = 'auto'
                    self.routinedict[routine][x]['Laseroutput'] = 'High power'
                    self.routinedict[routine][x]['Numscans'] = '1'
                    self.routinedict[routine][x]['Initialrange'] = '-20'
                    self.routinedict[routine][x]['RangeDec'] = '20'
                    self.routinedict[routine][x]['Wavelengths'] = '1480, 1500, 1550'
                    self.routinedict[routine][x]['Voltages'] = ''

                if routine == 'Set Voltage Wavelength Sweep':
                    self.routinedict[routine][x] = {}
                    self.routinedict[routine][x]['ELECflag'] = False
                    self.routinedict[routine][x]['OPTICflag'] = False
                    self.routinedict[routine][x]['setwflag'] = False
                    self.routinedict[routine][x]['setvflag'] = True
                    self.routinedict[routine][x]['Min'] = ''
                    self.routinedict[routine][x]['Max'] = ''
                    self.routinedict[routine][x]['Res'] = ''
                    self.routinedict[routine][x]['IV'] = False
                    self.routinedict[routine][x]['RV'] = False
                    self.routinedict[routine][x]['PV'] = False
                    self.routinedict[routine][x]['Channel A'] = True
                    self.routinedict[routine][x]['Channel B'] = False
                    self.routinedict[routine][x]['Start'] = '1480'
                    self.routinedict[routine][x]['Stop'] = '1580'
                    self.routinedict[routine][x]['Stepsize'] = '1'
                    self.routinedict[routine][x]['Sweeppower'] = ''
                    self.routinedict[routine][x]['Sweepspeed'] = 'auto'
                    self.routinedict[routine][x]['Laseroutput'] = 'High power'
                    self.routinedict[routine][x]['Numscans'] = '1'
                    self.routinedict[routine][x]['Initialrange'] = '-20'
                    self.routinedict[routine][x]['RangeDec'] = '20'
                    self.routinedict[routine][x]['Wavelengths'] = ''
                    self.routinedict[routine][x]['Voltages'] = '1, 2, 3'

        self.routinecheckList.DeleteAllItems()
        self.subroutinecheckList.DeleteAllItems()

        for ii, routine in enumerate(self.routineList):
            self.routinecheckList.InsertItem(ii, routine)
            #for dev in deviceListAsObjects:
             #   if dev.getDeviceID() == routine:
                #    index = deviceListAsObjects.index(dev)  # Stores index of device in list
            #self.routinecheckList.SetItemData(ii, index)
        self.routinecheckList.SortItems(self.checkListSort)  # Make sure items in list are sorted
        self.routinecheckList.EnableCheckBoxes()
        #self.set = [False] * self.routinecheckList.GetItemCount()


        global fileLoaded
        fileLoaded = True
        self.Refresh()

    def wavelengthcheck(self, event):

        self.filter = []
        self.filterdevices = []

        if self.wav1.GetValue() == True:

            for device in self.devicedict.keys():
                if self.devicedict[device]['Wavelength'] == '1310':
                    self.filter.append(self.devicedict[device]['DeviceID'])
                    self.filterdevices.append(device)

        if self.wav2.GetValue() == True:

            for device in self.devicedict.keys():
                if self.devicedict[device]['Wavelength'] == '1550':
                    self.filter.append(self.devicedict[device]['DeviceID'])
                    self.filterdevices.append(device)


        if self.te.GetValue() == False:

                for device in self.filterdevices:
                    if self.devicedict[device]['Polarization'] == 'TE':
                        self.filter.remove(self.devicedict[device]['DeviceID'])
                        #self.filterdevices.remove(device)

        if self.tm.GetValue() == False:

            for device in self.filterdevices:
                if self.devicedict[device]['Polarization'] == 'TM':
                    self.filter.remove(self.devicedict[device]['DeviceID'])
                    # self.filterdevices.remove(device)


        self.groupchecklistcheckuncheck(wx.EVT_BUTTON)

    def subroutinesavebutton(self, event):

        self.inputcheck('subroutinesave')
        if self.inputcheckflag == False:
            print('Please check parameter inputs')
            print("***********************************************")
            return


        if self.parameterPanel.name.GetValue() == '':
            print('Please enter a valid name for this subroutine')
            return

        check = False

        for routine in self.routinedict[self.routinetype].keys():
            if self.parameterPanel.name.GetValue() == routine:
                check = True

        if check == True:
            pass
        else:
            self.routinedict[self.routinetype][self.parameterPanel.name.GetValue()] = {}
            self.subroutineList[self.routinetype].append(self.parameterPanel.name.GetValue())


        self.routinedict[self.routinetype][self.parameterPanel.name.GetValue()]['Min'] = self.parameterPanel.minsetvoltage.GetValue()
        self.routinedict[self.routinetype][self.parameterPanel.name.GetValue()]['Max'] = self.parameterPanel.maxsetvoltage.GetValue()
        self.routinedict[self.routinetype][self.parameterPanel.name.GetValue()]['Res'] = self.parameterPanel.resovoltage.GetValue()
        self.routinedict[self.routinetype][self.parameterPanel.name.GetValue()]['IV'] = self.parameterPanel.typesel.GetValue()
        self.routinedict[self.routinetype][self.parameterPanel.name.GetValue()]['RV'] = self.parameterPanel.type2sel.GetValue()
        self.routinedict[self.routinetype][self.parameterPanel.name.GetValue()]['PV'] = self.parameterPanel.type3sel.GetValue()
        self.routinedict[self.routinetype][self.parameterPanel.name.GetValue()]['Channel A'] = self.parameterPanel.Asel.GetValue()
        self.routinedict[self.routinetype][self.parameterPanel.name.GetValue()]['Channel B'] = self.parameterPanel.Bsel.GetValue()
        self.routinedict[self.routinetype][self.parameterPanel.name.GetValue()]['Start'] = self.parameterPanel.startWvlTc.GetValue()
        self.routinedict[self.routinetype][self.parameterPanel.name.GetValue()]['Stop'] = self.parameterPanel.stopWvlTc.GetValue()
        self.routinedict[self.routinetype][self.parameterPanel.name.GetValue()]['Stepsize'] = self.parameterPanel.stepWvlTc.GetValue()
        self.routinedict[self.routinetype][self.parameterPanel.name.GetValue()]['Sweeppower'] = self.parameterPanel.sweepPowerTc.GetValue()
        self.routinedict[self.routinetype][self.parameterPanel.name.GetValue()]['Sweepspeed'] = self.parameterPanel.sweepSpeedCb.GetValue()
        self.routinedict[self.routinetype][self.parameterPanel.name.GetValue()]['Laseroutput'] = self.parameterPanel.laserOutputCb.GetValue()
        self.routinedict[self.routinetype][self.parameterPanel.name.GetValue()]['Numscans'] = self.parameterPanel.numSweepCb.GetValue()
        self.routinedict[self.routinetype][self.parameterPanel.name.GetValue()]['Initialrange'] = self.parameterPanel.sweepinitialrangeTc.GetValue()
        self.routinedict[self.routinetype][self.parameterPanel.name.GetValue()]['RangeDec'] = self.parameterPanel.rangedecTc.GetValue()
        self.routinedict[self.routinetype][self.parameterPanel.name.GetValue()]['Wavelengths'] = self.parameterPanel.wavesetTc2.GetValue()
        self.routinedict[self.routinetype][self.parameterPanel.name.GetValue()]['Voltages'] = self.parameterPanel.voltagesetTc2.GetValue()

        self.subroutinecheckList.DeleteAllItems()

        subroutList = self.routinedict[self.routinetype].keys()

        for ii, device in enumerate(subroutList):
            self.subroutinecheckList.InsertItem(ii, device)
            # for dev in deviceListAsObjects:
            #  if dev.getDeviceID() == device:
            #      index = deviceListAsObjects.index(dev)  # Stores index of device in list
        # self.devicecheckList.SetItemData(ii, index)
        self.subroutinecheckList.SortItems(self.checkListSort)  # Make sure items in list are sorted
        self.subroutinecheckList.EnableCheckBoxes()
        # self.set = [False] * self.devicecheckList.GetItemCount()

    def removeRoutine(self, event):

        for num in range(self.deviceroutinecheckList.GetItemCount()):
            if self.deviceroutinecheckList.IsItemChecked(num):
                self.devicedict[self.devicesselected[0]]['Routines'].remove(self.deviceroutinecheckList.GetItemText(num))
                if len(self.devicedict[self.devicesselected[0]]['Routines']) == 0:
                    self.devicedict[self.devicesselected[0]]['RoutineCheck'] = False

        self.showdeviceinfo()

    def routinesavebutton(self, event):

        if self.parameterPanel.name.GetValue() == '':
            print('Please enter a valid name for this subroutine')
            return

        check = False

        for routine in self.routinedict.keys():
            if self.parameterPanel.name.GetValue() == routine:
                check = True

        if check == True:
            pass
        else:
            self.routinedict[self.parameterPanel.name.GetValue()] = {}
            self.routinedict[self.parameterPanel.name.GetValue()]['Default'] = {}
            self.routineList.append(self.parameterPanel.name.GetValue())
            self.subroutineList[self.parameterPanel.name.GetValue()] = ['Default']

        self.routinedict[self.parameterPanel.name.GetValue()]['Default']['Min'] = self.parameterPanel.minsetvoltage.GetValue()
        self.routinedict[self.parameterPanel.name.GetValue()]['Default']['Max'] = self.parameterPanel.maxsetvoltage.GetValue()
        self.routinedict[self.parameterPanel.name.GetValue()]['Default']['Res'] = self.parameterPanel.resovoltage.GetValue()
        self.routinedict[self.parameterPanel.name.GetValue()]['Default']['IV'] = self.parameterPanel.typesel.GetValue()
        self.routinedict[self.parameterPanel.name.GetValue()]['Default']['RV'] = self.parameterPanel.type2sel.GetValue()
        self.routinedict[self.parameterPanel.name.GetValue()]['Default']['PV'] = self.parameterPanel.type3sel.GetValue()
        self.routinedict[self.parameterPanel.name.GetValue()]['Default']['Channel A'] = self.parameterPanel.Asel.GetValue()
        self.routinedict[self.parameterPanel.name.GetValue()]['Default']['Channel B'] = self.parameterPanel.Bsel.GetValue()
        self.routinedict[self.parameterPanel.name.GetValue()]['Default']['Start'] = self.parameterPanel.startWvlTc.GetValue()
        self.routinedict[self.parameterPanel.name.GetValue()]['Default']['Stop'] = self.parameterPanel.stopWvlTc.GetValue()
        self.routinedict[self.parameterPanel.name.GetValue()]['Default']['Stepsize'] = self.parameterPanel.stepWvlTc.GetValue()
        self.routinedict[self.parameterPanel.name.GetValue()]['Default']['Sweeppower'] = self.parameterPanel.sweepPowerTc.GetValue()
        self.routinedict[self.parameterPanel.name.GetValue()]['Default']['Sweepspeed'] = self.parameterPanel.sweepSpeedCb.GetValue()
        self.routinedict[self.parameterPanel.name.GetValue()]['Default']['Laseroutput'] = self.parameterPanel.laserOutputCb.GetValue()
        self.routinedict[self.parameterPanel.name.GetValue()]['Default']['Numscans'] = self.parameterPanel.numSweepCb.GetValue()
        self.routinedict[self.parameterPanel.name.GetValue()]['Default']['Initialrange'] = self.parameterPanel.sweepinitialrangeTc.GetValue()
        self.routinedict[self.parameterPanel.name.GetValue()]['Default']['RangeDec'] = self.parameterPanel.rangedecTc.GetValue()
        self.routinedict[self.parameterPanel.name.GetValue()]['Default']['Wavelengths'] = self.parameterPanel.wavesetTc2.GetValue()
        self.routinedict[self.parameterPanel.name.GetValue()]['Default']['Voltages'] = self.parameterPanel.voltagesetTc2.GetValue()

        self.routinecheckList.DeleteAllItems()
        self.subroutinecheckList.DeleteAllItems()

        self.clearparameters()

        for ii, routine in enumerate(self.routineList):
            self.routinecheckList.InsertItem(ii, routine)
            #for dev in deviceListAsObjects:
             #   if dev.getDeviceID() == routine:
                #    index = deviceListAsObjects.index(dev)  # Stores index of device in list
            #self.routinecheckList.SetItemData(ii, index)
        self.routinecheckList.SortItems(self.checkListSort)  # Make sure items in list are sorted
        self.routinecheckList.EnableCheckBoxes()
        #self.set = [False] * self.routinecheckList.GetItemCount()

    def clearparameters(self):

        self.parameterPanel.name.SetValue('')
        self.parameterPanel.minsetvoltage.SetValue('')
        self.parameterPanel.maxsetvoltage.SetValue('')
        self.parameterPanel.resovoltage.SetValue('')
        self.parameterPanel.typesel.SetValue(False)
        self.parameterPanel.type2sel.SetValue(False)
        self.parameterPanel.type3sel.SetValue(False)
        self.parameterPanel.Asel.SetValue(False)
        self.parameterPanel.Bsel.SetValue(False)
        self.parameterPanel.startWvlTc.SetValue('')
        self.parameterPanel.stopWvlTc.SetValue('')
        self.parameterPanel.stepWvlTc.SetValue('')
        self.parameterPanel.sweepPowerTc.SetValue('')
        self.parameterPanel.sweepSpeedCb.SetValue('auto')
        self.parameterPanel.laserOutputCb.SetValue('High power')
        self.parameterPanel.numSweepCb.SetValue('1')
        self.parameterPanel.sweepinitialrangeTc.SetValue('')
        self.parameterPanel.rangedecTc.SetValue('')
        self.parameterPanel.wavesetTc2.SetValue('')
        self.parameterPanel.voltagesetTc2.SetValue('')

    def subroutineunchecked(self, event):

        c = event.GetIndex()
        if c == self.newlyselected:
            self.subroutineselected = False

    def subroutinechecked(self, event):

        c = event.GetIndex()
        self.newlyselected = c

        if self.subroutineselected == True:
            self.subroutinecheckList.CheckItem(self.currentlychecked, False)

        self.currentlychecked = c

        self.subroutineselected = True

        subroutinetype = 'Default'

        for group in range(self.subroutinecheckList.GetItemCount()):
            if self.subroutinecheckList.IsItemChecked(group):
                subroutinetype = self.subroutinecheckList.GetItemText(group)

        self.parameterPanel.name.SetValue(subroutinetype)
        self.parameterPanel.minsetvoltage.SetValue(self.routinedict[self.routinetype][subroutinetype]['Min'])
        self.parameterPanel.maxsetvoltage.SetValue(self.routinedict[self.routinetype][subroutinetype]['Max'])
        self.parameterPanel.resovoltage.SetValue(self.routinedict[self.routinetype][subroutinetype]['Res'])
        self.parameterPanel.typesel.SetValue(self.routinedict[self.routinetype][subroutinetype]['IV'])
        self.parameterPanel.type2sel.SetValue(self.routinedict[self.routinetype][subroutinetype]['RV'])
        self.parameterPanel.type3sel.SetValue(self.routinedict[self.routinetype][subroutinetype]['PV'])
        self.parameterPanel.Asel.SetValue(self.routinedict[self.routinetype][subroutinetype]['Channel A'])
        self.parameterPanel.Bsel.SetValue(self.routinedict[self.routinetype][subroutinetype]['Channel B'])
        self.parameterPanel.startWvlTc.SetValue(self.routinedict[self.routinetype][subroutinetype]['Start'])
        self.parameterPanel.stopWvlTc.SetValue(self.routinedict[self.routinetype][subroutinetype]['Stop'])
        self.parameterPanel.stepWvlTc.SetValue(self.routinedict[self.routinetype][subroutinetype]['Stepsize'])
        self.parameterPanel.sweepPowerTc.SetValue(self.routinedict[self.routinetype][subroutinetype]['Sweeppower'])
        self.parameterPanel.sweepSpeedCb.SetValue(self.routinedict[self.routinetype][subroutinetype]['Sweepspeed'])
        self.parameterPanel.laserOutputCb.SetValue(self.routinedict[self.routinetype][subroutinetype]['Laseroutput'])
        self.parameterPanel.numSweepCb.SetValue(self.routinedict[self.routinetype][subroutinetype]['Numscans'])
        self.parameterPanel.sweepinitialrangeTc.SetValue(self.routinedict[self.routinetype][subroutinetype]['Initialrange'])
        self.parameterPanel.rangedecTc.SetValue(self.routinedict[self.routinetype][subroutinetype]['RangeDec'])
        self.parameterPanel.wavesetTc2.SetValue(self.routinedict[self.routinetype][subroutinetype]['Wavelengths'])
        self.parameterPanel.voltagesetTc2.SetValue(self.routinedict[self.routinetype][subroutinetype]['Voltages'])

    def routinechecklistchecked(self, event):

        c = event.GetIndex()
        self.newlyselectedroutine = c
        self.subroutineselected = False

        self.reorganizeparameters(c)



        if self.routineselected == True:
            self.routinecheckList.CheckItem(self.currentlycheckedroutine, False)

        self.currentlycheckedroutine = c

        for group in range(self.routinecheckList.GetItemCount()):
            if self.routinecheckList.IsItemChecked(group):
                self.routinetype = self.routinecheckList.GetItemText(group)

        self.routineselected = True

        self.parameterPanel.minsetvoltage.SetValue(self.routinedict[self.routinetype]['Default']['Min'])
        self.parameterPanel.maxsetvoltage.SetValue(self.routinedict[self.routinetype]['Default']['Max'])
        self.parameterPanel.resovoltage.SetValue(self.routinedict[self.routinetype]['Default']['Res'])
        self.parameterPanel.typesel.SetValue(self.routinedict[self.routinetype]['Default']['IV'])
        self.parameterPanel.type2sel.SetValue(self.routinedict[self.routinetype]['Default']['RV'])
        self.parameterPanel.type3sel.SetValue(self.routinedict[self.routinetype]['Default']['PV'])
        self.parameterPanel.Asel.SetValue(self.routinedict[self.routinetype]['Default']['Channel A'])
        self.parameterPanel.Bsel.SetValue(self.routinedict[self.routinetype]['Default']['Channel B'])
        self.parameterPanel.startWvlTc.SetValue(self.routinedict[self.routinetype]['Default']['Start'])
        self.parameterPanel.stopWvlTc.SetValue(self.routinedict[self.routinetype]['Default']['Stop'])
        self.parameterPanel.stepWvlTc.SetValue(self.routinedict[self.routinetype]['Default']['Stepsize'])
        self.parameterPanel.sweepPowerTc.SetValue(self.routinedict[self.routinetype]['Default']['Sweeppower'])
        self.parameterPanel.sweepSpeedCb.SetValue(self.routinedict[self.routinetype]['Default']['Sweepspeed'])
        self.parameterPanel.laserOutputCb.SetValue(self.routinedict[self.routinetype]['Default']['Laseroutput'])
        self.parameterPanel.numSweepCb.SetValue(self.routinedict[self.routinetype]['Default']['Numscans'])
        self.parameterPanel.sweepinitialrangeTc.SetValue(self.routinedict[self.routinetype]['Default']['Initialrange'])
        self.parameterPanel.rangedecTc.SetValue(self.routinedict[self.routinetype]['Default']['RangeDec'])
        self.parameterPanel.wavesetTc2.SetValue(self.routinedict[self.routinetype]['Default']['Wavelengths'])
        self.parameterPanel.voltagesetTc2.SetValue(self.routinedict[self.routinetype]['Default']['Voltages'])

        subroutList = []

        #for routine in routinetype:
        #for num in len(self.routinedict)
        subroutList = self.routinedict[self.routinetype].keys()

        # Adds items to the check list
        self.subroutinecheckList.DeleteAllItems()

        for ii, device in enumerate(subroutList):
            self.subroutinecheckList.InsertItem(ii, device)
            #for dev in deviceListAsObjects:
              #  if dev.getDeviceID() == device:
              #      index = deviceListAsObjects.index(dev)  # Stores index of device in list
           # self.devicecheckList.SetItemData(ii, index)
        self.subroutinecheckList.SortItems(self.checkListSort)  # Make sure items in list are sorted
        self.subroutinecheckList.EnableCheckBoxes()
        #self.set = [False] * self.devicecheckList.GetItemCount()

    def routinechecklistunchecked(self, event):

        c = event.GetIndex()
        if c == self.newlyselectedroutine:
            self.routineselected = False
            self.clearparameters()
            self.subroutineselected = False
            self.subroutinecheckList.DeleteAllItems()

    def OnButton_CheckAll(self, event):
        """
        Checks all the devices in the checklist, will not check the devices that have already been set
        Parameters
        ----------
        event : the event triggered when the select all button is pushed

        Returns
        -------

        """

        if self.retrievedataflag == False:
            for ii in range(self.devicecheckList.GetItemCount()):
                if self.set[ii] == False:
                    self.devicecheckList.CheckItem(ii, True)
        else:
            return

    def retrievedata(self, event):
        """
        configures the switch from set data mode to retrieve data mode by setting or unsetting various flags
        Parameters
        ----------
        event : the event triggered when the user presses the retrieve data button

        Returns
        -------

        """

        if self.retrievedataflag == False:
            print("Entering routine extraction mode")
            self.indicator.SetLabel('Retrieve Data Mode')
            self.retrievedataflag = True
            self.beginning = True
            for c in self.selected:
                self.checkList.CheckItem(c, False)
            self.beginning = False
            return

        self.end = True
        for c in self.retrievedataselected:
            self.checkList.CheckItem(c, False)

        for c in self.selected:
            self.checkList.CheckItem(c, True)
        self.end = False

        self.highlightchecked = []
        self.retrievedataselected = []

        for x in range(self.checkList.GetItemCount()):
            self.checkList.SetItemBackgroundColour(x, wx.Colour(255, 255, 255))


        self.indicator.SetLabel('')
        self.retrievedataflag = False
        print("Exiting routine extraction mode")

        #self.retrievedataselected
        #for c in self.set

    def OnButton_UncheckAll(self, event):
        """
        Uncheck all items in the checklist
        Parameters
        ----------
        event : the event triggered by pressing the unselect all button

        Returns
        -------

        """

        for ii in range(self.devicecheckList.GetItemCount()):
            self.devicecheckList.CheckItem(ii, False)

    def highlight(self, event):
        """
        Highlights the items in the checklist that contain the string in the searchfile textctrl box
        Parameters
        ----------
        event : the event triggered by pressing the select keyword button

        Returns
        -------

        """

        for c in range(self.devicecheckList.GetItemCount()):
            if self.set[c] != True and self.searchFile.GetValue() != None and self.searchFile.GetValue() in self.devicecheckList.GetItemText(c, 0):
                self.devicecheckList.SetItemBackgroundColour(c, wx.Colour(255, 255, 0))
            else:
                self.devicecheckList.SetItemBackgroundColour(c, wx.Colour(255,255,255))

            if self.searchFile.GetValue() == '':
                self.devicecheckList.SetItemBackgroundColour(c, wx.Colour(255,255,255))

    def retrievehighlight(self, index):
        """
        When an item is selected while in retrieve data mode this function highlights all the items that have the same
        routine (routine similarity is based on when the routine was originally set, not whether of not the routines are
        numerically the same)
        Parameters
        ----------
        index : the index of the checklist device chosen while in retrieve data mode

        Returns
        -------

        """

        flag = False
        if self.set[index] == True:
            flag = True

        if flag == False:
            return

        num = []
        for d in self.highlightchecked:
            for a in range(len(self.data['index'])):
                if self.data['index'][a] == d:
                    num.append(a)

        for d in range(len(num)):
            if self.data['RoutineNumber'][num[d]] != self.data['RoutineNumber'][index]:
                return

        self.highlightchecked.append(index)



        for c in range(len(self.data['RoutineNumber'])):
            if self.data['RoutineNumber'][c] == self.data['RoutineNumber'][index]:
                d = self.data['index'][c]
                self.checkList.SetItemBackgroundColour(d, wx.Colour(255, 255, 0))

    def retrieveunhighlight(self, index):
        """
        When the device that was previosuly selected becomes unselected this function unhighlights all similar routine devices
        Parameters
        ----------
        index : the index of the checklist device being unselected

        Returns
        -------

        """

        num = []
        for d in self.highlightchecked:
            for a in range(len(self.data['index'])):
                if self.data['index'][a] == d:
                    num.append(a)

        for d in range(len(num)):
            if self.data['RoutineNumber'][num[d]] != self.data['RoutineNumber'][index]:
                return

        self.highlightchecked.remove(index)

        if self.highlightchecked == []:
            for c in range(len(self.data['RoutineNumber'])):
                if self.data['RoutineNumber'][c] == self.data['RoutineNumber'][index]:
                    d = self.data['index'][c]
                    self.checkList.SetItemBackgroundColour(d, wx.Colour(255, 255, 255))

    def SearchDevices(self, event):
        """
        When the search devices button is clicked this function selects all devices in the checklist that contain the string in searchfile textctrl box
        Parameters
        ----------
        event : the event triggered by pressing the search keyword button

        Returns
        -------

        """

        for c in range(len(self.set)):
            if self.set[c] != True and self.searchFile.GetValue() != '' and self.searchFile.GetValue() in self.devicecheckList.GetItemText(c, 0):
                self.devicecheckList.CheckItem(c, True)

    def unSearchDevices(self, event):
        """
        Unselects all devices in checklist that contain the string in searchfile textctrl box
        Parameters
        ----------
        event : the event triggered on pressing the unselect keyword button

        Returns
        -------

        """

        for c in range(len(self.set)):
            if self.set[c] != True and self.searchFile.GetValue() != '' and self.searchFile.GetValue() in self.devicecheckList.GetItemText(c, 0):
                self.devicecheckList.CheckItem(c, False)

    def checkListSort(self, item1, item2):
        """
        Sorts two items passed to it, used to sort the items in the checklist on creation
        Parameters
        ----------
        item1 : integer value
        item2 : integer value

        Returns
        -------
        A -1, a 1 or a 0 depending on the size of the items

        """
        # Items are the client data associated with each entry
        if item2 < item2:
            return -1
        elif item1 > item2:
            return 1
        else:
            return 0

    def checkListchecked(self, event):
        """
        If in set data mode this function adds the now checked device to a list of selected devices, if in retrieve
        data mode this function calls reteivedataswap beginning the data reteival process for the device in quuestion
        Parameters
        ----------
        event : the event triggered by selecting a device in the list

        Returns
        -------

        """
        c = event.GetIndex()

        self.devicesselected.append(self.devicecheckList.GetItemText(c))
        self.deviceroutinecheckList.DeleteAllItems()
        self.showdeviceinfo()

    def showdeviceinfo(self):

        self.deviceroutinecheckList.DeleteAllItems()
        self.devicedatacheckList.DeleteAllItems()

        if len(self.devicesselected) == 1:
            optcoordstring = '(' + str(self.devicedict[self.devicesselected[0]]['Optical Coordinates'][0]) + ',' + str(
                self.devicedict[self.devicesselected[0]]['Optical Coordinates'][1]) + ')'
            self.devicedatacheckList.InsertItem(0, 'Optical Coordinates:' + ' ' + optcoordstring)
            if len(self.devicedict[self.devicesselected[0]]['Electrical Coordinates']) != 0:
                eleccoordstring = '(' + str(self.devicedict[self.devicesselected[0]]['Electrical Coordinates'][0]) + ',' + str(
                    self.devicedict[self.devicesselected[0]]['Electrical Coordinates'][1]) + ')'
                self.devicedatacheckList.InsertItem(1, 'Electrical Coordinates ' + eleccoordstring)
            self.devicedatacheckList.InsertItem(2, 'Polarization:' + ' ' + self.devicedict[self.devicesselected[0]]['Polarization'])
            self.devicedatacheckList.InsertItem(4, 'Wavelength:' + ' ' + self.devicedict[self.devicesselected[0]]['Wavelength'])
            self.devicedatacheckList.InsertItem(6, 'Type:' + ' ' + self.devicedict[self.devicesselected[0]]['Type'])

            for l in range(len(self.devicedict[self.devicesselected[0]]['Routines'])):
                self.deviceroutinecheckList.InsertItem(l, self.devicedict[self.devicesselected[0]]['Routines'][l])

            self.deviceroutinecheckList.EnableCheckBoxes(True)

    def deviceset(self, event):

        for device in self.devicesselected:

            for routine in range(self.subroutinecheckList.GetItemCount()):
                if self.subroutinecheckList.IsItemChecked(routine):
                    routinecode = self.routinetype + ':' + self.subroutinecheckList.GetItemText(routine)
                    self.devicedict[device]['Routines'].append(routinecode)
                    self.devicedict[device]['RoutineCheck'] = True
                    print("Set routine: " + routinecode + " for " + self.devicedict[device]['DeviceID'])

    def groupchecklistcheckuncheck(self, event):

        type = []
        self.devicesselected = []


        for group in range(self.groupcheckList.GetItemCount()):
            if self.groupcheckList.IsItemChecked(group):
                type.append(self.groupcheckList.GetItemText(group))

        deviceList = []

        if type == []:
            for device in self.devicedict.keys():
                for dev in self.filter:
                    if self.devicedict[device]['DeviceID'] == dev:
                        deviceList.append(self.devicedict[device]['DeviceID'])
        else:
            for device in self.devicedict.keys():
                for typ in type:
                    for dev in self.filter:
                        if self.devicedict[device]['Type'] == typ and self.devicedict[device]['DeviceID'] == dev:
                            deviceList.append(self.devicedict[device]['DeviceID'])

        # Adds items to the check list
        self.devicecheckList.DeleteAllItems()

        for ii, device in enumerate(deviceList):
            self.devicecheckList.InsertItem(ii, device)
            #for dev in deviceListAsObjects:
               # if dev.getDeviceID() == device:
               #     index = deviceListAsObjects.index(dev)  # Stores index of device in list
            #self.devicecheckList.SetItemData(ii, index)
        self.devicecheckList.SortItems(self.checkListSort)  # Make sure items in list are sorted
        self.devicecheckList.EnableCheckBoxes()
        self.set = [False] * self.devicecheckList.GetItemCount()

        self.showdeviceinfo()

    def checkListunchecked(self, event):
        """
        If in set data mode this function removes the now unchecked device from the list of selected devices, if in
        retrieve data mode this function removes the device from the list of selected retrieve data devices and
        unhighlights the similar routine devices
        Parameters
        ----------
        event : the event triggered by unselecting a device in the list

        Returns
        -------

        """
        x = event.GetIndex()
        self.devicesselected.remove(self.devicecheckList.GetItemText(x))

        self.showdeviceinfo()

    def OnButton_SelectOutputFolder(self, event):
        """
        Opens the file explorer and allows user to choose the location to save the exported csv file
        Parameters
        ----------
        event : the event triggered by pressing the "open" button to choose the output save location

        Returns
        -------

        """
        dirDlg = wx.DirDialog(self, "Open", "", wx.DD_DEFAULT_STYLE)
        dirDlg.ShowModal()
        self.outputFolderTb.SetValue(dirDlg.GetPath())
        dirDlg.Destroy()

    def OnButton_SelectImportFile(self, event):
        """
        Opens the file explorer and allows user to choose the location to save the exported csv file
        Parameters
        ----------
        event : the event triggered by pressing the "open" button to choose the output save location

        Returns
        -------

        """
        dirDlg = wx.DirDialog(self, "Open", "", wx.DD_DEFAULT_STYLE)
        dirDlg.ShowModal()
        self.importFolderTb = dirDlg.GetPath()
        dirDlg.Destroy()

    def SetButton(self, event):
        """
        This function converts the data input by the user into the various parameter locations and loads it into a
        dictionary that can then be used to either export the data or directly control the equipment
        Parameters
        ----------
        event : the event triggered by pressing the set button

        Returns
        -------

        """

        ROOT_DIR = format(os.getcwd())
        primarysavefilecsv = ROOT_DIR + '\TestParameters.csv'
        primarysavefileymlcwd = ROOT_DIR + '\TestParameters.yaml'

        # dump deviceListAsObjects which contains all the electroopticdevice objects to a file in selected output folder
        # with open(primarysavefileyml, 'w') as f:
        # documents = yaml.dump(deviceListAsObjects, f)

        outputyaml = self.Merge(self.routinedict, self.devicedict)

        # dump deviceListAsObjects which contains all the electroopticdevice objects to a file in current working directory
        with open(primarysavefileymlcwd, 'w') as f:
            documents = yaml.dump(outputyaml, f)

        self.autoMeasurePanel.readYAML(primarysavefileymlcwd)

        #deviceListAsObjects = []

        #for device in self.devicedict.keys():
          #  deviceObject = ElectroOpticDevice(self.devicedict[device]['DeviceID'], self.devicedict[device]['Wavelength'],
                                  #           self.devicedict[device]['Polarization'],
                                  #          self.devicedict[device]['Optical Coordinates'], self.devicedict[device]['Type'])
          #  deviceObject.hasroutines = self.devicedict[device]['RoutineCheck']
           # deviceObject.routines = self.devicedict[device]['Routines']
           # deviceListAsObjects.append(deviceObject)


        #self.autoMeasurePanel.importObjects(self.routinedict, deviceListAsObjects)

    def ExportButton(self, event):
        """
        This function takes the data contained in the data dictionary and formats it into a csv file
        Parameters
        ----------
        event : The event triggered by clicking the export button

        Returns
        -------

        """

        # set paths for saving file to current working directory
        ROOT_DIR = format(os.getcwd())
        primarysavefilecsv = ROOT_DIR + '\TestParameters.csv'
        primarysavefileymlcwd = ROOT_DIR + '\TestParameters.yaml'

        # set path for saving yaml file to selected output folder
        savelocation = self.outputFolderTb.GetValue()
        primarysavefileyml = savelocation + '\TestParameters.yaml'


        # dump deviceListAsObjects which contains all the electroopticdevice objects to a file in selected output folder
        #with open(primarysavefileyml, 'w') as f:
           # documents = yaml.dump(deviceListAsObjects, f)


        outputyaml = self.Merge(self.routinedict, self.devicedict)

        # dump deviceListAsObjects which contains all the electroopticdevice objects to a file in current working directory
        with open(primarysavefileyml, 'w') as f:
            documents = yaml.dump(outputyaml, f)

        print('Exported YAML file as ' + primarysavefileyml)

    def ImportButton(self, event):

        #open file explorer to find file to import
        filDlg = wx.FileDialog(self, "Open", "")
        filDlg.ShowModal()
        self.importFolderTb = filDlg.GetPath()
        filDlg.Destroy()

        originalfile = self.importFolderTb

        #if import file is a yaml file, use this to populate devicelistasobjects
        if '.yaml' in originalfile:

            with open(originalfile, 'r') as file:
                inputfile = yaml.safe_load(file)

            self.devicedict = inputfile['Devices']
            self.routinedict = inputfile['Routines']

            groupList = []
            deviceList = []

            check = True

            for group in self.devicedict.keys():
                for c in groupList:
                    if self.devicedict[group]['Type'] == c:
                        check = False
                if check:
                    groupList.append(self.devicedict[group]['Type'])
                check = True

            for device in self.devicedict.keys():
                deviceList.append(self.devicedict[device]['DeviceID'])

            # for group in deviceListAsObjects:
            #  for c in groupList:
            #     if group.getDeviceType() == c:
            #         check = False
            # if check:
            #    groupList.append(group.getDeviceType())
            # check = True

            # Adds items to the check list
            self.devicecheckList.DeleteAllItems()
            self.groupcheckList.DeleteAllItems()

            for ii, group in enumerate(groupList):
                self.groupcheckList.InsertItem(ii, group)
                # for gro in deviceListAsObjects:
                #  if gro.getDeviceType() == group:
                #     index = deviceListAsObjects.index(gro)  # Stores index of device in list
                # self.groupcheckList.SetItemData(ii, index)
            self.groupcheckList.SortItems(self.checkListSort)  # Make sure items in list are sorted
            self.groupcheckList.EnableCheckBoxes()
            #self.set = [False] * self.groupcheckList.GetItemCount()

            for ii, device in enumerate(deviceList):
                self.devicecheckList.InsertItem(ii, device)
                # for dev in deviceListAsObjects:
                #   if dev.getDeviceID() == device:
                #      index = deviceListAsObjects.index(dev)  # Stores index of device in list
                # self.devicecheckList.SetItemData(ii, index)
            self.devicecheckList.SortItems(self.checkListSort)  # Make sure items in list are sorted
            self.devicecheckList.EnableCheckBoxes()
            # self.set = [False] * self.devicecheckList.GetItemCount()

            self.routineList = self.routinedict.keys()
            self.subroutineList = []
            for list in self.routineList:
                temp = self.routinedict[list].keys()
                self.subroutineList.append(temp)

            self.routinecheckList.DeleteAllItems()
            self.subroutinecheckList.DeleteAllItems()


            for ii, routine in enumerate(self.routineList):
                self.routinecheckList.InsertItem(ii, routine)
                # for dev in deviceListAsObjects:
                #   if dev.getDeviceID() == routine:
                #    index = deviceListAsObjects.index(dev)  # Stores index of device in list
                # self.routinecheckList.SetItemData(ii, index)
            self.routinecheckList.SortItems(self.checkListSort)  # Make sure items in list are sorted
            self.routinecheckList.EnableCheckBoxes()
            #self.set = [False] * self.routinecheckList.GetItemCount()

            global fileLoaded
            fileLoaded = True
            self.Refresh()

    def Merge(self, dict1, dict2):

        output = {}
        output['Routines'] = dict1
        output['Devices'] = dict2

        return output

    def reorganizeparameters(self, c):


        routine = self.routinecheckList.GetItemText(c)
        self.parameterPanel.paramvbox.Show(self.parameterPanel.hbox2) #max
        self.parameterPanel.paramvbox.Show(self.parameterPanel.hbox3) #min
        self.parameterPanel.paramvbox.Show(self.parameterPanel.hbox4) #res
        self.parameterPanel.paramvbox.Show(self.parameterPanel.hbox5) #graph type
        self.parameterPanel.paramvbox.Show(self.parameterPanel.hbox6) #smu channel
        self.parameterPanel.paramvbox.Show(self.parameterPanel.opt_hbox) #start
        self.parameterPanel.paramvbox.Show(self.parameterPanel.opt_hbox2) #stop
        self.parameterPanel.paramvbox.Show(self.parameterPanel.opt_hbox3) #step
        self.parameterPanel.paramvbox.Show(self.parameterPanel.opt_hbox4) #sweep power
        self.parameterPanel.paramvbox.Show(self.parameterPanel.opt_hbox4_5) #initial range
        self.parameterPanel.paramvbox.Show(self.parameterPanel.opt_hbox4_6) #range decr
        self.parameterPanel.paramvbox.Show(self.parameterPanel.opt_hbox5) #sweep speed
        self.parameterPanel.paramvbox.Show(self.parameterPanel.opt_hbox6) #laser output
        self.parameterPanel.paramvbox.Show(self.parameterPanel.opt_hbox7) #number of scans
        self.parameterPanel.paramvbox.Show(self.parameterPanel.hbox7_2) # wavelengths
        self.parameterPanel.paramvbox.Show(self.parameterPanel.opt_hbox8_2) # voltages


        if routine == 'Wavelength Sweep':
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.hbox2)  # max
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.hbox3)  # min
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.hbox4)  # res
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.hbox5)  # graph type
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.hbox6) #laser output
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.hbox7_2)  # wavelengths
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox8_2) #voltages

        if routine == 'Voltage Sweep':
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox)  # start
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox2)  # stop
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox3)  # step
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox4)  # sweep power
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox4_5)  # initial range
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox4_6)  # range decr
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox5)  # sweep speed
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox6)  # laser output
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox7)  # number of scans
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.hbox7_2)  # wavelengths
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox8_2)  # voltages

        if routine == 'Current Sweep':
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox)  # start
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox2)  # stop
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox3)  # step
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox4)  # sweep power
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox4_5)  # initial range
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox4_6)  # range decr
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox5)  # sweep speed
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox6)  # laser output
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox7)  # number of scans
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.hbox7_2)  # wavelengths
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox8_2)  # voltages

        if routine == 'Set Wavelength Voltage Sweep':
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox)  # start
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox2)  # stop
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox3)  # step
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox4)  # sweep power
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox4_5)  # initial range
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox4_6)  # range decr
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox5)  # sweep speed
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox6)  # laser output
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox7)  # number of scans
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox8_2)  # voltages

        if routine == 'Set Wavelength Current Sweep':
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox)  # start
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox2)  # stop
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox3)  # step
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox4)  # sweep power
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox4_5)  # initial range
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox4_6)  # range decr
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox5)  # sweep speed
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox6)  # laser output
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox7)  # number of scans
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.opt_hbox8_2)  # voltages

        if routine == 'Set Voltage Wavelength Sweep':
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.hbox2)  # max
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.hbox3)  # min
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.hbox4)  # res
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.hbox5)  # graph type
            self.parameterPanel.paramvbox.Hide(self.parameterPanel.hbox7_2)  # wavelengths

    def inputcheck(self, setting, ):


        self.inputcheckflag = True

        if setting == 'subroutinesave':

            if self.routinetype == 'Voltage Sweep':

                if self.parameterPanel.maxsetvoltage.GetValue().replace('.', '').isnumeric == False:
                    self.inputcheckflag = False
                    print('Please check max input')
                else:
                    if float(self.parameterPanel.maxsetvoltage.GetValue()) > 240:
                        self.inputcheckflag = False
                        print('Please check max input, cannot be greater than 240V')

                if self.parameterPanel.minsetvoltage.GetValue().replace('.', '').isnumeric == False:
                    self.inputcheckflag = False
                    print('Please check min input')

                if self.parameterPanel.resovoltage.GetValue().replace('.', '').isnumeric == False:
                    self.inputcheckflag = False
                    print('Please check resolution input')
                else:
                    if self.parameterPanel.resovoltage.GetValue() == '0':
                        self.inputcheckflag = False
                        print('Please check resolution value')

                if self.parameterPanel.typesel.GetValue() == False and self.parameterPanel.type2sel.GetValue() == False and self.parameterPanel.type3sel.GetValue() == False:
                    self.inputcheckflag = False
                    print('Please select a plot type')

                if self.parameterPanel.Asel.GetValue() == False and self.parameterPanel.Bsel.GetValue() == False:
                    self.inputcheckflag = False
                    print('Please select an SMU channel')


            if self.routinetype == 'Current Sweep':

                if self.parameterPanel.maxsetvoltage.GetValue().replace('.', '').isnumeric == False:
                    self.inputcheckflag = False
                    print('Please check max input')
                else:
                    if float(self.parameterPanel.maxsetvoltage.GetValue()) > 10000:
                        self.inputcheckflag = False
                        print('Please check max input, cannot be greater than 10A')

                if self.parameterPanel.minsetvoltage.GetValue().replace('.', '').isnumeric == False:
                    self.inputcheckflag = False
                    print('Please check min input')

                if self.parameterPanel.resovoltage.GetValue().replace('.', '').isnumeric == False:
                    self.inputcheckflag = False
                    print('Please check resolution input')
                else:
                    if self.parameterPanel.resovoltage.GetValue() == '0':
                        self.inputcheckflag = False
                        print('Please check resolution value')

                if self.parameterPanel.typesel.GetValue() == False and self.parameterPanel.type2sel.GetValue() == False and self.parameterPanel.type3sel.GetValue() == False:
                    self.inputcheckflag = False
                    print('Please select a plot type')

                if self.parameterPanel.Asel.GetValue() == False and self.parameterPanel.Bsel.GetValue() == False:
                    self.inputcheckflag = False
                    print('Please select an SMU channel')


            if self.routinetype == 'Wavelength Sweep':

                if self.parameterPanel.startWvlTc.GetValue().replace('.', '').isnumeric() == False:
                    self.inputcheckflag = False
                    print('Please check start wavelength')

                if self.parameterPanel.stopWvlTc.GetValue().replace('.', '').isnumeric() == False:
                    self.inputcheckflag = False
                    print('Please check stop wavelength')

                if self.parameterPanel.stepWvlTc.GetValue().replace('.', '').isnumeric() == False:
                    self.inputcheckflag = False
                    print('Please check step distance')

                if self.isNumericMinus(self.parameterPanel.sweepPowerTc.GetValue()) == False:
                    self.inputcheckflag = False
                    print('Please check sweep power')

                if self.isNumericMinus(self.parameterPanel.sweepinitialrangeTc.GetValue()) == False:
                    self.inputcheckflag = False
                    print('Please check initial range')

                if self.parameterPanel.rangedecTc.GetValue().replace('.', '').isnumeric() == False:
                    self.inputcheckflag = False
                    print('Please check range decrement value')

            if self.routinetype == 'Set Wavelength Voltage Sweep':

                if self.parameterPanel.maxsetvoltage.GetValue().replace('.', '').isnumeric == False:
                    self.inputcheckflag = False
                    print('Please check max input')
                else:
                    if float(self.parameterPanel.maxsetvoltage.GetValue()) > 240:  # wont be able to sweep above 240 mA, fix at some point
                        self.inputcheckflag = False
                        print('Please check max input, cannot be greater than 240V')

                if self.parameterPanel.minsetvoltage.GetValue().replace('.', '').isnumeric == False:
                    self.inputcheckflag = False
                    print('Please check min input')

                if self.parameterPanel.resovoltage.GetValue().replace('.', '').isnumeric == False:
                    self.inputcheckflag = False
                    print('Please check resolution input')
                else:
                    if self.parameterPanel.resovoltage.GetValue() == '0':
                        self.inputcheckflag = False
                        print('Please check resolution value')

                if self.parameterPanel.typesel.GetValue() == False and self.parameterPanel.type2sel.GetValue() == False and self.parameterPanel.type3sel.GetValue() == False:
                    self.inputcheckflag = False
                    print('Please select a plot type')

                if self.parameterPanel.Asel.GetValue() == False and self.parameterPanel.Bsel.GetValue() == False:
                    self.inputcheckflag = False
                    print('Please select an SMU channel')

                # if self.parameterPanel.wavesetTc2.GetValue().isnumeric() == False:
                #   self.inputcheckflag = False
                #   print('Please check wavelengths input')

            if self.routinetype == 'Set Wavelength Current Sweep':

                if self.parameterPanel.maxsetvoltage.GetValue().replace('.', '').isnumeric == False:
                    self.inputcheckflag = False
                    print('Please check max input')
                else:
                    if float(self.parameterPanel.maxsetvoltage.GetValue()) > 10000:  # wont be able to sweep above 240 mA, fix at some point
                        self.inputcheckflag = False
                        print('Please check max input, cannot be greater than 10A')

                if self.parameterPanel.minsetvoltage.GetValue().replace('.', '').isnumeric == False:
                    self.inputcheckflag = False
                    print('Please check min input')

                if self.parameterPanel.resovoltage.GetValue().replace('.', '').isnumeric == False:
                    self.inputcheckflag = False
                    print('Please check resolution input')
                else:
                    if self.parameterPanel.resovoltage.GetValue() == '0':
                        self.inputcheckflag = False
                        print('Please check resolution value')

                if self.parameterPanel.typesel.GetValue() == False and self.parameterPanel.type2sel.GetValue() == False and self.parameterPanel.type3sel.GetValue() == False:
                    self.inputcheckflag = False
                    print('Please select a plot type')

                if self.parameterPanel.Asel.GetValue() == False and self.parameterPanel.Bsel.GetValue() == False:
                    self.inputcheckflag = False
                    print('Please select an SMU channel')

                # if self.parameterPanel.wavesetTc2.GetValue().isnumeric() == False:
                #   self.inputcheckflag = False
                #   print('Please check wavelengths input')

            if self.routinetype == 'Set Voltage Wavelength Sweep':

                if self.parameterPanel.startWvlTc.GetValue().replace('.', '').isnumeric() == False:
                    self.inputcheckflag = False
                    print('Please check start wavelength')

                if self.parameterPanel.stopWvlTc.GetValue().replace('.', '').isnumeric() == False:
                    self.inputcheckflag = False
                    print('Please check stop wavelength')

                if self.parameterPanel.stepWvlTc.GetValue().replace('.', '').isnumeric() == False:
                    self.inputcheckflag = False
                    print('Please check step distance')

                if self.isNumericMinus(self.parameterPanel.sweepPowerTc.GetValue()) == False:
                    self.inputcheckflag = False
                    print('Please check sweep power')

                if self.isNumericMinus(self.parameterPanel.sweepinitialrangeTc.GetValue()) == False:
                    self.inputcheckflag = False
                    print('Please check initial range')

                if self.parameterPanel.rangedecTc.GetValue().replace('.', '').isnumeric() == False:
                    self.inputcheckflag = False
                    print('Please check range decrement value')

                #if self.parameterPanel.voltagesetTc2.GetValue().isnumeric() == False:
                    #self.inputcheckflag = False
                    #print('Please check range voltages input')

    def isNumericMinus(self, string):
        """

        Args:
            string ():

        Returns: True if the input string contains no letters but it can have a negative sign at the front
        False if the input string contains any letters other than a negative sign at the beginning


        """
        if string == '':
            return False

        if string.replace('.', '').isnumeric() == False:
            minuscheck = string[0]
            if minuscheck == '-':
                newstring = string[1:]
                if newstring.isnumeric() == False:
                    return False
                else:
                    return True

            else:
                return False
        else:
            return True

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
        reg = re.compile(r'(.-?[0-9]*),(.-?[0-9]*),(T(E|M)),([0-9]+),(.+?),(.+),(.*)')
        # x, y, deviceid, padname, params
        regElec = re.compile(r'(.-?[0-9]+),(.-?[0-9]+),(.+),(.+),(.*)')

        self.devices = []
        self.devSet = set()

        for ii, line in enumerate(dataStrip2):
            if reg.match(line):
                matchRes = reg.findall(line)[0]
                devName = matchRes[6]
                self.devSet.add(devName)

        # Parse the data in each line and put it into a list of devices
        for ii, line in enumerate(dataStrip2):
            if reg.match(line):
                matchRes = reg.findall(line)[0]
                devName = matchRes[6]
                if devName in self.devSet:
                    devName = "X:"+matchRes[0]+"Y:"+matchRes[1]+devName
                self.devSet.add(devName)
                device = ElectroOpticDevice(devName, matchRes[3], matchRes[2], float(matchRes[0]), float(matchRes[1]),
                                            matchRes[5])
                self.devices.append(device)
            else:
                if regElec.match(line):
                    print(line)
                    matchRes = reg.findall(line)[0]
                    devName = matchRes[2]
                    for device in self.devices:
                        if device.getDeviceID() == devName:
                            device.addElectricalCoordinates(matchRes[3], float(matchRes[0]), float(matchRes[1]))
                else:
                    if line == "" or line == "%X-coord,Y-coord,deviceID,padName,params":
                        pass
                    else:
                        print('Warning: The entry\n%s\nis not formatted correctly.' % line)

    def readCSV(self, originalFile):
        """Reads a csv testing parameters file and stores the information as a list of electro-optic device
         objects to be used for automated measurements."""

        global deviceListAsObjects
        deviceListAsObjects = []

        with open(originalFile, 'r') as file:
            rows = []
            for row in file:
                rows.append(row)

            rows.pop(2)
            rows.pop(1)
            rows.pop(0)

            for c in range(len(rows)):
                x = rows[c].split(',')

                deviceToTest = False
                deviceToTestFlag = True

                if len(deviceListAsObjects) == 0:
                    deviceToTest = ElectroOpticDevice(x[1], x[54], x[55], x[56], x[57], x[58])
                else:
                    for device in deviceListAsObjects:
                        if device.getDeviceID() == x[1]:
                            deviceToTest = device
                            deviceToTestFlag = False
                    if deviceToTest == False:
                        print("got here")
                        deviceToTest = ElectroOpticDevice(x[1], x[54], x[55], x[56], x[57], x[58])

                if x[2] == "True":
                    """electrical routine"""
                    if x[6] == "True":
                        """voltage sweep"""
                        deviceToTest.addVoltageSweep(x[8], x[9], x[12], x[14], x[15], x[16], x[17], x[18])
                    if x[7] == "True":
                        """Current sweep"""
                        deviceToTest.addCurrentSweep(x[10], x[11], x[13], x[14], x[15], x[16], x[17], x[18])
                if x[3] == "True":
                    """optical routine"""
                    deviceToTest.addWavelengthSweep(x[19], x[20], x[21], x[22], x[23], x[24], x[25], x[26], x[27])
                if x[4] == "True":
                    """set wavelength iv"""
                    if x[28] == "True":
                        """voltage sweep"""
                        deviceToTest.addSetWavelengthVoltageSweep(x[30], x[31], x[34], x[36], x[37], x[38], x[39], x[40], x[41])
                    if x[29] == "True":
                        """current sweep"""
                        deviceToTest.addSetWavelengthCurrentSweep(x[32], x[33], x[35], x[36], x[37], x[38], x[39], x[40], x[41])
                if x[5] == "True":
                    """set voltage optical sweep"""
                    deviceToTest.addSetVoltageWavelengthSweep(x[42], x[43], x[44], x[45], x[46], x[47], x[48],
                                                              x[49], x[50], x[51], x[52], x[53])
                if deviceToTestFlag:
                    deviceListAsObjects.append(deviceToTest)


#This panel class contains the instructions for going about inputting the routine data for the devices as well as the
#selection menu for the number of different routines
class InstructPanel(wx.Panel):

    def __init__(self, parent, setpanel):
        super(InstructPanel, self).__init__(parent)
        self.setpanel = setpanel
        self.InitUI()


    def InitUI(self):

        # INSTRUCTIONS###################################################################################################

        sbw = wx.StaticBox(self, label='Instructions')
        instructions = wx.StaticBoxSizer(sbw, wx.VERTICAL)

        # create sizers and text for instructions
        steps = wx.BoxSizer(wx.VERTICAL)
        step1 = wx.BoxSizer(wx.HORIZONTAL)
        stp1 = wx.StaticText(self, label='1. Upload automated test coordinate file')
        step1.Add(stp1, 1, wx.EXPAND)

        step1_5 = wx.BoxSizer(wx.HORIZONTAL)
        stp1_5 = wx.StaticText(self, label='coordinate file')
        step1_5.Add(stp1_5, 1, wx.EXPAND)

        step2 = wx.BoxSizer(wx.HORIZONTAL)
        stp2 = wx.StaticText(self, label='2. Select devices you wish to create routines for')
        step2.Add(stp2, 1, wx.EXPAND)

        step2_5 = wx.BoxSizer(wx.HORIZONTAL)
        stp2_5 = wx.StaticText(self, label='create routines for')
        step2_5.Add(stp2_5, 1, wx.EXPAND)

        step3 = wx.BoxSizer(wx.HORIZONTAL)
        stp3 = wx.StaticText(self, label='3. Select number of routines per type of routine')
        step3.Add(stp3, 1, wx.EXPAND)

        step3_5 = wx.BoxSizer(wx.HORIZONTAL)
        stp3_5 = wx.StaticText(self, label='per type of routine')
        step3_5.Add(stp3_5, 1, wx.EXPAND)

        step4 = wx.BoxSizer(wx.HORIZONTAL)
        stp4 = wx.StaticText(self, label='4. Fill in routine data')
        step4.Add(stp4, 1, wx.EXPAND)

        step5 = wx.BoxSizer(wx.HORIZONTAL)
        stp5 = wx.StaticText(self, label='5. Click set button')
        step5.Add(stp5, 1, wx.EXPAND)

        step6 = wx.BoxSizer(wx.HORIZONTAL)
        stp6 = wx.StaticText(self, label='6. Repeat from step 2')
        step6.Add(stp6, 1, wx.EXPAND)

        # format steps
        steps.AddMany([(step1, 1, wx.EXPAND), (step1_5, 1, wx.EXPAND), (step2, 1, wx.EXPAND), (step2_5, 1, wx.EXPAND), (step3, 1, wx.EXPAND), (step3_5, 1, wx.EXPAND), (step4, 1, wx.EXPAND),
                       (step5, 1, wx.EXPAND), (step6, 1, wx.EXPAND)])
        instructions.Add(steps, 1, wx.EXPAND)

        # NUMBER OF ROUTINES SELECTION###################################################################################

        # create general sizer for routine selection
        sb1_3 = wx.StaticBox(self, label='Routine Select')
        routineselect = wx.StaticBoxSizer(sb1_3, wx.VERTICAL)

        # Electrical, set number of routines selection
        electricalroutine = wx.BoxSizer(wx.HORIZONTAL)
        st10_2 = wx.StaticText(self, label='Electrical Routine')
        self.elecroutine = wx.TextCtrl(self, size=(40, 20))
        self.elecroutine.name = 'elecroutine'
        self.elecroutine.SetValue('0')
        self.elecroutine.Bind(wx.EVT_TEXT, self.setnumroutine)
        electricalroutine.AddMany([(st10_2, 1, wx.EXPAND), (self.elecroutine, 0)])

        # Optical, set number of routines selection
        opticalroutine = wx.BoxSizer(wx.HORIZONTAL)
        st11_2 = wx.StaticText(self, label='Optical Routine')
        self.optroutine = wx.TextCtrl(self, size=(40, 20))
        self.optroutine.name = 'optroutine'
        self.optroutine.SetValue('0')
        self.optroutine.Bind(wx.EVT_TEXT, self.setnumroutine)
        opticalroutine.AddMany([(st11_2, 1, wx.EXPAND), (self.optroutine, 0)])

        # Set voltage, wavelength sweep, set number of routines selection
        setvwsweeproutine = wx.BoxSizer(wx.HORIZONTAL)
        st12_2 = wx.StaticText(self, label='Set Voltage')
        self.setvroutine = wx.TextCtrl(self, size=(40, 20))
        self.setvroutine.name = 'setvroutine'
        self.setvroutine.SetValue('0')
        self.setvroutine.Bind(wx.EVT_TEXT, self.setnumroutine)
        setvwsweeproutine.AddMany([(st12_2, 1, wx.EXPAND), (self.setvroutine, 0)])

        # Set wavelength, voltage sweep, set number of routines selection
        setwvsweeproutine = wx.BoxSizer(wx.HORIZONTAL)
        st13_2 = wx.StaticText(self, label='Set Wavelength')
        self.setwroutine = wx.TextCtrl(self, size=(40, 20))
        self.setwroutine.name = 'setwroutine'
        self.setwroutine.SetValue('0')
        self.setwroutine.Bind(wx.EVT_TEXT, self.setnumroutine)
        setwvsweeproutine.AddMany([(st13_2, 1, wx.EXPAND), (self.setwroutine)])

        # format routine selection sizers
        routineselect.AddMany(
            [(instructions, 0, wx.EXPAND), (electricalroutine, 0, wx.EXPAND), (opticalroutine, 0, wx.EXPAND),
             (setvwsweeproutine, 0, wx.EXPAND), (setwvsweeproutine, 0, wx.EXPAND)])

        self.SetSizer(routineselect)


    def setnumroutine(self, event):
        """
        Based on the input for number of different routines this function will create lists for each routine with
        the length equal to the number of routines input
        :param event: the event created on input of number into number of routine menu
        Parameters
        ----------
        event : the event triggered on input of number into number of routine menu

        Returns
        -------

        """
        c = event.GetEventObject()

        optionsblank = []

        if c.GetValue().isdigit() != True and c.GetValue() != '':
            c.SetValue('')
            print('Routine number must be a positive integer')
            return

        if c.GetValue() != '':
            options = []
            for x in range(int(c.GetValue())):
                x = x + 1
                options.append(str(x))

            if c.name == 'elecroutine':
                self.setpanel.routineselectelec.SetItems(options)
                self.setpanel.elecvolt = [''] * int(c.GetValue())
                self.setpanel.eleccurrent = [''] * int(c.GetValue())
                self.setpanel.elecvmax = [''] * int(c.GetValue())
                self.setpanel.elecvmin = ['']* int(c.GetValue())
                self.setpanel.elecimin = [''] * int(c.GetValue())
                self.setpanel.elecimax = [''] * int(c.GetValue())
                self.setpanel.elecires = [''] * int(c.GetValue())
                self.setpanel.elecvres = [''] * int(c.GetValue())
                self.setpanel.eleciv = [''] * int(c.GetValue())
                self.setpanel.elecrv = [''] * int(c.GetValue())
                self.setpanel.elecpv = [''] * int(c.GetValue())
                self.setpanel.elecchannelA = [''] * int(c.GetValue())
                self.setpanel.elecchannelB = [''] * int(c.GetValue())
                self.setpanel.elecflagholder = [''] * int(c.GetValue())

            if c.name == 'optroutine':
                self.setpanel.routineselectopt.SetItems(options)
                self.setpanel.start = [''] * int(c.GetValue())
                self.setpanel.stop = [''] * int(c.GetValue())
                self.setpanel.step = [''] * int(c.GetValue())
                self.setpanel.sweeppow = [''] * int(c.GetValue())
                self.setpanel.sweepsped = [''] * int(c.GetValue())
                self.setpanel.laserout = [''] * int(c.GetValue())
                self.setpanel.numscans = [''] * int(c.GetValue())
                self.setpanel.initialran = [''] * int(c.GetValue())
                self.setpanel.rangedecre = [''] * int(c.GetValue())
                self.setpanel.opticflagholder = [''] * int(c.GetValue())

            if c.name == 'setwroutine':
                self.setpanel.routineselectsetw.SetItems(options)
                self.setpanel.setwvolt = [''] * int(c.GetValue())
                self.setpanel.setwcurrent = [''] * int(c.GetValue())
                self.setpanel.setwvmax = [''] * int(c.GetValue())
                self.setpanel.setwvmin = [''] * int(c.GetValue())
                self.setpanel.setwimin = [''] * int(c.GetValue())
                self.setpanel.setwimax = [''] * int(c.GetValue())
                self.setpanel.setwires = [''] * int(c.GetValue())
                self.setpanel.setwvres = [''] * int(c.GetValue())
                self.setpanel.setwiv = [''] * int(c.GetValue())
                self.setpanel.setwrv = [''] * int(c.GetValue())
                self.setpanel.setwpv = [''] * int(c.GetValue())
                self.setpanel.setwchannelA = [''] * int(c.GetValue())
                self.setpanel.setwchannelB = [''] * int(c.GetValue())
                self.setpanel.setwwavelengths = [''] * int(c.GetValue())
                self.setpanel.setwflagholder = [''] * int(c.GetValue())

            if c.name == 'setvroutine':
                self.setpanel.routineselectsetv.SetItems(options)
                self.setpanel.setvstart = [''] * int(c.GetValue())
                self.setpanel.setvstop = [''] * int(c.GetValue())
                self.setpanel.setvstep = [''] * int(c.GetValue())
                self.setpanel.setvsweeppow = [''] * int(c.GetValue())
                self.setpanel.setvsweepsped = [''] * int(c.GetValue())
                self.setpanel.setvlaserout = [''] * int(c.GetValue())
                self.setpanel.setvnumscans = [''] * int(c.GetValue())
                self.setpanel.setvinitialran = [''] * int(c.GetValue())
                self.setpanel.setvrangedecre = [''] * int(c.GetValue())
                self.setpanel.setvchannelA = [''] * int(c.GetValue())
                self.setpanel.setvchannelB = [''] * int(c.GetValue())
                self.setpanel.setvvoltages = [''] * int(c.GetValue())
                self.setpanel.setvflagholder = [''] * int(c.GetValue())

        if c.GetValue() == '':
            if c.name == 'elecroutine':
                self.setpanel.routineselectelec.SetItems(optionsblank)
            if c.name == 'optroutine':
                self.setpanel.routineselectopt.SetItems(optionsblank)
            if c.name == 'setwroutine':
                self.setpanel.routineselectsetw.SetItems(optionsblank)
            if c.name == 'setvroutine':
                self.setpanel.routineselectsetv.SetItems(optionsblank)


#the Panel responsible for the user input of parameters
class ParameterPanel(wx.Panel):

    def __init__(self, parent):
        super(ParameterPanel, self).__init__(parent)
        self.infoFrame = infoFrame
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

        ##CREATE PARAMETERS PANEL#######################################################################################

        #create electrical panel sizer and necessary vboxes and hboxes
        #sb = wx.StaticBox(self, label='Parameters')
        #self.paramvbox = wx.StaticBoxSizer(sb, wx.VERTICAL)
        self.paramvbox = wx.BoxSizer(wx.VERTICAL)
        self.paramvbox.SetMinSize(300, 400)

        self.hboxname = wx.BoxSizer(wx.HORIZONTAL)
        sqname = wx.StaticText(self, label='Routine Name: ')
        self.name = wx.TextCtrl(self, size=(60, -1))
        self.hboxname.AddMany([(sqname, 0, wx.EXPAND), (self.name, 1, wx.EXPAND)])

        self.paramvbox.Add(self.hboxname, 1, wx.EXPAND)

        #Independent Variable selection
        #self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        #sq1_1 = wx.StaticText(self, label='Select Independent Variable: ')
        #self.voltsel = wx.CheckBox(self, label='Voltage', pos=(20, 20), size=(40, -1))
        #self.voltsel.SetValue(False)
        #self.voltsel.Bind(wx.EVT_CHECKBOX, self.trueorfalse)
        #self.currentsel = wx.CheckBox(self, label='Current', pos=(20, 20))
        #self.currentsel.SetValue(False)
        #self.currentsel.Bind(wx.EVT_CHECKBOX, self.trueorfalse)
        #self.hbox1.AddMany([(sq1_1, 0, wx.EXPAND), (self.voltsel, 1, wx.EXPAND), (self.currentsel, 0, wx.EXPAND)])

        #self.paramvbox.Add(self.hbox1, 1, wx.EXPAND)

        #Voltage and Current maximum select
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        sw1 = wx.StaticText(self, label='Set Max (V/mA):')
        self.maxsetvoltage = wx.TextCtrl(self, size=(60, -1))
        #self.maxsetvoltage.SetValue('V')
        #self.maxsetvoltage.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        #self.maxsetvoltage.SetForegroundColour(wx.Colour(211, 211, 211))
        #self.maxsetcurrent = wx.TextCtrl(self, size=(60, -1))
        #self.maxsetcurrent.SetValue('mA')
        #self.maxsetcurrent.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        #self.maxsetcurrent.SetForegroundColour(wx.Colour(211,211,211))
        self.hbox2.AddMany([(sw1, 1, wx.EXPAND), (self.maxsetvoltage, 0, wx.EXPAND)])# (self.maxsetcurrent, 0, wx.EXPAND)])

        self.paramvbox.Add(self.hbox2, 1, wx.EXPAND)

        #Voltage and current minimum select
        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        sw2 = wx.StaticText(self, label='Set Min (V/mA):')
        #self.minsetcurrent = wx.TextCtrl(self, size=(60, -1))
        #self.minsetcurrent.SetValue('mA')
        #self.minsetcurrent.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        #self.minsetcurrent.SetForegroundColour(wx.Colour(211, 211, 211))
        self.minsetvoltage = wx.TextCtrl(self, size=(60, -1))
        #self.minsetvoltage.SetValue('V')
        #self.minsetvoltage.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        #self.minsetvoltage.SetForegroundColour(wx.Colour(211, 211, 211))
        self.hbox3.AddMany([(sw2, 1, wx.EXPAND), (self.minsetvoltage, 0, wx.EXPAND)])# (self.minsetcurrent, 0, wx.EXPAND)])

        self.paramvbox.Add(self.hbox3, 1, wx.EXPAND)

        #Voltage and Current resolution select
        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        sw3 = wx.StaticText(self, label='Set Resolution (mV/mA):')
        self.resovoltage = wx.TextCtrl(self, size=(60, -1))
        #self.resovoltage.SetValue('V')
        #self.resovoltage.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        #self.resovoltage.SetForegroundColour(wx.Colour(211, 211, 211))
        #self.resocurrent = wx.TextCtrl(self, size=(60, -1))
        #self.resocurrent.SetValue('mA')
        #self.resocurrent.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        #self.resocurrent.SetForegroundColour(wx.Colour(211, 211, 211))
        self.hbox4.AddMany([(sw3, 1, wx.EXPAND), (self.resovoltage, 0, wx.EXPAND)]) #(self.resocurrent, 0, wx.EXPAND)])

        self.paramvbox.Add(self.hbox4, 1, wx.EXPAND)

        #Plot type selection checkboxes
        self.hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        sh2 = wx.StaticText(self, label='Plot Type:')
        self.typesel = wx.CheckBox(self, label='IV/VI', pos=(20, 20))
        self.typesel.SetValue(False)
        self.type2sel = wx.CheckBox(self, label='RV/RI', pos=(20, 20))
        self.type2sel.SetValue(False)
        self.type3sel = wx.CheckBox(self, label='PV/PI', pos=(20, 20))
        self.type3sel.SetValue(False)
        self.hbox5.AddMany([(sh2, 1, wx.EXPAND), (self.typesel, 1, wx.EXPAND), (self.type2sel, 1, wx.EXPAND),
                       (self.type3sel, 1, wx.EXPAND)])

        self.paramvbox.Add(self.hbox5, 1, wx.EXPAND)

        #electrical SMU channel select checkboxes and elecrical save button
        self.hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        sq6_1 = wx.StaticText(self, label='Select SMU Channel: ')
        self.Asel = wx.CheckBox(self, label='A', pos=(20, 20))
        self.Asel.SetValue(False)
        self.Bsel = wx.CheckBox(self, label='B', pos=(20, 20))
        self.Bsel.SetValue(False)
        self.Asel.Bind(wx.EVT_CHECKBOX, self.trueorfalse)
        self.Bsel.Bind(wx.EVT_CHECKBOX, self.trueorfalse)
        self.hbox6.AddMany([(sq6_1, 1, wx.EXPAND), (self.Asel, 1, wx.EXPAND), (self.Bsel, 0, wx.EXPAND)])

        self.paramvbox.Add(self.hbox6, 1, wx.EXPAND)

        #optical start wavelength select
        self.opt_hbox = wx.BoxSizer(wx.HORIZONTAL)
        st4 = wx.StaticText(self, label='Start (nm)')
        self.startWvlTc = wx.TextCtrl(self)
        self.startWvlTc.SetValue('0')
        self.opt_hbox.AddMany([(st4, 1, wx.EXPAND), (self.startWvlTc, 1, wx.EXPAND)])

        self.paramvbox.Add(self.opt_hbox, 1, wx.EXPAND)

        #optical stop wavelength select
        self.opt_hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st5 = wx.StaticText(self, label='Stop (nm)')
        self.stopWvlTc = wx.TextCtrl(self)
        self.stopWvlTc.SetValue('0')
        self.opt_hbox2.AddMany([(st5, 1, wx.EXPAND), (self.stopWvlTc, 1, wx.EXPAND)])

        self.paramvbox.Add(self.opt_hbox2, 1, wx.EXPAND)

        #optical step size select
        self.opt_hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        st6 = wx.StaticText(self, label='Step (nm)')
        self.stepWvlTc = wx.TextCtrl(self)
        self.stepWvlTc.SetValue('0')
        self.opt_hbox3.AddMany([(st6, 1, wx.EXPAND), (self.stepWvlTc, 1, wx.EXPAND)])

        self.paramvbox.Add(self.opt_hbox3, 1, wx.EXPAND)

        #optical sweep power tab
        self.opt_hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        sweepPowerSt = wx.StaticText(self, label='Sweep power (dBm)')
        self.sweepPowerTc = wx.TextCtrl(self)
        self.sweepPowerTc.SetValue('0')
        self.opt_hbox4.AddMany([(sweepPowerSt, 1, wx.EXPAND), (self.sweepPowerTc, 1, wx.EXPAND)])

        self.paramvbox.Add(self.opt_hbox4, 1, wx.EXPAND)

        #optical Initial range tab
        self.opt_hbox4_5 = wx.BoxSizer(wx.HORIZONTAL)
        sweepinitialrangeSt = wx.StaticText(self, label='Initial Range (dBm)')
        self.sweepinitialrangeTc = wx.TextCtrl(self)
        self.sweepinitialrangeTc.SetValue('0')
        self.opt_hbox4_5.AddMany([(sweepinitialrangeSt, 1, wx.EXPAND), (self.sweepinitialrangeTc, 1, wx.EXPAND)])

        self.paramvbox.Add(self.opt_hbox4_5, 1, wx.EXPAND)

        #optical range decrement tab
        self.opt_hbox4_6 = wx.BoxSizer(wx.HORIZONTAL)
        rangedecSt = wx.StaticText(self, label='Range Decrement (dBm)')
        self.rangedecTc = wx.TextCtrl(self)
        self.rangedecTc.SetValue('0')
        self.opt_hbox4_6.AddMany([(rangedecSt, 1, wx.EXPAND), (self.rangedecTc, 1, wx.EXPAND)])

        self.paramvbox.Add(self.opt_hbox4_6, 1, wx.EXPAND)

        #optical sweep speed tab
        self.opt_hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        st7 = wx.StaticText(self, label='Sweep speed')
        sweepSpeedOptions = ['80 nm/s', '40 nm/s', '20 nm/s', '10 nm/s', '5 nm/s', '0.5 nm/s', 'auto']
        self.sweepSpeedCb = wx.ComboBox(self, choices=sweepSpeedOptions, style=wx.CB_READONLY, value='auto')
        self.opt_hbox5.AddMany([(st7, 1, wx.EXPAND), (self.sweepSpeedCb, 1, wx.EXPAND)])

        self.paramvbox.Add(self.opt_hbox5, 1, wx.EXPAND)

        #optical laser output tab
        self.opt_hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        st8 = wx.StaticText(self, label='Laser output')
        laserOutputOptions = ['High power', 'Low SSE']
        self.laserOutputCb = wx.ComboBox(self, choices=laserOutputOptions, style=wx.CB_READONLY, value='High power')
        self.opt_hbox6.AddMany([(st8, 1, wx.EXPAND), (self.laserOutputCb, 1, wx.EXPAND)])

        self.paramvbox.Add(self.opt_hbox6, 1, wx.EXPAND)

        #optical number of scans tab
        self.opt_hbox7 = wx.BoxSizer(wx.HORIZONTAL)
        st9 = wx.StaticText(self, label='Number of scans')
        numSweepOptions = ['1', '2', '3']
        self.numSweepCb = wx.ComboBox(self, choices=numSweepOptions, style=wx.CB_READONLY, value='1')
        self.opt_hbox7.AddMany([(st9, 1, wx.EXPAND), (self.numSweepCb, 1, wx.EXPAND)])

        self.paramvbox.Add(self.opt_hbox7, 1, wx.EXPAND)


        #set wavelength, wavelength select
        self.hbox7_2 = wx.BoxSizer(wx.HORIZONTAL)
        wavesetst = wx.StaticText(self, label='Wavelengths (nm)')
        self.wavesetTc2 = wx.TextCtrl(self)
        self.wavesetTc2.SetValue('0')
        self.hbox7_2.AddMany([(wavesetst, 1, wx.EXPAND), (self.wavesetTc2, 1, wx.EXPAND)])

        self.paramvbox.Add(self.hbox7_2, 1, wx.EXPAND)

        #set voltage, voltage selection
        self.opt_hbox8_2 = wx.BoxSizer(wx.HORIZONTAL)
        voltagesetst = wx.StaticText(self, label='Voltages (V)')
        self.voltinfoBtn = wx.Button(self,id= 0, label = '?', size=(20, 20))
        self.voltinfoBtn.Bind(wx.EVT_BUTTON, self.OnButton_createinfoframe)

        self.voltagesetTc2 = wx.TextCtrl(self)
        self.voltagesetTc2.SetValue('0')
        self.opt_hbox8_2.AddMany([(voltagesetst, 1, wx.EXPAND), (self.voltinfoBtn, 0, wx.EXPAND), (self.voltagesetTc2, 1, wx.EXPAND)])

        self.paramvbox.Add(self.opt_hbox8_2, 1, wx.EXPAND)

        self.SetSizer(self.paramvbox)

    def cleartext(self, event):
        """
        Clears the text in the textctrl boxes on user clicking the box
        Parameters
        ----------
        event : The event triggered when the user clicks the textctrl box

        Returns
        -------

        """
        e = event.GetEventObject()
        if e.GetValue() == 'mA' or e.GetValue() == 'mV' or e.GetValue() == 'V':
            e.SetValue('')
            e.SetForegroundColour(wx.Colour(0, 0, 0))
        if e.GetValue() == '':
            e.SetForegroundColour(wx.Colour(0, 0, 0))
        event.Skip()

    def trueorfalse(self, event):
        """
        For selections that can only be one or the other this function deselects the other option on the selection of one of the parameters
        Parameters
        ----------
        event : event triggered by any one of the parameters that are exclusive

        Returns
        -------

        """
        e = event.GetEventObject()

        if e == self.Asel and self.Asel.GetValue() == True:
            self.Bsel.SetValue(False)

        if e == self.Bsel and self.Bsel.GetValue() == True:
            self.Asel.SetValue(False)

        event.Skip()

    def OnButton_createinfoframe(self, event):
        """Creates filter frame when filter button is pressed"""
        c = event.GetId()
        self.infoclicked = c
        self.createinfoFrame()
        self.Refresh()

    def createinfoFrame(self):
        """Opens up a frame to facilitate filtering of devices within the checklist."""
        try:
            self.infoFrame(None, self.infoclicked)

        except Exception as e:
            dial = wx.MessageDialog(None, 'Could not initiate filter. ' + traceback.format_exc(),
                                    'Error', wx.ICON_ERROR)
            dial.ShowModal()

if __name__ == '__main__':
    app = wx.App(redirect=False)
    testParameters()
    app.MainLoop()
    app.Destroy()
    del app