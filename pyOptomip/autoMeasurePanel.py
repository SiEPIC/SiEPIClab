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

import traceback
import wx
import wx.lib.mixins.listctrl
import myMatplotlibPanel
from autoMeasureProgressDialog import autoMeasureProgressDialog
import os
import time
from filterFrame import filterFrame
import csv
import numpy as np

global deviceList
global deviceListAsObjects


class coordinateMapPanel(wx.Panel):
    def __init__(self, parent, autoMeasure, type):
        """Panel which is used to obtain the necessary parameters to calculate the transformation from
        gds coordinates to motor coordinates. Three devices must be selected and the respective motor
        coordinates saved.

        Args:
            parent: wx Panel
            autoMeasure: The automeasure object used for the automeasure panel"""

        super(coordinateMapPanel, self).__init__(parent)
        self.autoMeasure = autoMeasure
        self.type = type
        self.InitUI()

    def InitUI(self):
        """
        Sets up the layout for the coordinate map panel.
        """
        gbs = wx.GridBagSizer(0, 0)

        # Create text labels for the panel
        stMotorCoord = wx.StaticText(self, label='Motor Coordinates')

        stxMotorCoord = wx.StaticText(self, label='X')
        styMotorCoord = wx.StaticText(self, label='Y')
        stzMotorCoord = wx.StaticText(self, label='Z')

        # Add text labels into grid bag sizer
        gbs.Add(stMotorCoord, pos=(0, 2), span=(1, 2), flag=wx.ALIGN_CENTER)

        gbs.Add(stxMotorCoord, pos=(1, 2), span=(1, 1), flag=wx.ALIGN_CENTER)
        gbs.Add(styMotorCoord, pos=(1, 3), span=(1, 1), flag=wx.ALIGN_CENTER)
        gbs.Add(stzMotorCoord, pos=(1, 4), span=(1, 1), flag=wx.ALIGN_CENTER)

        # Create empty lists to store all necessary coordinates
        self.stxMotorCoordLst = np.zeros(3)
        self.styMotorCoordLst = np.zeros(3)
        self.stzMotorCoordLst = np.zeros(3)
        self.stxGdsCoordLst = np.zeros(3)
        self.styGdsCoordLst = np.zeros(3)
        self.elecxGdsCoordLst = []
        self.elecyGdsCoordLst = []

        self.tbGdsDevice1 = wx.ComboBox(self, size=(200, 20), choices=[], style=wx.TE_PROCESS_ENTER)
        self.tbGdsDevice1.Bind(wx.EVT_CHOICE, self.on_drop_down1)
        self.tbGdsDevice1.Bind(wx.EVT_TEXT, self.on_drop_down1)
        self.tbGdsDevice1.Bind(wx.EVT_TEXT_ENTER, self.SortDropDowns1)

        # Create drop down menus to select devices
        # self.tbGdsDevice1 = wx.Choice(self, size=(200, 20), choices=[])
        # self.tbGdsDevice1.Bind(wx.EVT_CHOICE, self.on_drop_down1)

        # self.tbGdsDevice2 = wx.Choice(self, size=(200, 20), choices=[])
        # self.tbGdsDevice2.Bind(wx.EVT_CHOICE, self.on_drop_down2)

        self.tbGdsDevice2 = wx.ComboBox(self, size=(200, 20), choices=[], style=wx.TE_PROCESS_ENTER)
        self.tbGdsDevice2.Bind(wx.EVT_CHOICE, self.on_drop_down2)
        self.tbGdsDevice2.Bind(wx.EVT_TEXT, self.on_drop_down2)
        self.tbGdsDevice2.Bind(wx.EVT_TEXT_ENTER, self.SortDropDowns2)

        # self.tbGdsDevice3 = wx.Choice(self, size=(200, 20), choices=[])
        # self.tbGdsDevice3.Bind(wx.EVT_CHOICE, self.on_drop_down3)

        self.tbGdsDevice3 = wx.ComboBox(self, size=(200, 20), choices=[], style=wx.TE_PROCESS_ENTER)
        self.tbGdsDevice3.Bind(wx.EVT_CHOICE, self.on_drop_down3)
        self.tbGdsDevice3.Bind(wx.EVT_TEXT, self.on_drop_down3)
        self.tbGdsDevice3.Bind(wx.EVT_TEXT_ENTER, self.SortDropDowns3)

        # List of all drop down menus
        self.GDSDevList = [self.tbGdsDevice1, self.tbGdsDevice2, self.tbGdsDevice3]

        # Get motor coordinates of first device from text box
        stDevice1 = wx.StaticText(self, label='Device %d' % (1))
        self.tbxMotorCoord1 = wx.TextCtrl(self, size=(80, 20))
        self.tbyMotorCoord1 = wx.TextCtrl(self, size=(80, 20))
        self.tbzMotorCoord1 = wx.TextCtrl(self, size=(80, 20))

        btnGetMotorCoord = wx.Button(self, label='Get Pos.', size=(50, 20))

        # Add text boxes to grid bag sizer
        gbs.Add(stDevice1, pos=(2, 0), span=(1, 1))
        gbs.Add(self.tbxMotorCoord1, pos=(2, 2), span=(1, 1))
        gbs.Add(self.tbyMotorCoord1, pos=(2, 3), span=(1, 1))
        gbs.Add(self.tbzMotorCoord1, pos=(2, 4), span=(1, 1))
        gbs.Add(self.GDSDevList[0], pos=(2, 1), span=(1, 1))
        gbs.Add(btnGetMotorCoord, pos=(2, 6), span=(1, 1))

        # For "Get Position" button map a function which is called when it is pressed
        btnGetMotorCoord.Bind(wx.EVT_BUTTON,
                              lambda event, xcoord=self.tbxMotorCoord1, ycoord=self.tbyMotorCoord1,
                                     zcoord=self.tbzMotorCoord1: self.Event_OnCoordButton1(
                                  event, xcoord, ycoord, zcoord))

        # Get motor coordinates of second device from text box
        stDevice2 = wx.StaticText(self, label='Device %d' % (2))
        self.tbxMotorCoord2 = wx.TextCtrl(self, size=(80, 20))
        self.tbyMotorCoord2 = wx.TextCtrl(self, size=(80, 20))
        self.tbzMotorCoord2 = wx.TextCtrl(self, size=(80, 20))

        btnGetMotorCoord = wx.Button(self, label='Get Pos.', size=(50, 20))

        # Add text boxes to grid bag sizer
        gbs.Add(stDevice2, pos=(3, 0), span=(1, 1))
        gbs.Add(self.tbxMotorCoord2, pos=(3, 2), span=(1, 1))
        gbs.Add(self.tbyMotorCoord2, pos=(3, 3), span=(1, 1))
        gbs.Add(self.tbzMotorCoord2, pos=(3, 4), span=(1, 1))
        gbs.Add(self.GDSDevList[1], pos=(3, 1), span=(1, 1))
        gbs.Add(btnGetMotorCoord, pos=(3, 6), span=(1, 1))

        # For "Get Position" button map a function which is called when it is pressed
        btnGetMotorCoord.Bind(wx.EVT_BUTTON,
                              lambda event, xcoord=self.tbxMotorCoord2, ycoord=self.tbyMotorCoord2,
                                     zcoord=self.tbzMotorCoord2: self.Event_OnCoordButton2(
                                  event, xcoord, ycoord, zcoord))

        # Get motor coordinates of first device from text box
        stDevice3 = wx.StaticText(self, label='Device %d' % (3))
        self.tbxMotorCoord3 = wx.TextCtrl(self, size=(80, 20))
        self.tbyMotorCoord3 = wx.TextCtrl(self, size=(80, 20))
        self.tbzMotorCoord3 = wx.TextCtrl(self, size=(80, 20))

        btnGetMotorCoord = wx.Button(self, label='Get Pos.', size=(50, 20))

        # Add text boxes to grid bag sizer
        gbs.Add(stDevice3, pos=(4, 0), span=(1, 1))
        gbs.Add(self.tbxMotorCoord3, pos=(4, 2), span=(1, 1))
        gbs.Add(self.tbyMotorCoord3, pos=(4, 3), span=(1, 1))
        gbs.Add(self.tbzMotorCoord3, pos=(4, 4), span=(1, 1))
        gbs.Add(self.GDSDevList[2], pos=(4, 1), span=(1, 1))
        gbs.Add(btnGetMotorCoord, pos=(4, 6), span=(1, 1))

        # For "Get Position" button map a function which is called when it is pressed
        btnGetMotorCoord.Bind(wx.EVT_BUTTON,
                              lambda event, xcoord=self.tbxMotorCoord3, ycoord=self.tbyMotorCoord3,
                                     zcoord=self.tbzMotorCoord3: self.Event_OnCoordButton3(
                                  event, xcoord, ycoord, zcoord))

        gbs.AddGrowableCol(1)
        gbs.AddGrowableCol(2)
        gbs.AddGrowableCol(3)
        gbs.AddGrowableCol(4)
        self.SetSizerAndFit(gbs)

    def on_drop_down1(self, event):
        """Drop down menu for the first device. When a device is selected, its coordinates are added to the
        gds coordinates list"""
        for dev in deviceListAsObjects:
            if self.GDSDevList[0].GetString(self.GDSDevList[0].GetSelection()) == dev.getDeviceID():
                if dev.getOpticalCoordinates() is not None:
                    self.stxGdsCoordLst[0] = dev.getOpticalCoordinates()[0]
                    self.styGdsCoordLst[0] = dev.getOpticalCoordinates()[1]
                if dev.getReferenceBondPad() is not None:
                    self.elecxGdsCoordLst.append(dev.getReferenceBondPad()[1])
                    self.elecyGdsCoordLst.append(dev.getReferenceBondPad()[2])

    def on_drop_down2(self, event):
        """Drop down menu for the second device. When a device is selected, its coordinates are added to the
        gds coordinates list and associated motor coordinates are added to the motor coordinates list"""
        for dev in deviceListAsObjects:
            if self.GDSDevList[1].GetString(self.GDSDevList[1].GetSelection()) == dev.getDeviceID():
                if dev.getOpticalCoordinates() is not None:
                    self.stxGdsCoordLst[1] = dev.getOpticalCoordinates()[0]
                    self.styGdsCoordLst[1] = dev.getOpticalCoordinates()[1]
                if dev.getReferenceBondPad() is not None:
                    self.elecxGdsCoordLst.append(dev.getReferenceBondPad()[1])
                    self.elecyGdsCoordLst.append(dev.getReferenceBondPad()[2])

    def on_drop_down3(self, event):
        """Drop down menu for the third device. When a device is selected, its coordinates are added to the
        gds coordinates list and associated motor coordinates are added to the motor coordinates list"""
        for dev in deviceListAsObjects:
            if self.GDSDevList[2].GetString(self.GDSDevList[2].GetSelection()) == dev.getDeviceID():
                if dev.getOpticalCoordinates() is not None:
                    self.stxGdsCoordLst[2] = dev.getOpticalCoordinates()[0]
                    self.styGdsCoordLst[2] = dev.getOpticalCoordinates()[1]
                if dev.getReferenceBondPad() is not None:
                    self.elecxGdsCoordLst.append(dev.getReferenceBondPad()[1])
                    self.elecyGdsCoordLst.append(dev.getReferenceBondPad()[2])

    def Event_OnCoordButton1(self, event, xcoord, ycoord, zcoord):
        """ Called when the button is pressed to get the current motor coordinates, and put it into the text box. """
        motorPosition = self.autoMeasure.motorOpt.getPosition()
        xcoord.SetValue(str(motorPosition[0]))
        ycoord.SetValue(str(motorPosition[1]))
        zcoord.SetValue(str(motorPosition[2]))
        self.stxMotorCoordLst[0] = self.tbxMotorCoord1.GetValue()
        self.styMotorCoordLst[0] = self.tbyMotorCoord1.GetValue()
        self.stzMotorCoordLst[0] = self.tbzMotorCoord1.GetValue()

    def Event_OnCoordButton2(self, event, xcoord, ycoord, zcoord):
        """ Called when the button is pressed to get the current motor coordinates, and put it into the text box. """
        motorPosition = self.autoMeasure.motorOpt.getPosition()
        xcoord.SetValue(str(motorPosition[0]))
        ycoord.SetValue(str(motorPosition[1]))
        zcoord.SetValue(str(motorPosition[2]))
        self.stxMotorCoordLst[1] = self.tbxMotorCoord2.GetValue()
        self.styMotorCoordLst[1] = self.tbyMotorCoord2.GetValue()
        self.stzMotorCoordLst[1] = self.tbzMotorCoord2.GetValue()

    def Event_OnCoordButton3(self, event, xcoord, ycoord, zcoord):
        """ Called when the button is pressed to get the current motor coordinates, and put it into the text box. """
        motorPosition = self.autoMeasure.motorOpt.getPosition()
        xcoord.SetValue(str(motorPosition[0]))
        ycoord.SetValue(str(motorPosition[1]))
        zcoord.SetValue(str(motorPosition[2]))
        self.stxMotorCoordLst[2] = self.tbxMotorCoord3.GetValue()
        self.styMotorCoordLst[2] = self.tbyMotorCoord3.GetValue()
        self.stzMotorCoordLst[2] = self.tbzMotorCoord3.GetValue()

    def getMotorCoords(self):
        """ Returns a list of motor coordinates for each entered device. """
        coordsLst = []

        for tcx, tcy, tcz in zip(self.stxMotorCoordLst, self.styMotorCoordLst, self.stzMotorCoordLst):
            xval = tcx  # .GetValue()
            yval = tcy  # .GetValue()
            zval = tcz  # .GetValue()
            # if xval != '' and yval != '' and zval != '':
            coordsLst.append((float(xval), float(yval), float(zval)))

        return coordsLst

    def getGdsCoordsOpt(self):
        """ Returns a list of the GDS coordinates where the laser is to be aligned for each entered
        device. """
        coordsLst = []
        for tcx, tcy in zip(self.stxGdsCoordLst, self.styGdsCoordLst):
            xval = tcx  # .GetValue()
            yval = tcy  # .GetValue()
            if xval != '' and yval != '':
                coordsLst.append((float(xval), float(yval)))
        return coordsLst

    def getGdsCoordsElec(self):
        """ Returns a list of the GDS coordinates of the left-most bond pad for each entered
        device.  """
        coordsLst = []
        for tcx, tcy in zip(self.elecxGdsCoordLst, self.elecyGdsCoordLst):
            xval = tcx.GetValue()
            yval = tcy.GetValue()
            if xval != '' and yval != '':
                coordsLst.append((float(xval), float(yval)))
        return coordsLst

    def PopulateDropDowns(self):
        """Populates drop down menu for device selection within the coordinate map panel"""
        global deviceList
        for GDSDevice in self.GDSDevList:
            GDSDevice.AppendItems(deviceList)

    def SortDropDowns1(self, event):
        """Sort drop downs based on search"""
        global deviceList
        GDSDevice = self.GDSDevList[0]

        deviceList.sort(key=lambda x: 1 if GDSDevice.GetValue() not in x else 0)
        GDSDevice.Clear()
        GDSDevice.AppendItems(deviceList)

    def SortDropDowns2(self, event):
        """Sort drop downs based on search"""
        global deviceList
        GDSDevice = self.GDSDevList[1]

        deviceList.sort(key=lambda x: 1 if GDSDevice.GetValue() not in x else 0)
        GDSDevice.Clear()
        GDSDevice.AppendItems(deviceList)

    def SortDropDowns3(self, event):
        """Sort drop downs based on search"""
        global deviceList
        GDSDevice = self.GDSDevList[2]

        deviceList.sort(key=lambda x: 1 if GDSDevice.GetValue() not in x else 0)
        GDSDevice.Clear()
        GDSDevice.AppendItems(deviceList)


class autoMeasurePanel(wx.Panel):

    def __init__(self, parent, autoMeasure):
        """
        Creates the panel used to automate measurement of chips. Users must upload a text file created
        using the automated coordinate extraction from the Si-EPIC tools k-layout package. Then, three devices
        must be used to create a transform matrix which allows automatic location of specific devices. This
        involves selecting the device from a drop-down menu as well as aligning with the device and recording
        the motor coordinates. Finally, a testing parameters file must either be uploaded or created in the
        testing parameters tab after which automatic measurements can begin.

        Args:
            parent: wx Panel
            autoMeasure: The automeasure object to be used for this panel.
        """
        super(autoMeasurePanel, self).__init__(parent)
        # autoMeasure object used to upload the coordinate file, calculate transform matrices and perform
        # automated measurements
        self.autoMeasure = autoMeasure
        # List of all the names of devices on the chip
        self.device_list = []
        # No testing parameters have been uploaded
        self.parametersImported = False
        # Parameters to be imported from the testing parameters tab or uploaded file
        self.dataimport = {'index': [], 'device': [], 'ELECflag': [], 'OPTICflag': [], 'setwflag': [], 'setvflag': [],
                           'Voltsel': [],
                           'Currentsel': [], 'VoltMin': [], 'VoltMax': [], 'CurrentMin': [], 'CurrentMax': [],
                           'VoltRes': [], 'CurrentRes': [], 'IV': [], 'RV': [], 'PV': [], 'ChannelA': [],
                           'ChannelB': [],
                           'Start': [], 'Stop': [], 'Stepsize': [], 'Sweeppower': [], 'Sweepspeed': [],
                           'Laseroutput': [],
                           'Numscans': [], 'InitialRange': [], 'RangeDec': [], 'setwVoltsel': [], 'setwCurrentsel': [],
                           'setwVoltMin': [], 'setwVoltMax': [], 'setwCurrentMin': [], 'setwCurrentMax': [],
                           'setwVoltRes': [], 'setwCurrentRes': [], 'setwIV': [], 'setwRV': [], 'setwPV': [],
                           'setwChannelA': [], 'setwChannelB': [], 'Wavelengths': [], 'setvStart': [], 'setvStop': [],
                           'setvStepsize': [], 'setvSweeppower': [], 'setvSweepspeed': [], 'setvLaseroutput': [],
                           'setvNumscans': [], 'setvInitialRange': [], 'setvRangeDec': [], 'setvChannelA': [],
                           'setvChannelB': [], 'Voltages': [], 'RoutineNumber': []}
        self.InitUI()

    def InitUI(self):
        """Sets up the layout for the autoMeasurePanel"""

        # List of devices as ElectroOpticDevice objects
        global deviceListAsObjects
        deviceListAsObjects = []

        # Create Automated Measurements Panel
        sbOuter = wx.StaticBox(self, label='Automated Measurements')
        vboxOuter = wx.StaticBoxSizer(sbOuter, wx.VERTICAL)

        # Create File Upload Box
        sbUpload = wx.StaticBox(self, label='File Upload')
        vboxUpload = wx.StaticBoxSizer(sbUpload, wx.VERTICAL)

        # Create Opical Alignment Box
        sbOptical = wx.StaticBox(self, label='Optical Alignment')
        vboxOptical = wx.StaticBoxSizer(sbOptical, wx.VERTICAL)

        # Create Electrical Alignment Box
        sbElectrical = wx.StaticBox(self, label='Electrical Alignment')
        vboxElectrical = wx.StaticBoxSizer(sbElectrical, wx.VERTICAL)

        # Create Electrical Optic Measurement Box
        sbMeasurement = wx.StaticBox(self, label='Electro-Optic Measurements')
        vboxMeasurement = wx.StaticBoxSizer(sbMeasurement, wx.VERTICAL)

        # Add MatPlotLib Panel
        matPlotBox = wx.BoxSizer(wx.HORIZONTAL)
        self.graph = myMatplotlibPanel.myMatplotlibPanel(self)  # use for regular mymatplotlib file
        matPlotBox.Add(self.graph, flag=wx.EXPAND, border=0, proportion=1)

        # Add Coordinate file label
        st1 = wx.StaticText(self, label='Coordinate file:')
        fileLabelBox = wx.BoxSizer(wx.HORIZONTAL)
        fileLabelBox.Add(st1, proportion=1, flag=wx.EXPAND)

        # Allow File Selection
        self.coordFileTb = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.coordFileTb.SetValue('No file selected')
        self.coordFileSelectBtn = wx.Button(self, wx.ID_OPEN, size=(50, 20))
        self.coordFileSelectBtn.Bind(wx.EVT_BUTTON, self.OnButton_ChooseCoordFile)
        fileLoadBox = wx.BoxSizer(wx.HORIZONTAL)
        fileLoadBox.AddMany([(self.coordFileTb, 1, wx.EXPAND), (self.coordFileSelectBtn, 0, wx.EXPAND)])

        # Add Selection Buttons and Filter
        self.checkAllBtn = wx.Button(self, label='Select All', size=(80, 20))
        self.checkAllBtn.Bind(wx.EVT_BUTTON, self.OnButton_CheckAll)
        self.uncheckAllBtn = wx.Button(self, label='Unselect All', size=(80, 20))
        self.uncheckAllBtn.Bind(wx.EVT_BUTTON, self.OnButton_UncheckAll)
        self.filterBtn = wx.Button(self, label='Filter', size=(70, 20))
        self.filterBtn.Bind(wx.EVT_BUTTON, self.OnButton_Filter)

        # Add devices checklist
        self.checkList = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        self.checkList.InsertColumn(0, 'Device', width=500)
        checkListBox = wx.BoxSizer(wx.HORIZONTAL)
        checkListBox.Add(self.checkList, proportion=1, flag=wx.EXPAND)

        # CheckList Search
        self.search = wx.SearchCtrl(self, -1)
        self.search.Bind(wx.EVT_SEARCH, self.OnButton_SearchChecklist)
        searchListBox = wx.BoxSizer(wx.HORIZONTAL)
        searchListBox.Add(self.search, proportion=1, flag=wx.EXPAND)

        # Add Optical Alignment set up
        self.coordMapPanelOpt = coordinateMapPanel(self, self.autoMeasure, "opt")
        opticalBox = wx.BoxSizer(wx.HORIZONTAL)
        opticalBox.Add(self.coordMapPanelOpt, proportion=1, flag=wx.EXPAND)

        # Add Electrical Alignment set up
        self.coordMapPanelElec = coordinateMapPanel(self, self.autoMeasure, "elec")
        electricalBox = wx.BoxSizer(wx.HORIZONTAL)
        electricalBox.Add(self.coordMapPanelElec, proportion=1, flag=wx.EXPAND)

        # Add Measurement Buttons
        self.calculateBtnO = wx.Button(self, label='Calculate', size=(70, 20))
        self.calculateBtnO.Bind(wx.EVT_BUTTON, self.OnButton_CalculateOpt)
        optButtonBox = wx.BoxSizer(wx.HORIZONTAL)
        optButtonBox.AddMany([(self.calculateBtnO, 0, wx.EXPAND)])

        # Add Measurement Buttons
        self.calculateBtnE = wx.Button(self, label='Calculate', size=(70, 20))
        self.calculateBtnE.Bind(wx.EVT_BUTTON, self.OnButton_CalculateElec)
        elecButtonBox = wx.BoxSizer(wx.HORIZONTAL)
        elecButtonBox.AddMany([(self.calculateBtnE, 0, wx.EXPAND)])

        self.startBtn = wx.Button(self, label='Start Measurements', size=(120, 20))
        self.startBtn.Bind(wx.EVT_BUTTON, self.OnButton_Start)
        self.saveBtn = wx.Button(self, label='Save Alignment', size=(120, 20))
        self.saveBtn.Bind(wx.EVT_BUTTON, self.OnButton_Save)
        self.importBtn = wx.Button(self, label='Import Alignment', size=(120, 20))
        self.importBtn.Bind(wx.EVT_BUTTON, self.OnButton_Import)

        self.importBtnCSV = wx.Button(self, label='Import Testing Parameters', size=(150, 20))
        self.importBtnCSV.Bind(wx.EVT_BUTTON, self.OnButton_ImportTestingParameters)

        selectBox = wx.BoxSizer(wx.HORIZONTAL)
        selectBox.AddMany([(self.checkAllBtn, 0, wx.EXPAND), (self.uncheckAllBtn, 0, wx.EXPAND),
                           (self.filterBtn, 0, wx.EXPAND), (self.importBtnCSV, 0, wx.EXPAND)])

        selectBox2 = wx.BoxSizer(wx.HORIZONTAL)
        selectBox2.AddMany([(self.saveBtn, 0, wx.EXPAND),
                            (self.importBtn, 0, wx.EXPAND), (self.startBtn, 0, wx.EXPAND)])

        # Add Save folder label
        st2 = wx.StaticText(self, label='Save folder:')
        saveLabelBox = wx.BoxSizer(wx.HORIZONTAL)
        saveLabelBox.Add(st2, proportion=1, flag=wx.EXPAND)

        # Add Save folder Option
        self.outputFolderTb = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.outputFolderBtn = wx.Button(self, wx.ID_OPEN, size=(50, 20))
        self.outputFolderBtn.Bind(wx.EVT_BUTTON, self.OnButton_SelectOutputFolder)
        saveBox = wx.BoxSizer(wx.HORIZONTAL)
        saveBox.AddMany([(self.outputFolderTb, 1, wx.EXPAND), (self.outputFolderBtn, 0, wx.EXPAND)])

        # Add "Align Laser" label
        st3 = wx.StaticText(self, label='Align Laser')
        moveLabelBox = wx.BoxSizer(wx.HORIZONTAL)
        moveLabelBox.Add(st3, proportion=1, flag=wx.EXPAND)

        # Add "Align Electrical Probe" label
        st = wx.StaticText(self, label='Align Electrical Probe')
        moveElecLabelBox = wx.BoxSizer(wx.HORIZONTAL)
        moveElecLabelBox.Add(st, proportion=1, flag=wx.EXPAND)

        # Add Measurement Buttons
        self.devSelectCbOpt = wx.ComboBox(self, style=wx.CB_READONLY, size=(200, 20))
        self.gotoDevBtnOpt = wx.Button(self, label='Go', size=(70, 20))
        self.gotoDevBtnOpt.Bind(wx.EVT_BUTTON, self.OnButton_GotoDeviceOpt)
        goBoxOpt = wx.BoxSizer(wx.HORIZONTAL)
        goBoxOpt.AddMany([(self.devSelectCbOpt, 1, wx.EXPAND), (self.gotoDevBtnOpt, 0, wx.EXPAND)])

        # Add Measurement Buttons
        self.devSelectCb = wx.ComboBox(self, style=wx.CB_READONLY, size=(200, 20))
        self.gotoDevBtn = wx.Button(self, label='Go', size=(70, 20))
        self.gotoDevBtn.Bind(wx.EVT_BUTTON, self.OnButton_GotoDeviceElec)
        goBoxElec = wx.BoxSizer(wx.HORIZONTAL)
        goBoxElec.AddMany([(self.devSelectCb, 1, wx.EXPAND), (self.gotoDevBtn, 0, wx.EXPAND)])

        # Populate File Upload Box with file upload, save folder selection and device checklist
        vboxUpload.AddMany([(fileLabelBox, 0, wx.EXPAND), (fileLoadBox, 0, wx.EXPAND),
                            (saveLabelBox, 0, wx.EXPAND), (saveBox, 0, wx.EXPAND)])

        # Populate Optical Box with alignment and buttons
        vboxOptical.AddMany([(opticalBox, 0, wx.EXPAND)])

        # Populate Electrical Box with alignment and buttons
        vboxElectrical.AddMany([(electricalBox, 0, wx.EXPAND)])

        # Populate Measurement Box with drop down menu and go button
        vboxMeasurement.AddMany(
            [(moveLabelBox, 0, wx.EXPAND), (goBoxOpt, 0, wx.EXPAND),
             (moveElecLabelBox, 0, wx.EXPAND), (goBoxElec, 0, wx.EXPAND)])

        topBox = wx.BoxSizer(wx.HORIZONTAL)
        topBox.AddMany([(vboxUpload, 0, wx.EXPAND), (vboxMeasurement, 0, wx.EXPAND)])

        checkBox = wx.BoxSizer(wx.VERTICAL)
        checkBox.AddMany([(checkListBox, 0, wx.EXPAND), (searchListBox, 0, wx.EXPAND), (selectBox, 0, wx.EXPAND),
                          (selectBox2, 0, wx.EXPAND)])

        # Add all boxes to outer box
        vboxOuter.AddMany([(topBox, 0, wx.EXPAND), (checkBox, 0, wx.EXPAND), (vboxOptical, 0, wx.EXPAND),
                           (vboxElectrical, 0, wx.EXPAND)])
        matPlotBox.Add(vboxOuter, flag=wx.LEFT | wx.TOP | wx.ALIGN_LEFT, border=0, proportion=0)

        self.SetSizer(matPlotBox)

    def createFilterFrame(self):
        """Opens up a frame to facilitate filtering of devices within the checklist."""
        try:
            filterFrame(None, self.checkList, self.device_list)

        except Exception as e:
            dial = wx.MessageDialog(None, 'Could not initiate filter. ' + traceback.format_exc(),
                                    'Error', wx.ICON_ERROR)
            dial.ShowModal()

    def OnButton_Filter(self, event):
        """Creates filter frame when filter button is pressed"""
        self.createFilterFrame()
        self.Refresh()

    def OnButton_SearchChecklist(self, event):
        """Moves devices with searched term present in ID to the top of the checklist. Have to double click
        magnifying glass for search to proceed."""
        term = self.search.GetStringSelection()

        def checkListSort(item1, item2):
            """Used for sorting the checklist of devices on the chip"""
            # Items are the client data associated with each entry
            if term in deviceListAsObjects[item2].getDeviceID() and term not in deviceListAsObjects[
                item1].getDeviceID():
                return 1
            elif term in deviceListAsObjects[item1].getDeviceID() and term not in deviceListAsObjects[
                item2].getDeviceID():
                return -1
            else:
                return 0

        self.checkList.SortItems(checkListSort)  # Make sure items in list are sorted
        self.checkList.Refresh()

    def OnButton_ChooseCoordFile(self, event):
        """ Opens a file dialog to select a coordinate file. """
        fileDlg = wx.FileDialog(self, "Open", "", "",
                                "Text Files (*.txt)|*.txt",
                                wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        fileDlg.ShowModal()
        self.coordFileTb.SetValue(fileDlg.GetFilenames()[0])
        self.coordFilePath = fileDlg.GetPath()
        self.parseCoordFile(self.coordFilePath)

    def parseCoordFile(self, coordFilePath):
        """Parses given coordinate files and stores all info as a list of electro-Optic Devices
        as well as a list of device ids and populates checklist of devices"""
        self.autoMeasure.readCoordFile(coordFilePath)
        global deviceListAsObjects
        deviceListAsObjects = self.autoMeasure.devices
        self.device_list = deviceListAsObjects
        global deviceList
        deviceList = []
        for device in deviceListAsObjects:
            deviceList.append(device.getDeviceID())
        self.devSelectCb.Clear()
        self.devSelectCb.AppendItems(deviceList)
        self.devSelectCbOpt.Clear()
        self.devSelectCbOpt.AppendItems(deviceList)
        # Adds items to the checklist
        self.checkList.DeleteAllItems()
        for ii, device in enumerate(deviceList):
            self.checkList.InsertItem(ii, device)
            for dev in deviceListAsObjects:
                if dev.getDeviceID() == device:
                    index = deviceListAsObjects.index(dev)  # Stores index of device in list
                    self.checkList.SetItemData(ii, index)
        self.checkList.EnableCheckBoxes()
        self.coordMapPanelOpt.PopulateDropDowns()
        self.coordMapPanelElec.PopulateDropDowns()

    def OnButton_Save(self, event):
        """Saves the gds devices used for alignment as well as motor positions to a csv file"""
        A = self.autoMeasure.findCoordinateTransformOpt(self.coordMapPanelOpt.getMotorCoords(),
                                                        self.coordMapPanelOpt.getGdsCoordsOpt())

        B = self.autoMeasure.findCoordinateTransformElec(self.coordMapPanelElec.getMotorCoords(),
                                                         self.coordMapPanelElec.getGdsCoordsElec())

        # Make a folder with the current time
        fileName = self.coordFileTb.GetValue()
        timeStr = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())
        csvFileName = os.path.join(self.outputFolderTb.GetValue(), timeStr + '_{}.csv'.format(fileName))

        f = open(csvFileName, 'w', newline='')
        writer = csv.writer(f)
        textFilePath = [self.coordFilePath]
        writer.writerow(textFilePath)
        optCoords = self.coordMapPanelOpt.getMotorCoords()
        Opt = ['Optical Alignment']
        writer.writerow(Opt)
        Opt = ['Device', 'Motor x', 'Motor y', 'Motor z']
        writer.writerow(Opt)
        if optCoords:
            if optCoords[0]:
                dev1 = [self.coordMapPanelOpt.tbGdsDevice1.GetString(self.coordMapPanelOpt.tbGdsDevice1.GetSelection()),
                        optCoords[0][0], optCoords[0][1], optCoords[0][2]]
            else:
                dev1 = [self.coordMapPanelOpt.tbGdsDevice1.GetString(self.coordMapPanelOpt.tbGdsDevice1.GetSelection())]
            if optCoords[1]:
                dev2 = [self.coordMapPanelOpt.tbGdsDevice2.GetString(self.coordMapPanelOpt.tbGdsDevice2.GetSelection()),
                        optCoords[1][0], optCoords[1][1], optCoords[1][2]]
            else:
                dev2 = [self.coordMapPanelOpt.tbGdsDevice2.GetString(self.coordMapPanelOpt.tbGdsDevice2.GetSelection())]
            if optCoords[2]:
                dev3 = [self.coordMapPanelOpt.tbGdsDevice3.GetString(self.coordMapPanelOpt.tbGdsDevice3.GetSelection()),
                        optCoords[2][0], optCoords[2][1], optCoords[2][2]]
            else:
                dev3 = [self.coordMapPanelOpt.tbGdsDevice3.GetString(self.coordMapPanelOpt.tbGdsDevice3.GetSelection())]
        else:
            dev1 = [self.coordMapPanelOpt.tbGdsDevice1.GetString(self.coordMapPanelOpt.tbGdsDevice1.GetSelection())]
            dev2 = [self.coordMapPanelOpt.tbGdsDevice2.GetString(self.coordMapPanelOpt.tbGdsDevice2.GetSelection())]
            dev3 = [self.coordMapPanelOpt.tbGdsDevice3.GetString(self.coordMapPanelOpt.tbGdsDevice3.GetSelection())]
        writer.writerow(dev1)
        writer.writerow(dev2)
        writer.writerow(dev3)
        elecCoords = self.coordMapPanelElec.getMotorCoords()
        Elec = ['Electrical Alignment']
        writer.writerow(Elec)
        elec = ['Device', 'Motor x', 'Motor y', 'Motor z']
        writer.writerow(elec)
        if elecCoords:
            if elecCoords[0]:
                dev1 = [
                    self.coordMapPanelElec.tbGdsDevice1.GetString(self.coordMapPanelElec.tbGdsDevice1.GetSelection()),
                    elecCoords[0][0], elecCoords[0][1], elecCoords[0][2]]
            else:
                dev1 = [
                    self.coordMapPanelElec.tbGdsDevice1.GetString(self.coordMapPanelElec.tbGdsDevice1.GetSelection())]
            if elecCoords[1]:
                dev2 = [
                    self.coordMapPanelElec.tbGdsDevice2.GetString(self.coordMapPanelElec.tbGdsDevice2.GetSelection()),
                    elecCoords[1][0], elecCoords[1][1], elecCoords[1][2]]
            else:
                dev2 = [
                    self.coordMapPanelElec.tbGdsDevice2.GetString(self.coordMapPanelElec.tbGdsDevice2.GetSelection())]
            if elecCoords[2]:
                dev3 = [
                    self.coordMapPanelElec.tbGdsDevice3.GetString(self.coordMapPanelElec.tbGdsDevice3.GetSelection()),
                    elecCoords[2][0], elecCoords[2][1], elecCoords[2][2]]
            else:
                dev3 = [
                    self.coordMapPanelElec.tbGdsDevice3.GetString(self.coordMapPanelElec.tbGdsDevice3.GetSelection())]
        else:
            dev1 = [self.coordMapPanelElec.tbGdsDevice1.GetString(self.coordMapPanelElec.tbGdsDevice1.GetSelection())]
            dev2 = [self.coordMapPanelElec.tbGdsDevice2.GetString(self.coordMapPanelElec.tbGdsDevice2.GetSelection())]
            dev3 = [self.coordMapPanelElec.tbGdsDevice3.GetString(self.coordMapPanelElec.tbGdsDevice3.GetSelection())]
        writer.writerow(dev1)
        writer.writerow(dev2)
        writer.writerow(dev3)
        f.close()

    def OnButton_Import(self, event):
        """ Opens a file dialog to select a csv alignment file and populates all position fields"""
        fileDlg = wx.FileDialog(self, "Open", "", "",
                                "Text Files (*.csv)|*.csv",
                                wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        fileDlg.ShowModal()
        filePath = fileDlg.GetPath()
        f = open(filePath, 'r', newline='')
        reader = csv.reader(f)
        textCoordPath = next(reader)
        self.coordFilePath = textCoordPath[0]
        self.parseCoordFile(textCoordPath[0])
        next(reader)
        next(reader)
        optDev1 = next(reader)
        optDev1 = optDev1  # [dev name, x motor coord, y motor coord, z motor coord]
        self.coordMapPanelOpt.tbGdsDevice1.SetString(0, optDev1[0])
        self.coordMapPanelOpt.tbGdsDevice1.SetSelection(0)
        for dev in deviceListAsObjects:
            if optDev1[0] == dev.getDeviceID():
                if dev.getOpticalCoordinates() is not None:
                    self.coordMapPanelOpt.stxGdsCoordLst[0] = dev.getOpticalCoordinates()[0]
                    self.coordMapPanelOpt.styGdsCoordLst[0] = dev.getOpticalCoordinates()[1]
                if dev.getReferenceBondPad() is not None:
                    self.coordMapPanelOpt.elecxGdsCoordLst.append(dev.getReferenceBondPad()[1])
                    self.coordMapPanelOpt.elecyGdsCoordLst.append(dev.getReferenceBondPad()[2])
        if len(optDev1) > 1:
            self.coordMapPanelOpt.tbxMotorCoord1.SetValue(optDev1[1])
            self.coordMapPanelOpt.tbyMotorCoord1.SetValue(optDev1[2])
            self.coordMapPanelOpt.tbzMotorCoord1.SetValue(optDev1[3])
            self.coordMapPanelOpt.stxMotorCoordLst[0] = self.coordMapPanelOpt.tbxMotorCoord1.GetValue()
            self.coordMapPanelOpt.styMotorCoordLst[0] = self.coordMapPanelOpt.tbyMotorCoord1.GetValue()
            self.coordMapPanelOpt.stzMotorCoordLst[0] = self.coordMapPanelOpt.tbzMotorCoord1.GetValue()
        optDev2 = next(reader)
        optDev2 = optDev2
        self.coordMapPanelOpt.tbGdsDevice2.SetString(0, optDev2[0])
        self.coordMapPanelOpt.tbGdsDevice2.SetSelection(0)
        for dev in deviceListAsObjects:
            if optDev2[0] == dev.getDeviceID():
                if dev.getOpticalCoordinates() is not None:
                    self.coordMapPanelOpt.stxGdsCoordLst[1] = dev.getOpticalCoordinates()[0]
                    self.coordMapPanelOpt.styGdsCoordLst[1] = dev.getOpticalCoordinates()[1]
                if dev.getReferenceBondPad() is not None:
                    self.coordMapPanelOpt.elecxGdsCoordLst.append(dev.getReferenceBondPad()[1])
                    self.coordMapPanelOpt.elecyGdsCoordLst.append(dev.getReferenceBondPad()[2])
        if len(optDev2) > 1:
            self.coordMapPanelOpt.tbxMotorCoord2.SetValue(optDev2[1])
            self.coordMapPanelOpt.tbyMotorCoord2.SetValue(optDev2[2])
            self.coordMapPanelOpt.tbzMotorCoord2.SetValue(optDev2[3])
            self.coordMapPanelOpt.stxMotorCoordLst[1] = self.coordMapPanelOpt.tbxMotorCoord2.GetValue()
            self.coordMapPanelOpt.styMotorCoordLst[1] = self.coordMapPanelOpt.tbyMotorCoord2.GetValue()
            self.coordMapPanelOpt.stzMotorCoordLst[1] = self.coordMapPanelOpt.tbzMotorCoord2.GetValue()
        optDev3 = next(reader)
        optDev3 = optDev3
        self.coordMapPanelOpt.tbGdsDevice3.SetString(0, optDev3[0])
        self.coordMapPanelOpt.tbGdsDevice3.SetSelection(0)
        for dev in deviceListAsObjects:
            if optDev3[0] == dev.getDeviceID():
                if dev.getOpticalCoordinates() is not None:
                    self.coordMapPanelOpt.stxGdsCoordLst[2] = dev.getOpticalCoordinates()[0]
                    self.coordMapPanelOpt.styGdsCoordLst[2] = dev.getOpticalCoordinates()[1]
                if dev.getReferenceBondPad() is not None:
                    self.coordMapPanelOpt.elecxGdsCoordLst.append(dev.getReferenceBondPad()[1])
                    self.coordMapPanelOpt.elecyGdsCoordLst.append(dev.getReferenceBondPad()[2])
        if len(optDev3) > 1:
            self.coordMapPanelOpt.tbxMotorCoord3.SetValue(optDev3[1])
            self.coordMapPanelOpt.tbyMotorCoord3.SetValue(optDev3[2])
            self.coordMapPanelOpt.tbzMotorCoord3.SetValue(optDev3[3])
            self.coordMapPanelOpt.stxMotorCoordLst[2] = self.coordMapPanelOpt.tbxMotorCoord3.GetValue()
            self.coordMapPanelOpt.styMotorCoordLst[2] = self.coordMapPanelOpt.tbyMotorCoord3.GetValue()
            self.coordMapPanelOpt.stzMotorCoordLst[2] = self.coordMapPanelOpt.tbzMotorCoord3.GetValue()
        next(reader)
        next(reader)
        elecDev1 = next(reader)
        elecDev1 = elecDev1
        self.coordMapPanelElec.tbGdsDevice1.SetString(0, elecDev1[0])
        self.coordMapPanelElec.tbGdsDevice1.SetSelection(0)
        if len(elecDev1) > 1:
            self.coordMapPanelElec.tbxMotorCoord1.SetValue(elecDev1[1])
            self.coordMapPanelElec.tbyMotorCoord1.SetValue(elecDev1[2])
            self.coordMapPanelElec.tbzMotorCoord1.SetValue(elecDev1[3])
        elecDev2 = next(reader)
        elecDev2 = elecDev2
        self.coordMapPanelElec.tbGdsDevice2.SetString(0, elecDev2[0])
        self.coordMapPanelElec.tbGdsDevice2.SetSelection(0)
        if len(elecDev2) > 1:
            self.coordMapPanelElec.tbxMotorCoord2.SetValue(elecDev2[1])
            self.coordMapPanelElec.tbyMotorCoord2.SetValue(elecDev2[2])
            self.coordMapPanelElec.tbzMotorCoord2.SetValue(elecDev2[3])
        elecDev3 = next(reader)
        elecDev3 = elecDev3
        self.coordMapPanelElec.tbGdsDevice3.SetString(0, elecDev3[0])
        self.coordMapPanelElec.tbGdsDevice3.SetSelection(0)
        if len(elecDev3) > 1:
            self.coordMapPanelElec.tbxMotorCoord3.SetValue(elecDev3[1])
            self.coordMapPanelElec.tbyMotorCoord3.SetValue(elecDev3[2])
            self.coordMapPanelElec.tbzMotorCoord3.SetValue(elecDev3[3])

    def OnButton_ImportTestingParameters(self, event):
        """Imports a testing parameters file and stores data as a dictionary"""

        fileDlg = wx.FileDialog(self, "Open", "", "",
                                "CSV Files (*.csv)|*.csv",
                                wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        fileDlg.ShowModal()
        originalFile = fileDlg.GetPath()

        if originalFile == '':
            print('Please select a file to import')
            return

        self.readCSV(originalFile)
        self.parametersImported = True

    def readCSV(self, originalFile):
        """Reads a csv testing parameters file and stores the information in a dictionary to be used for
        automated measurements."""
        with open(originalFile, 'r') as file:
            rows = []
            for row in file:
                rows.append(row)

            rows.pop(2)
            rows.pop(1)
            rows.pop(0)

            for c in range(len(rows)):
                x = rows[c].split(',')

                self.dataimport['device'].append(x[1])
                self.dataimport['ELECflag'].append(x[2])
                self.dataimport['OPTICflag'].append(x[3])
                self.dataimport['setwflag'].append(x[4])
                self.dataimport['setvflag'].append(x[5])
                self.dataimport['Voltsel'].append(x[6])
                self.dataimport['Currentsel'].append(x[7])
                self.dataimport['VoltMin'].append(x[8])
                self.dataimport['VoltMax'].append(x[9])
                self.dataimport['CurrentMin'].append(x[10])
                self.dataimport['CurrentMax'].append(x[11])
                self.dataimport['VoltRes'].append(x[12])
                self.dataimport['CurrentRes'].append(x[13])
                self.dataimport['IV'].append(x[14])
                self.dataimport['RV'].append(x[15])
                self.dataimport['PV'].append(x[16])
                self.dataimport['ChannelA'].append(x[17])
                self.dataimport['ChannelB'].append(x[18])
                self.dataimport['Start'].append(x[19])
                self.dataimport['Stop'].append(x[20])
                self.dataimport['Stepsize'].append(x[21])
                self.dataimport['Sweeppower'].append(x[22])
                self.dataimport['Sweepspeed'].append(x[23])
                self.dataimport['Laseroutput'].append(x[24])
                self.dataimport['Numscans'].append(x[25])
                self.dataimport['InitialRange'].append(x[26])
                self.dataimport['RangeDec'].append(x[27])
                self.dataimport['setwVoltsel'].append(x[28])
                self.dataimport['setwCurrentsel'].append(x[29])
                self.dataimport['setwVoltMin'].append(x[30])
                self.dataimport['setwVoltMax'].append(x[31])
                self.dataimport['setwCurrentMin'].append(x[32])
                self.dataimport['setwCurrentMax'].append(x[33])
                self.dataimport['setwVoltRes'].append(x[34])
                self.dataimport['setwCurrentRes'].append(x[35])
                self.dataimport['setwIV'].append(x[36])
                self.dataimport['setwRV'].append(x[37])
                self.dataimport['setwPV'].append(x[38])
                self.dataimport['setwChannelA'].append(x[39])
                self.dataimport['setwChannelB'].append(x[40])
                self.dataimport['Wavelengths'].append(x[41])
                self.dataimport['setvStart'].append(x[42])
                self.dataimport['setvStop'].append(x[43])
                self.dataimport['setvStepsize'].append(x[44])
                self.dataimport['setvSweeppower'].append(x[45])
                self.dataimport['setvSweepspeed'].append(x[46])
                self.dataimport['setvLaseroutput'].append(x[47])
                self.dataimport['setvNumscans'].append(x[48])
                self.dataimport['setvInitialRange'].append(x[49])
                self.dataimport['setvRangeDec'].append(x[50])
                self.dataimport['setvChannelA'].append(x[51])
                self.dataimport['setvChannelB'].append(x[52])
                self.dataimport['Voltages'].append(x[53])

        for keys, values in self.dataimport.items():
            pass
            #print(keys)
            #print(values)

    def OnButton_CheckAll(self, event):
        """Selects all items in the devices check list"""
        for ii in range(self.checkList.GetItemCount()):
            self.checkList.CheckItem(ii, True)

    def OnButton_UncheckAll(self, event):
        """Deselects all items in the devices checklist"""
        for ii in range(self.checkList.GetItemCount()):
            self.checkList.CheckItem(ii, False)

    # TODO: Modify to move probe out of the way and keep track of chip stage movement
    def OnButton_GotoDeviceOpt(self, event):
        """Moves laser to selected device"""
        selectedDevice = self.devSelectCb.GetValue()
        global deviceListAsObjects
        for device in deviceListAsObjects:
            if device.getDeviceID == selectedDevice:
                gdsCoord = (device.getOpticalCoordinates[0], device.getOpticalCoordinates[1])
                motorCoord = self.autoMeasure.gdsToMotorCoordsOpt(gdsCoord)
                # Get wedge probe coordinates
                # Calculate laser coordinates
                self.autoMeasure.motorOpt.moveAbsoluteXYZ(motorCoord[0], motorCoord[1], motorCoord[2])

    # TODO: Modify to move laser out of the way
    def OnButton_GotoDeviceElec(self, event):
        """Move probe to selected device"""
        selectedDevice = self.devSelectCb.GetValue()
        global deviceListAsObjects
        for device in deviceListAsObjects:
            if device.getDeviceID == selectedDevice:
                gdsCoord = (device.getReferenceBondPad[1], device.getReferenceBondPad[2])
                motorCoord = self.autoMeasure.gdsToMotorCoordsElec(gdsCoord)
                self.autoMeasure.motorElec.moveAbsoluteXYZ(motorCoord[0], motorCoord[1], motorCoord[2])

    def OnButton_CalculateOpt(self, event):
        """ Computes the optical coordinate transformation matrix. Used to align the laser with the stage.
        Used for debugging."""
        A = self.autoMeasure.findCoordinateTransformOpt(self.coordMapPanelOpt.getMotorCoords(),
                                                        self.coordMapPanelOpt.getGdsCoordsOpt())
        print('Coordinate transform matrix')
        print(A)

    def OnButton_CalculateElec(self, event):
        """ Computes the electrical coordinate transformation matrix. Used to align the wedge probe with the
        stage. Used for debugging."""
        A = self.autoMeasure.findCoordinateTransformElec(self.coordMapPanelElec.getMotorCoords(),
                                                         self.coordMapPanelElec.getGdsCoordsElec())
        print('Coordinate transform matrix')
        print(A)

    def OnButton_SelectOutputFolder(self, event):
        """ Opens a file dialog to select an output directory for automatic measurement results. """
        dirDlg = wx.DirDialog(self, "Open", "", wx.DD_DEFAULT_STYLE)
        dirDlg.ShowModal()
        self.outputFolderTb.SetValue(dirDlg.GetPath())
        dirDlg.Destroy()

    def OnButton_Start(self, event):
        """ Starts an automatic measurement routine. """

        self.autoMeasure.findCoordinateTransformOpt(self.coordMapPanelOpt.getMotorCoords(),
                                                    self.coordMapPanelOpt.getGdsCoordsOpt())

        self.autoMeasure.findCoordinateTransformElec(self.coordMapPanelElec.getMotorCoords(),
                                                     self.coordMapPanelElec.getGdsCoordsElec())

        # Reads parameters from testingParameters tab if no testing parameters file has been uploaded
        if self.parametersImported is False:
            path = os.path.realpath(__file__)
            originalFile = os.path.join(path, 'pyOptomip', 'TestingParameters.csv')
            self.readCSV(originalFile)

        # Disable detector auto measurement
        self.autoMeasure.laser.ctrlPanel.laserPanel.laserPanel.haltDetTimer()
        # self.autoMeasure.laser.laserPanel.laserPanel.haltDetTimer()

        # Make a folder with the current time
        timeStr = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())
        self.autoMeasure.saveFolder = os.path.join(self.outputFolderTb.GetValue(), timeStr)
        if not os.path.exists(self.autoMeasure.saveFolder):
            os.makedirs(self.autoMeasure.saveFolder)

        # Create list of all devices which are selected for measurement from the checklist
        checkedDevicesText = []
        # checkedDevices = []

        for i in range(self.checkList.GetItemCount()):  # self.device_list:
            if self.checkList.IsItemChecked(i):
                checkedDevicesText.append(self.checkList.GetItemText(i))
                # checkedDevices.append(self.checkList.GetItemText(i))

        # Start measurement using the autoMeasure device
        ###MUST HAVE AVAILABLE TESTING INFO FOR SELECTED DEVICE
        self.autoMeasure.beginMeasure(devices=checkedDevicesText, testingParameters=self.dataimport,
                                      checkList=self.checkList,
                                      abortFunction=None, updateFunction=None, updateGraph=True)

        # Copy settings from laser panel
        self.autoMeasure.laser.ctrlPanel.laserPanel.laserPanel.copySweepSettings()
        # Create a measurement progress dialog.
        autoMeasureDlg = autoMeasureProgressDialog(self, title='Automatic measurement')
        autoMeasureDlg.runMeasurement(checkedDevicesText, self.autoMeasure)

        # Enable detector auto measurement
        self.autoMeasure.laser.ctrlPanel.laserPanel.laserPanel.startDetTimer()
