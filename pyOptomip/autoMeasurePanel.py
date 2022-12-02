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
from ElectroOpticDevice import ElectroOpticDevice
import yaml

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
        self.type = type  # "opt" or "elec"
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

        self.tbGdsDevice2 = wx.ComboBox(self, size=(200, 20), choices=[], style=wx.TE_PROCESS_ENTER)
        self.tbGdsDevice2.Bind(wx.EVT_CHOICE, self.on_drop_down2)
        self.tbGdsDevice2.Bind(wx.EVT_TEXT, self.on_drop_down2)
        self.tbGdsDevice2.Bind(wx.EVT_TEXT_ENTER, self.SortDropDowns2)

        self.tbGdsDevice3 = wx.ComboBox(self, size=(200, 20), choices=[], style=wx.TE_PROCESS_ENTER)
        self.tbGdsDevice3.Bind(wx.EVT_CHOICE, self.on_drop_down3)
        self.tbGdsDevice3.Bind(wx.EVT_TEXT, self.on_drop_down3)
        self.tbGdsDevice3.Bind(wx.EVT_TEXT_ENTER, self.SortDropDowns3)

        # List of all drop down menus
        self.GDSDevList = [self.tbGdsDevice1, self.tbGdsDevice2, self.tbGdsDevice3]

        # Get motor coordinates of first device from text box
        stDevice1 = wx.StaticText(self, label='Device %d' % (1))
        self.tbxMotorCoord1 = wx.TextCtrl(self, size=(80, 20), style=wx.TE_READONLY)
        self.tbyMotorCoord1 = wx.TextCtrl(self, size=(80, 20), style=wx.TE_READONLY)
        self.tbzMotorCoord1 = wx.TextCtrl(self, size=(80, 20), style=wx.TE_READONLY)

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
        self.tbxMotorCoord2 = wx.TextCtrl(self, size=(80, 20), style=wx.TE_READONLY)
        self.tbyMotorCoord2 = wx.TextCtrl(self, size=(80, 20), style=wx.TE_READONLY)
        self.tbzMotorCoord2 = wx.TextCtrl(self, size=(80, 20), style=wx.TE_READONLY)

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
        self.tbxMotorCoord3 = wx.TextCtrl(self, size=(80, 20), style=wx.TE_READONLY)
        self.tbyMotorCoord3 = wx.TextCtrl(self, size=(80, 20), style=wx.TE_READONLY)
        self.tbzMotorCoord3 = wx.TextCtrl(self, size=(80, 20), style=wx.TE_READONLY)

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
        if self.type == "opt":
            motorPosition = self.autoMeasure.motorOpt.getPosition()
            xcoord.SetValue(str(motorPosition[0]))
            ycoord.SetValue(str(motorPosition[1]))
            zcoord.SetValue(str(motorPosition[2]))
            self.stxMotorCoordLst[0] = self.tbxMotorCoord1.GetValue()
            self.styMotorCoordLst[0] = self.tbyMotorCoord1.GetValue()
            self.stzMotorCoordLst[0] = self.tbzMotorCoord1.GetValue()
        if self.type == "elec":
            if self.autoMeasure.motorOpt and self.autoMeasure.motorElec:
                optPosition = self.autoMeasure.motorOpt.getPosition()
                elecPosition = self.autoMeasure.motorElec.getPosition()
                relativePosition = []
                relativePosition.append(elecPosition[0] - optPosition[0]*0.82)
                relativePosition.append(elecPosition[1] - optPosition[1]*0.8)
                print("Electrical Motor Position:")
                print(elecPosition)
                relativePosition.append(elecPosition[2])
                xcoord.SetValue(str(relativePosition[0]))
                ycoord.SetValue(str(relativePosition[1]))
                zcoord.SetValue(str(relativePosition[2]))
                self.stxMotorCoordLst[0] = self.tbxMotorCoord1.GetValue()
                self.styMotorCoordLst[0] = self.tbyMotorCoord1.GetValue()
                self.stzMotorCoordLst[0] = self.tbzMotorCoord1.GetValue()
            else:
                motorPosition = self.autoMeasure.motorElec.getPosition()
                xcoord.SetValue(str(motorPosition[0]))
                ycoord.SetValue(str(motorPosition[1]))
                zcoord.SetValue(str(motorPosition[2]))
                self.stxMotorCoordLst[0] = self.tbxMotorCoord1.GetValue()
                self.styMotorCoordLst[0] = self.tbyMotorCoord1.GetValue()
                self.stzMotorCoordLst[0] = self.tbzMotorCoord1.GetValue()

    def Event_OnCoordButton2(self, event, xcoord, ycoord, zcoord):
        """ Called when the button is pressed to get the current motor coordinates, and put it into the text box. """
        if self.type == "opt":
            motorPosition = self.autoMeasure.motorOpt.getPosition()
            xcoord.SetValue(str(motorPosition[0]))
            ycoord.SetValue(str(motorPosition[1]))
            zcoord.SetValue(str(motorPosition[2]))
            self.stxMotorCoordLst[1] = self.tbxMotorCoord2.GetValue()
            self.styMotorCoordLst[1] = self.tbyMotorCoord2.GetValue()
            self.stzMotorCoordLst[1] = self.tbzMotorCoord2.GetValue()
        if self.type == "elec":
            if self.autoMeasure.motorOpt and self.autoMeasure.motorElec:
                optPosition = self.autoMeasure.motorOpt.getPosition()
                elecPosition = self.autoMeasure.motorElec.getPosition()
                print("Electrical Motor Position:")
                print(elecPosition)
                relativePosition = []
                relativePosition.append(elecPosition[0] - optPosition[0]*0.82)
                relativePosition.append(elecPosition[1] - optPosition[1]*0.8)
                relativePosition.append(elecPosition[2])
                xcoord.SetValue(str(relativePosition[0]))
                ycoord.SetValue(str(relativePosition[1]))
                zcoord.SetValue(str(relativePosition[2]))
                self.stxMotorCoordLst[1] = self.tbxMotorCoord2.GetValue()
                self.styMotorCoordLst[1] = self.tbyMotorCoord2.GetValue()
                self.stzMotorCoordLst[1] = self.tbzMotorCoord2.GetValue()
            else:
                motorPosition = self.autoMeasure.motorElec.getPosition()
                xcoord.SetValue(str(motorPosition[0]))
                ycoord.SetValue(str(motorPosition[1]))
                zcoord.SetValue(str(motorPosition[2]))
                self.stxMotorCoordLst[1] = self.tbxMotorCoord2.GetValue()
                self.styMotorCoordLst[1] = self.tbyMotorCoord2.GetValue()
                self.stzMotorCoordLst[1] = self.tbzMotorCoord2.GetValue()

    def Event_OnCoordButton3(self, event, xcoord, ycoord, zcoord):
        """ Called when the button is pressed to get the current motor coordinates, and put it into the text box. """
        if self.type == "opt":
            motorPosition = self.autoMeasure.motorOpt.getPosition()
            xcoord.SetValue(str(motorPosition[0]))
            ycoord.SetValue(str(motorPosition[1]))
            zcoord.SetValue(str(motorPosition[2]))
            self.stxMotorCoordLst[2] = self.tbxMotorCoord3.GetValue()
            self.styMotorCoordLst[2] = self.tbyMotorCoord3.GetValue()
            self.stzMotorCoordLst[2] = self.tbzMotorCoord3.GetValue()
        if self.type == "elec":
            if self.autoMeasure.motorOpt and self.autoMeasure.motorElec:
                optPosition = self.autoMeasure.motorOpt.getPosition()
                elecPosition = self.autoMeasure.motorElec.getPosition()
                print("Electrical Motor Position:")
                print(elecPosition)
                relativePosition = []
                relativePosition.append(elecPosition[0] - optPosition[0]*0.82)
                relativePosition.append(elecPosition[1] - optPosition[1]*0.8)
                relativePosition.append(elecPosition[2])
                xcoord.SetValue(str(relativePosition[0]))
                ycoord.SetValue(str(relativePosition[1]))
                zcoord.SetValue(str(relativePosition[2]))
                self.stxMotorCoordLst[2] = self.tbxMotorCoord3.GetValue()
                self.styMotorCoordLst[2] = self.tbyMotorCoord3.GetValue()
                self.stzMotorCoordLst[2] = self.tbzMotorCoord3.GetValue()
            else:
                motorPosition = self.autoMeasure.motorElec.getPosition()
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
            xval = tcx
            yval = tcy
            zval = tcz
            if xval != '' and yval != '' and zval != '':
                coordsLst.append((float(xval), float(yval), float(zval)))

        return coordsLst

    def getGdsCoordsOpt(self):
        """ Returns a list of the GDS coordinates where the laser is to be aligned for each entered
        device. """
        coordsLst = []
        for tcx, tcy in zip(self.stxGdsCoordLst, self.styGdsCoordLst):
            xval = tcx
            yval = tcy
            if xval != '' and yval != '':
                coordsLst.append((float(xval), float(yval)))
        return coordsLst

    def getGdsCoordsElec(self):
        """ Returns a list of the GDS coordinates of the left-most bond pad for each entered
        device.  """
        coordsLst = []
        for tcx, tcy in zip(self.elecxGdsCoordLst, self.elecyGdsCoordLst):
            xval = tcx
            yval = tcy
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

    def __init__(self, parent, autoMeasure, camera):
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
        self.camera = camera
        # No testing parameters have been uploaded
        self.parametersImported = False
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
        sbUpload = wx.StaticBox(self, label='Save Results')
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

        # Create Detector Selection Box
        sbDetectors = wx.StaticBox(self, label='Choose Detectors')
        vboxDetectors = wx.StaticBoxSizer(sbDetectors, wx.VERTICAL)

        # Add MatPlotLib Panel
        matPlotBox = wx.BoxSizer(wx.HORIZONTAL)
        self.graph = myMatplotlibPanel.myMatplotlibPanel(self)  # use for regular mymatplotlib file
        matPlotBox.Add(self.graph, flag=wx.EXPAND, border=0, proportion=1)

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
        st3 = wx.StaticText(self, label='Align to Device')
        moveLabelBox = wx.BoxSizer(wx.HORIZONTAL)
        moveLabelBox.Add(st3, proportion=1, flag=wx.EXPAND)

        # Add Measurement Buttons
        self.devSelectCb = wx.ComboBox(self, style=wx.CB_READONLY, size=(200, 20))
        self.gotoDevBtn = wx.Button(self, label='Go', size=(70, 20))
        self.gotoDevBtn.Bind(wx.EVT_BUTTON, self.OnButton_GotoDevice)
        goBox = wx.BoxSizer(wx.HORIZONTAL)
        goBox.AddMany([(self.devSelectCb, 1, wx.EXPAND), (self.gotoDevBtn, 0, wx.EXPAND)])

        vboxUpload.AddMany([(saveLabelBox, 0, wx.EXPAND), (saveBox, 0, wx.EXPAND)])

        # Populate Optical Box with alignment and buttons
        vboxOptical.AddMany([(opticalBox, 0, wx.EXPAND)])

        # Populate Electrical Box with alignment and buttons
        vboxElectrical.AddMany([(electricalBox, 0, wx.EXPAND)])

        # Populate Measurement Box with drop down menu and go button
        vboxMeasurement.AddMany(
            [(moveLabelBox, 0, wx.EXPAND), (goBox, 0, wx.EXPAND)])

        topBox = wx.BoxSizer(wx.HORIZONTAL)
        topBox.AddMany([(vboxUpload, 1, wx.EXPAND), (vboxMeasurement, 0, wx.EXPAND)])

        checkBox = wx.BoxSizer(wx.VERTICAL)
        checkBox.AddMany([(checkListBox, 0, wx.EXPAND), (searchListBox, 0, wx.EXPAND), (selectBox, 0, wx.EXPAND),
                          (selectBox2, 0, wx.EXPAND)])

        # Add box to enter minimum wedge probe position in x
        stMinPosition = wx.StaticText(self, label='Minimum Wedge Probe Position in X:')
        hBoxMinElec = wx.BoxSizer(wx.HORIZONTAL)
        self.tbxMotorCoord = wx.TextCtrl(self, size=(80, 20), style=wx.TE_READONLY)
        btnGetMotorCoord = wx.Button(self, label='Get Pos.', size=(50, 20))
        btnGetMotorCoord.Bind(wx.EVT_BUTTON,
                              lambda event, xcoord=self.tbxMotorCoord: self.Event_OnCoordButton(
                                  event, xcoord))
        hBoxMinElec.AddMany([(self.tbxMotorCoord, 1, wx.EXPAND), (btnGetMotorCoord, 1, wx.EXPAND)])
        vBoxMinElec = wx.BoxSizer(wx.VERTICAL)
        vBoxMinElec.AddMany([(stMinPosition, 1, wx.EXPAND), (hBoxMinElec, 1, wx.EXPAND)])

        # Format check boxes for detector selection
        self.sel1 = wx.CheckBox(self, label='Slot 1 Det 1', pos=(20, 20))
        self.sel1.SetValue(False)

        self.sel2 = wx.CheckBox(self, label='Slot 2 Det 1', pos=(20, 20))
        self.sel2.SetValue(False)

        self.sel3 = wx.CheckBox(self, label='Slot 3 Det 1', pos=(20, 20))
        self.sel3.SetValue(False)

        self.sel4 = wx.CheckBox(self, label='Slot 4 Det 1', pos=(20, 20))
        self.sel4.SetValue(False)

        # Populate Detector selection box with check boxes and text
        hboxDetectors = wx.BoxSizer(wx.HORIZONTAL)
        hboxDetectors.AddMany([(self.sel1, 1, wx.EXPAND), (self.sel2, 1, wx.EXPAND), (self.sel3, 1, wx.EXPAND),
                               (self.sel4, 1, wx.EXPAND)])

        vboxDetectors.AddMany([(hboxDetectors, 0, wx.EXPAND)])

        # Add all boxes to outer box
        vboxOuter.AddMany([(topBox, 0, wx.EXPAND), (checkBox, 0, wx.EXPAND), (vboxOptical, 0, wx.EXPAND),
                           (vboxElectrical, 0, wx.EXPAND), (vBoxMinElec, 0, wx.EXPAND), (vboxDetectors, 0, wx.EXPAND)])
        matPlotBox.Add(vboxOuter, flag=wx.LEFT | wx.TOP | wx.ALIGN_LEFT, border=0, proportion=0)

        self.SetSizer(matPlotBox)

    def Event_OnCoordButton(self, event, xcoord):
        """ Called when the button is pressed to get the current motor coordinates, and put it into the text box. """
        elecPosition = self.autoMeasure.motorElec.getPosition()
        xcoord.SetValue(str(elecPosition[0]))
        self.autoMeasure.motorElec.setMinXPosition(elecPosition[0])

    def importObjects(self, listOfDevicesAsObjects):
        """Given a list of electro-optic device objects, this method populates all drop-down menus and
        checklists in the automeasure panel."""
        global deviceListAsObjects
        deviceListAsObjects = listOfDevicesAsObjects
        self.device_list = listOfDevicesAsObjects
        global deviceList
        deviceList = []
        for device in listOfDevicesAsObjects:
            deviceList.append(device.getDeviceID())
        self.devSelectCb.Clear()
        self.devSelectCb.AppendItems(deviceList)
        # Adds items to the checklist
        self.checkList.DeleteAllItems()
        for ii, device in enumerate(deviceList):
            self.checkList.InsertItem(ii, device)
            for dev in listOfDevicesAsObjects:
                if dev.getDeviceID() == device:
                    index = deviceListAsObjects.index(dev)  # Stores index of device in list
                    self.checkList.SetItemData(ii, index)
                    if not dev.hasRoutines():
                        self.checkList.SetItemTextColour(ii, wx.Colour(211, 211, 211))
        self.checkList.EnableCheckBoxes()
        self.coordMapPanelOpt.PopulateDropDowns()
        self.coordMapPanelElec.PopulateDropDowns()

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

    def OnButton_CheckAll(self, event):
        """Selects all items in the devices check list"""
        for ii in range(self.checkList.GetItemCount()):
            self.checkList.CheckItem(ii, True)

    def OnButton_UncheckAll(self, event):
        """Deselects all items in the devices checklist"""
        for ii in range(self.checkList.GetItemCount()):
            self.checkList.CheckItem(ii, False)

    def getActiveDetectors(self):
        activeDetectorLst = list()
        if self.sel1.GetValue() == True:
            activeDetectorLst.append(0)
        if self.sel2.GetValue() == True:
            activeDetectorLst.append(1)
        if self.sel3.GetValue() == True:
            activeDetectorLst.append(2)
        if self.sel4.GetValue() == True:
            activeDetectorLst.append(3)
        return activeDetectorLst

    def OnButton_Save(self, event):
        """Saves the gds devices used for alignment as well as motor positions to a csv file"""
        A = self.autoMeasure.findCoordinateTransformOpt(self.coordMapPanelOpt.getMotorCoords(),
                                                        self.coordMapPanelOpt.getGdsCoordsOpt())

        B = self.autoMeasure.findCoordinateTransformElec(self.coordMapPanelElec.getMotorCoords(),
                                                         self.coordMapPanelElec.getGdsCoordsElec())

        # Make a folder with the current time
        fileName = self.outputFolderTb.GetValue()
        timeStr = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())
        csvFileName = os.path.join(self.outputFolderTb.GetValue(), timeStr + '_{}.csv'.format(fileName))

        f = open(csvFileName, 'w', newline='')
        writer = csv.writer(f)
        textFilePath = [fileName]
        writer.writerow(textFilePath)
        optCoords = self.coordMapPanelOpt.getMotorCoords()
        Opt = ['Optical Alignment']
        writer.writerow(Opt)
        Opt = ['Device', 'Motor x', 'Motor y', 'Motor z']
        writer.writerow(Opt)
        if not all(optCoords):
            dev1 = [self.coordMapPanelOpt.tbGdsDevice1.GetString(self.coordMapPanelOpt.tbGdsDevice1.GetSelection()),
                    optCoords[0][0], optCoords[0][1], optCoords[0][2]]
            dev2 = [self.coordMapPanelOpt.tbGdsDevice2.GetString(self.coordMapPanelOpt.tbGdsDevice2.GetSelection()),
                    optCoords[1][0], optCoords[1][1], optCoords[1][2]]
            dev3 = [self.coordMapPanelOpt.tbGdsDevice3.GetString(self.coordMapPanelOpt.tbGdsDevice3.GetSelection()),
                    optCoords[2][0], optCoords[2][1], optCoords[2][2]]
        else:
            dev1 = [self.coordMapPanelOpt.tbGdsDevice1.GetString(self.coordMapPanelOpt.tbGdsDevice1.GetSelection())]
            dev2 = [self.coordMapPanelOpt.tbGdsDevice2.GetString(self.coordMapPanelOpt.tbGdsDevice2.GetSelection())]
            dev3 = [self.coordMapPanelOpt.tbGdsDevice3.GetString(self.coordMapPanelOpt.tbGdsDevice3.GetSelection())]
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
        self.autoMeasure.parseCoordFile(textCoordPath[0])
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

    def OnButton_ImportTestingParameters(self, event):
        """Imports a testing parameters file and stores data as a dictionary"""

        fileDlg = wx.FileDialog(self, "Open", "", "",
                                "YAML Files (*.yaml)|*.yaml",
                                wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_FILE_MUST_EXIST)
        fileDlg.ShowModal()
        Files = fileDlg.GetPaths()

        if not Files:
            print('Please select a file to import')
            return

        for file in Files:
            self.readYAML(file)
        self.parametersImported = True

    def readYAML(self, originalFile):
        """Reads a yaml testing parameters file and stores the information as a list of electro-optic device
         objects to be used for automated measurements as well as a dictionary of routines."""

        global deviceListAsObjects
        deviceListAsObjects = []

        with open(originalFile, 'r') as file:
            loadedYAML = yaml.safe_load(file)

            for device in loadedYAML['Devices']:
                devExists = False
                device = loadedYAML['Devices'][device]
                if len(deviceListAsObjects) == 0:
                    deviceToTest = ElectroOpticDevice(device['DeviceID'], device['Wavelength'],
                                                      device['Polarization'], device['Optical Coordinates'],
                                                      device['Type'])
                    deviceToTest.addRoutines(device['Routines'])
                    if device['Electrical Coordinates']:
                        for pad in device['Electrical Coordinates']:
                            electricalCoords = []
                            electricalCoords.extend(pad)
                            deviceToTest.addElectricalCoordinates(electricalCoords)
                else:
                    for deviceObj in deviceListAsObjects:
                        if deviceObj.getDeviceID() == device['DeviceID']:
                            deviceToTest = device
                            deviceToTest.addRoutines(device['Routines'])
                            for pad in device['Electrical Coordinates']:
                                electricalCoords = []
                                electricalCoords.extend(pad)
                                deviceToTest.addElectricalCoordinates(electricalCoords)
                            devExists = True
                    if not devExists:
                        deviceToTest = ElectroOpticDevice(device['DeviceID'], device['Wavelength'],
                                                          device['Polarization'], device['Optical Coordinates'],
                                                          device['Type'])
                        deviceToTest.addRoutines(device['Routines'])
                        for pad in device['Electrical Coordinates']:
                            electricalCoords = []
                            electricalCoords.extend(pad)
                            deviceToTest.addElectricalCoordinates(electricalCoords)
                deviceListAsObjects.append(deviceToTest)
                for type in loadedYAML['Routines']:
                    if type == 'Wavelength Sweep':
                        type = loadedYAML['Routines']['Wavelength Sweep']
                        for routine in type:
                            routine = type[routine]
                            self.autoMeasure.addWavelengthSweep(routine, routine['Start'], routine['Stop'],
                                                                routine['Stepsize'], routine['Sweeppower'],
                                                                routine['Sweepspeed'], routine['Laseroutput'],
                                                                routine['Numscans'], routine['Initialrange'],
                                                                routine['RangeDec'])
                    if type == 'Voltage Sweep':
                        type = loadedYAML['Routines']['Voltage Sweep']
                        for routine in type:
                            routine = type[routine]
                            self.autoMeasure.addVoltageSweep(routine, routine['Min'], routine['Max'],
                                                             routine['Res'], routine['IV'], routine['RV'],
                                                             routine['PV'], routine['Channel A'],
                                                             routine['Channel B'])
                    if type == 'Current Sweep':
                        type = loadedYAML['Routines']['Current Sweep']
                        for routine in type:
                            routine = type[routine]
                            self.autoMeasure.addCurrentSweep(routine, routine['Min'], routine['Max'],
                                                             routine['Res'], routine['IV'], routine['RV'],
                                                             routine['PV'], routine['Channel A'],
                                                             routine['Channel B'])
                    if type == 'Set Wavelength Voltage Sweep':
                        type = loadedYAML['Routines']['Set Wavelength Voltage Sweep']
                        for routine in type:
                            routine = type[routine]
                            self.autoMeasure.addSetWavelengthVoltageSweep(routine, routine['Min'], routine['Max'],
                                                                          routine['Res'], routine['IV'], routine['RV'],
                                                                          routine['PV'], routine['Channel A'],
                                                                          routine['Channel B'], routine['Wavelengths'])
                    if type == 'Set Wavelength Current Sweep':
                        type = loadedYAML['Routines']['Set Wavelength Current Sweep']
                        for routine in type:
                            routine = type[routine]
                            self.autoMeasure.addSetWavelengthCurrentSweep(routine, routine['Min'], routine['Max'],
                                                                          routine['Res'], routine['IV'], routine['RV'],
                                                                          routine['PV'], routine['Channel A'],
                                                                          routine['Channel B'], routine['Wavelengths'])
                    if type == 'Set Voltage Wavelength Sweep':
                        type = loadedYAML['Routines']['Set Voltage Wavelength Sweep']
                        for routine in type:
                            routine = type[routine]
                            self.autoMeasure.addSetVoltageWavelengthSweep(routine, routine['Start'], routine['Stop'],
                                                                          routine['Stepsize'], routine['Sweeppower'],
                                                                          routine['Sweepspeed'], routine['Laseroutput'],
                                                                          routine['Numscans'], routine['Initialrange'],
                                                                          routine['RangeDec'], routine['Channel A'],
                                                                          routine['Channel B'], routine['Voltages'])

        self.importObjects(deviceListAsObjects)

    def OnButton_GotoDevice(self, event):
        """
        Move laser and or probe to selected device
        """
        # If laser and probe are connected
        if self.autoMeasure.laser and self.autoMeasure.motorElec:
            # Calculate transform matrices
            self.autoMeasure.findCoordinateTransformOpt(self.coordMapPanelOpt.getMotorCoords(),
                                                        self.coordMapPanelOpt.getGdsCoordsOpt())
            self.autoMeasure.findCoordinateTransformElec(self.coordMapPanelElec.getMotorCoords(),
                                                         self.coordMapPanelElec.getGdsCoordsElec())
            # lift wedge probe
            self.autoMeasure.motorElec.moveRelativeZ(1000)
            time.sleep(2)
            # move wedge probe out of the way
            elecPosition = self.autoMeasure.motorElec.getPosition()
            if elecPosition[0] < self.autoMeasure.motorElec.minXPosition:
                relativex = self.autoMeasure.motorElec.minXPosition - elecPosition[0]
                self.autoMeasure.motorElec.moveRelativeX(-relativex)
                time.sleep(2)
            selectedDevice = self.devSelectCb.GetString(self.devSelectCb.GetSelection())
            # find device object
            for device in self.autoMeasure.devices:
                if device.getDeviceID() == selectedDevice:
                    gdsCoordOpt = (device.getOpticalCoordinates()[0], device.getOpticalCoordinates()[1])
                    motorCoordOpt = self.autoMeasure.gdsToMotorCoordsOpt(gdsCoordOpt)
                    # Move chip stage
                    self.autoMeasure.motorOpt.moveAbsoluteXYZ(motorCoordOpt[0], motorCoordOpt[1], motorCoordOpt[2])
                    # Fine align to device
                    self.autoMeasure.fineAlign.doFineAlign()
                    # Find relative probe position
                    gdsCoordElec = (float(device.getElectricalCoordinates()[0][1]), float(device.getElectricalCoordinates()[0][2]))
                    motorCoordElec = self.autoMeasure.gdsToMotorCoordsElec(gdsCoordElec)
                    optPosition = self.autoMeasure.motorOpt.getPosition()
                    elecPosition = self.autoMeasure.motorElec.getPosition()
                    adjustment = self.autoMeasure.motorOpt.getPositionforRelativeMovement()
                    adjustx = adjustment[0] / 20
                    adjusty = adjustment[1] / 20
                    absolutex = motorCoordElec[0] + optPosition[0]  # - adjustment[0]/20
                    absolutey = motorCoordElec[1] + optPosition[1]  # - adjustment[1]/20
                    absolutez = motorCoordElec[2]
                    relativex = absolutex[0] - elecPosition[0]
                    relativey = absolutey[0] - elecPosition[1]
                    relativez = absolutez[0] - elecPosition[2] + 30
                    if relativex < 0:
                        relativex = relativex
                    if relativey < 0:
                        relativey = relativey
                    if relativex > 0:
                        relativex = relativex
                    if relativey > 0:
                        relativey = relativey
                    # Move probe to device
                    self.autoMeasure.motorElec.moveRelativeX(-relativex)
                    time.sleep(2)
                    self.autoMeasure.motorElec.moveRelativeY(-relativey)
                    time.sleep(2)
                    self.autoMeasure.motorElec.moveRelativeZ(-relativez)
                    # Fine align to device again
                    self.autoMeasure.fineAlign.doFineAlign()

        # if laser is connected but probe isn't
        elif self.autoMeasure.laser and not self.autoMeasure.motorElec:
            # Calculate optical transform matrix
            self.autoMeasure.findCoordinateTransformOpt(self.coordMapPanelOpt.getMotorCoords(),
                                                        self.coordMapPanelOpt.getGdsCoordsOpt())
            selectedDevice = self.devSelectCb.GetString(self.devSelectCb.GetSelection())
            # find device object
            for device in self.autoMeasure.devices:
                if device.getDeviceID() == selectedDevice:
                    gdsCoordOpt = (device.getOpticalCoordinates()[0], device.getOpticalCoordinates()[1])
                    motorCoordOpt = self.autoMeasure.gdsToMotorCoordsOpt(gdsCoordOpt)
                    # Move chip stage
                    self.autoMeasure.motorOpt.moveAbsoluteXYZ(motorCoordOpt[0], motorCoordOpt[1], motorCoordOpt[2])

                    # Fine align to device
                    self.autoMeasure.fineAlign.doFineAlign()

        # if probe is connected but laser isn't
        elif not self.autoMeasure.laser and self.autoMeasure.motorElec:
            self.autoMeasure.findCoordinateTransformElec(self.coordMapPanelElec.getMotorCoords(),
                                                         self.coordMapPanelElec.getGdsCoordsElec())
            selectedDevice = self.devSelectCb.GetString(self.devSelectCb.GetSelection())
            for device in self.autoMeasure.devices:
                if device.getDeviceID() == selectedDevice:
                    gdsCoord = (
                    float(device.getElectricalCoordinates()[0][1]), float(device.getElectricalCoordinates()[0][2]))
                    motorCoord = self.autoMeasure.gdsToMotorCoordsElec(gdsCoord)
                    self.autoMeasure.motorElec.moveRelativeZ(1000)
                    time.sleep(2)
                    if [self.autoMeasure.motorOpt] and [self.autoMeasure.motorElec]:
                        print("moving relative")
                        optPosition = self.autoMeasure.motorOpt.getPosition()
                        elecPosition = self.autoMeasure.motorElec.getPosition()
                        adjustment = self.autoMeasure.motorOpt.getPositionforRelativeMovement()
                        adjustx = adjustment[0] / 20
                        adjusty = adjustment[1] / 20
                        absolutex = motorCoord[0] + optPosition[0]  # - adjustment[0]/20
                        absolutey = motorCoord[1] + optPosition[1]  # - adjustment[1]/20
                        absolutez = motorCoord[2]
                        relativex = absolutex[0] - elecPosition[0]
                        relativey = absolutey[0] - elecPosition[1]
                        relativez = absolutez[0] - elecPosition[2] + 30
                        if relativex < 0:
                            relativex = relativex
                        if relativey < 0:
                            relativey = relativey
                        if relativex > 0:
                            relativex = relativex
                        if relativey > 0:
                            relativey = relativey
                        self.autoMeasure.motorElec.moveRelativeX(-relativex)
                        time.sleep(2)
                        self.autoMeasure.motorElec.moveRelativeY(-relativey)
                        time.sleep(2)
                        self.autoMeasure.motorElec.moveRelativeZ(-relativez)

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

        # Disable detector auto measurement
        self.autoMeasure.laser.ctrlPanel.laserPanel.laserPanel.haltDetTimer()

        # Make a folder with the current time
        timeStr = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())
        self.autoMeasure.saveFolder = os.path.join(self.outputFolderTb.GetValue(), timeStr)
        if not os.path.exists(self.autoMeasure.saveFolder):
            os.makedirs(self.autoMeasure.saveFolder)

        # Create list of all devices which are selected for measurement from the checklist
        checkedDevicesText = []

        for i in range(self.checkList.GetItemCount()):  # self.device_list:
            if self.checkList.IsItemChecked(i):
                for device in self.autoMeasure.devices:
                    if device.getDeviceID() == self.checkList.GetItemText(i):
                        if device.hasRoutines():
                            checkedDevicesText.append(self.checkList.GetItemText(i))

        activeDetectors = self.getActiveDetectors()

        # Start measurement using the autoMeasure device
        self.autoMeasure.beginMeasure(devices=checkedDevicesText, checkList=self.checkList,
                                      activeDetectors=activeDetectors, graph=self.graph,
                                      camera=self.camera, abortFunction=None, updateFunction=None,
                                      updateGraph=True)

        # Create a measurement progress dialog.
        autoMeasureDlg = autoMeasureProgressDialog(self, title='Automatic measurement')
        autoMeasureDlg.runMeasurement(checkedDevicesText, self.autoMeasure)

        # Enable detector auto measurement
        self.autoMeasure.laser.ctrlPanel.laserPanel.laserPanel.startDetTimer()
