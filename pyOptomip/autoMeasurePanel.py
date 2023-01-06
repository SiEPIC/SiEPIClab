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
import math
from autoMeasureProgressDialog import autoMeasureProgressDialog
import os
import time
from filterFrame import filterFrame
import csv
import numpy as np
from ElectroOpticDevice import ElectroOpticDevice
import yaml
from informationframes import infoFrame
from multiprocessing import Process
from threading import Thread
from queue import Queue
import matplotlib.pyplot as plt
from scipy.io import savemat
import os.path
from os import path
global deviceList
global xscalevar
global yscalevar


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
        self.deviceList = []
        self.maxZElecPosition = []
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
        for dev in self.autoMeasure.devices:
            if self.GDSDevList[0].GetString(self.GDSDevList[0].GetSelection()) == dev.getDeviceID():
                if dev.getOpticalCoordinates() is not None:
                    self.stxGdsCoordLst[0] = dev.getOpticalCoordinates()[0]
                    self.styGdsCoordLst[0] = dev.getOpticalCoordinates()[1]
                if dev.getReferenceBondPad() is not None:
                    self.elecxGdsCoordLst.append(dev.getReferenceBondPad()[0])
                    self.elecyGdsCoordLst.append(dev.getReferenceBondPad()[1])

    def on_drop_down2(self, event):
        """Drop down menu for the second device. When a device is selected, its coordinates are added to the
        gds coordinates list and associated motor coordinates are added to the motor coordinates list"""
        for dev in self.autoMeasure.devices:
            if self.GDSDevList[1].GetString(self.GDSDevList[1].GetSelection()) == dev.getDeviceID():
                if dev.getOpticalCoordinates() is not None:
                    self.stxGdsCoordLst[1] = dev.getOpticalCoordinates()[0]
                    self.styGdsCoordLst[1] = dev.getOpticalCoordinates()[1]
                if dev.getReferenceBondPad() is not None:
                    self.elecxGdsCoordLst.append(dev.getReferenceBondPad()[0])
                    self.elecyGdsCoordLst.append(dev.getReferenceBondPad()[1])

    def on_drop_down3(self, event):
        """Drop down menu for the third device. When a device is selected, its coordinates are added to the
        gds coordinates list and associated motor coordinates are added to the motor coordinates list"""
        for dev in self.autoMeasure.devices:
            if self.GDSDevList[2].GetString(self.GDSDevList[2].GetSelection()) == dev.getDeviceID():
                if dev.getOpticalCoordinates() is not None:
                    self.stxGdsCoordLst[2] = dev.getOpticalCoordinates()[0]
                    self.styGdsCoordLst[2] = dev.getOpticalCoordinates()[1]
                if dev.getReferenceBondPad() is not None:
                    self.elecxGdsCoordLst.append(dev.getReferenceBondPad()[0])
                    self.elecyGdsCoordLst.append(dev.getReferenceBondPad()[1])

    def Event_OnCoordButton1(self, event, xcoord, ycoord, zcoord):
        """ Called when the button is pressed to get the current motor coordinates, and put it into the text box. """
        global xscalevar
        global yscalevar
        self.startingstageposition = self.autoMeasure.motorOpt.position
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
                self.saveelecposition1 = [elecPosition[0], elecPosition[1], elecPosition[2]]
                self.saveoptposition1 = [optPosition[0], optPosition[1]]
                relativePosition.append(elecPosition[0] - optPosition[0]*xscalevar)
                relativePosition.append(elecPosition[1] - optPosition[1]*yscalevar)
                relativePosition.append(elecPosition[2])
                if not self.maxZElecPosition:
                    self.maxZElecPosition.append(elecPosition[2])
                    self.setMaxZPositionForMotor(self.maxZElecPosition[0])
                else:
                    self.maxZElecPosition[0] = elecPosition[2]
                    self.setMaxZPositionForMotor(self.maxZElecPosition[0])
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
                if not self.maxZElecPosition:
                    self.maxZElecPosition[0].append(motorPosition[2])
                    self.setMaxZPositionForMotor(self.maxZElecPosition[0])
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
                relativePosition = []
                self.saveelecposition2 = [elecPosition[0], elecPosition[1], elecPosition[2]]
                self.saveoptposition2 = [optPosition[0], optPosition[1]]
                relativePosition.append(elecPosition[0] - optPosition[0]*xscalevar)
                relativePosition.append(elecPosition[1] - optPosition[1]*yscalevar)
                relativePosition.append(elecPosition[2])
                if not self.maxZElecPosition:
                    self.maxZElecPosition.append(elecPosition[2])
                    self.setMaxZPositionForMotor(self.maxZElecPosition[0])
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
                if not self.maxZElecPosition:
                    self.maxZElecPosition.append(motorPosition[2])
                    self.setMaxZPositionForMotor(self.maxZElecPosition[0])
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
                relativePosition = []
                self.saveelecposition3 = [elecPosition[0], elecPosition[1], elecPosition[2]]
                self.saveoptposition3 = [optPosition[0], optPosition[1]]
                relativePosition.append(elecPosition[0] - optPosition[0]*xscalevar)
                relativePosition.append(elecPosition[1] - optPosition[1]*yscalevar)
                relativePosition.append(elecPosition[2])
                if not self.maxZElecPosition:
                    self.maxZElecPosition.append(elecPosition[2])
                    self.setMaxZPositionForMotor(self.maxZElecPosition[0])
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
                if not self.maxZElecPosition:
                    self.maxZElecPosition.append(motorPosition[2])
                    self.setMaxZPositionForMotor(self.maxZElecPosition[0])
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

    def PopulateDropDowns(self, testParametersImported):
        """Populates drop down menu for device selection within the coordinate map panel"""
        if testParametersImported is True:
            self.deviceList = []
        for device in self.autoMeasure.devices:
            self.deviceList.append(device.getDeviceID())
        for GDSDevice in self.GDSDevList:
            GDSDevice.Clear()
            GDSDevice.AppendItems(self.deviceList)

    def SortDropDowns1(self, event):
        """Sort drop downs based on search"""
        GDSDevice = self.GDSDevList[0]

        self.deviceList.sort(key=lambda x: 1 if GDSDevice.GetValue() not in x else 0)
        GDSDevice.Clear()
        GDSDevice.AppendItems(self.deviceList)

    def SortDropDowns2(self, event):
        """Sort drop downs based on search"""
        GDSDevice = self.GDSDevList[1]

        self.deviceList.sort(key=lambda x: 1 if GDSDevice.GetValue() not in x else 0)
        GDSDevice.Clear()
        GDSDevice.AppendItems(self.deviceList)

    def SortDropDowns3(self, event):
        """Sort drop downs based on search"""
        GDSDevice = self.GDSDevList[2]

        self.deviceList.sort(key=lambda x: 1 if GDSDevice.GetValue() not in x else 0)
        GDSDevice.Clear()
        GDSDevice.AppendItems(self.deviceList)

    def setMaxZPositionForMotor(self, maxZ):
        self.autoMeasure.motorElec.setMaxZPosition(maxZ)


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
        self.infoFrame = infoFrame
        ida = True
        pyoptomipfolder = 'C:/Users/SiEPIC_Kaiser/Desktop/Repos/pyOptomip'
        # List of all the names of devices on the chip
        self.device_list = []
        self.camera = camera
        self.calibrationflag = False
        self.part = 0
        global xscalevar
        global yscalevar
        xscalevar = 0.8
        yscalevar = 0.8
        global stopflag
        stopflag = False
        if ida == True:
            ROOT_DIR = 'C:/Users/SiEPIC_Kaiser/Desktop/Repos/pyOptomip/pyOptomip'
        else:
            ROOT_DIR = format(os.getcwd())
        scalefactorcsv = ROOT_DIR + '/ScaleFactor.csv'

        if path.exists(scalefactorcsv):

            f = open(scalefactorcsv, 'r', newline='')
            reader = csv.reader(f)
            xscalevar = float(next(reader)[0])
            yscalevar = float(next(reader)[0])
            self.theta = float(next(reader)[0])
            print('X axis scale adjustment is: ' + str(xscalevar))
            print('Y axis scale adjustment is: ' + str(yscalevar))
            print('Theta is ' + str(self.theta))
            print('Angle of misalignment is: ' + str(self.theta * (180 / math.pi)) + ' degrees')
            self.caldone = True
        else:
            self.theta = 0
            self.caldone = False
        self.testParametersPath = []
        # No testing parameters have been uploaded
        self.parametersImported = False
        self.InitUI()

    def InitUI(self):
        """Sets up the layout for the autoMeasurePanel"""

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
        sbDetectors = wx.StaticBox(self, label='Choose Detectors for Automated Measurements')
        vboxDetectors = wx.StaticBoxSizer(sbDetectors, wx.VERTICAL)

        # Add MatPlotLib Panel
        matPlotBox = wx.BoxSizer(wx.HORIZONTAL)
        self.graph = self.autoMeasure.graphPanel
        matPlotBox.Add(self.graph, flag=wx.EXPAND, border=0, proportion=1)

        # Add Selection Buttons and Filter
        self.checkAllBtn = wx.Button(self, label='Select All', size=(100, 20))
        self.checkAllBtn.Bind(wx.EVT_BUTTON, self.OnButton_CheckAll)
        self.uncheckAllBtn = wx.Button(self, label='Unselect All', size=(100, 20))
        self.uncheckAllBtn.Bind(wx.EVT_BUTTON, self.OnButton_UncheckAll)
        self.filterBtn = wx.Button(self, label='Filter', size=(100, 20))
        self.filterBtn.Bind(wx.EVT_BUTTON, self.OnButton_Filter)
        self.calibrateBtn = wx.Button(self, label='Calibration Mode', size=(100, 20))
        self.calibrateBtn.Bind(wx.EVT_BUTTON, self.OnButton_Calibrate)

        # Add devices checklist
        self.checkList = wx.ListCtrl(self, size = (500, 100),  style=wx.LC_REPORT)
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

        self.startBtn = wx.Button(self, label='Start Measurements', size=(550, 20))
        self.startBtn.Bind(wx.EVT_BUTTON, self.OnButton_Start)
        self.saveBtn = wx.Button(self, label='Save Optical Alignment', size=(200, 20))
        self.saveBtn.Bind(wx.EVT_BUTTON, self.OnButton_Save)
        self.importBtn = wx.Button(self, label='Import Optical Alignment', size=(200, 20))
        self.importBtn.Bind(wx.EVT_BUTTON, self.OnButton_Import)

        self.importBtnCSV = wx.Button(self, label='Import Testing Parameters', size=(200, 20))
        self.importBtnCSV.Bind(wx.EVT_BUTTON, self.OnButton_ImportTestingParameters)

        selectBox = wx.BoxSizer(wx.HORIZONTAL)
        selectBox.AddMany([(self.importBtnCSV, 0, wx.EXPAND), (self.checkAllBtn, 0, wx.EXPAND), (self.uncheckAllBtn, 0, wx.EXPAND),
                           (self.filterBtn, 0, wx.EXPAND), (self.calibrateBtn, 0, wx.EXPAND)])

        alignmentBox = wx.BoxSizer(wx.HORIZONTAL)
        alignmentBox.AddMany([(self.saveBtn, 0, wx.EXPAND), (self.importBtn, 0, wx.EXPAND)])

        startBox = wx.BoxSizer(wx.HORIZONTAL)
        startBox.AddMany([(self.startBtn, 0, wx.EXPAND)])

        scaletext = wx.StaticBox(self, label='Scale Adjust')
        scalehbox = wx.StaticBoxSizer(scaletext, wx.HORIZONTAL)

        #self.setscaleBtn = wx.Button(self, label='Set Scale Adjustment', size=(150, 20))
        #self.setscaleBtn.Bind(wx.EVT_BUTTON, self.changescale)

        self.setscaleBtn = wx.Button(self, label='Calibration Location Set', size=(150, 20))
        self.setscaleBtn.Bind(wx.EVT_BUTTON, self.calibrationroutine)

        self.checkcalBtn = wx.Button(self, label='Check Calibration Status', size=(150, 20))
        self.checkcalBtn.Bind(wx.EVT_BUTTON, self.calibrationcheck)

        #sw1 = wx.StaticText(self, label='X: ')
        #self.xadjust = wx.TextCtrl(self, size=(60, 18))
        #self.xadjust.SetValue('')

        #sw2 = wx.StaticText(self, label='Y: ')
        #self.yadjust = wx.TextCtrl(self, size=(60, 18))
        #self.yadjust.SetValue('')

        #self.scaleinfoBtn = wx.Button(self, id=1, label='?', size=(20, 20))
        #self.scaleinfoBtn.Bind(wx.EVT_BUTTON, self.OnButton_createinfoframe)

        scalehbox.AddMany([(self.setscaleBtn, 0, wx.EXPAND), (self.checkcalBtn, 0, wx.EXPAND)])

        # Add Save folder label
        st2 = wx.StaticText(self, label='Save Folder:')
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
        self.gotoDevBtn = wx.Button(self, label='Go', size=(70, 22))
        self.gotoDevBtn.Bind(wx.EVT_BUTTON, self.OnButton_GotoDevice)
        goBox = wx.BoxSizer(wx.HORIZONTAL)
        goBox.AddMany([(self.devSelectCb, 1, wx.EXPAND), (self.gotoDevBtn, 0, wx.EXPAND)])

        vboxUpload.AddMany([(saveLabelBox, 0, wx.EXPAND), (saveBox, 0, wx.EXPAND)])

        # Populate Optical Box with alignment and buttons
        vboxOptical.AddMany([(opticalBox, 0, wx.EXPAND), (alignmentBox, 0, wx.EXPAND)])

        # Populate Electrical Box with alignment and buttons
        vboxElectrical.AddMany([(electricalBox, 0, wx.EXPAND)])

        # Populate Measurement Box with drop down menu and go button
        vboxMeasurement.AddMany(
            [(moveLabelBox, 0, wx.EXPAND), (goBox, 0, wx.EXPAND)])

        topBox = wx.BoxSizer(wx.HORIZONTAL)
        topBox.AddMany([(vboxUpload, 1, wx.EXPAND), (vboxMeasurement, 0, wx.EXPAND)])

        checkBox = wx.BoxSizer(wx.VERTICAL)
        checkBox.AddMany([(checkListBox, 0, wx.EXPAND), (searchListBox, 0, wx.EXPAND)])

        # Add box to enter minimum wedge probe position in x
        stMinPosition = wx.StaticBox(self, label='Minimum Wedge Probe Position in X:  ')
        hBoxMinElec = wx.StaticBoxSizer(stMinPosition, wx.HORIZONTAL)
        self.tbxMotorCoord = wx.TextCtrl(self, size=(80, 20), style=wx.TE_READONLY)
        btnGetMotorCoord = wx.Button(self, label='Set Position', size=(80, 20))
        btnGetMotorCoord.Bind(wx.EVT_BUTTON,
                              lambda event, xcoord=self.tbxMotorCoord: self.Event_OnCoordButton(
                                  event, xcoord))
        btnUndoMotorCoord = wx.Button(self, label='Undo', size=(80, 20))
        btnUndoMotorCoord.Bind(wx.EVT_BUTTON, self.OnButton_Undo)
        hBoxMinElec.AddMany([(self.tbxMotorCoord, 1, wx.EXPAND), (btnGetMotorCoord, 1, wx.EXPAND), (btnUndoMotorCoord, 1, wx.EXPAND)])

        elecAdjustBox = wx.BoxSizer(wx.HORIZONTAL)
        elecAdjustBox.AddMany([(hBoxMinElec, 0, wx.EXPAND), (scalehbox, 0, wx.EXPAND)])

        hboxDetectors = wx.BoxSizer(wx.HORIZONTAL)

        if self.autoMeasure.laser:
            # Format check boxes for detector selection
            self.numDetectors = self.autoMeasure.laser.numPWMSlots - 1
            self.detectorList = []
            for ii in range(self.numDetectors):
                self.sel = wx.CheckBox(self, label='Slot {} Det 1'.format(ii+1), pos=(20, 20))
                self.sel.SetValue(False)
                self.detectorList.append(self.sel)
                hboxDetectors.AddMany([(self.sel, 1, wx.EXPAND)])

        vboxDetectors.AddMany([(hboxDetectors, 0, wx.EXPAND)])

        # Add all boxes to outer box
        vboxOuter.AddMany([(checkBox, 0, wx.EXPAND), (selectBox, 0, wx.EXPAND),
                           (vboxOptical, 0, wx.EXPAND), (vboxElectrical, 0, wx.EXPAND),
                           (elecAdjustBox, 0, wx.EXPAND), (vboxDetectors, 0, wx.EXPAND), (topBox, 0, wx.EXPAND),
                           (startBox, 0, wx.EXPAND)])
        matPlotBox.Add(vboxOuter, flag=wx.LEFT | wx.TOP | wx.ALIGN_LEFT, border=0, proportion=0)

        self.SetSizer(matPlotBox)

    def calibrationcheck(self, event):
        if self.caldone == True:
            print('Calibration settings are as follows:')
            print('X axis scale adjustment is: ' + str(xscalevar))
            print('Y axis scale adjustment is: ' + str(yscalevar))
            print('Theta is ' + str(self.theta))
            print('Angle of misalignment is: ' + str(self.theta * (180 / math.pi)) + ' degrees')
        else:
            print('Calibration has not been performed,\n please complete calibration routine before commencing automated measurements')

    def calibrationroutine(self, event):

        if self.part == 0:
            self.OnButton_GotoDevice(0)
            #self.autoMeasure.motorElec.moveRelativeZ(300)
            self.autoMeasure.motorOpt.moveRelative(-1000, 0, 0)
            self.OnButton_GotoDevice(0)
        if self.part == 1:
            self.autoMeasure.motorElec.moveRelativeZ(300)
            self.autoMeasure.motorOpt.moveRelative(1000, 0, 0)
            xside = self.autoMeasure.motorElec.xbank
            yside = self.autoMeasure.motorElec.ybank
            if yside == 0:
                yside = 0.00000001
            self.theta = math.atan(xside/yside)
            self.theta = (math.pi/2) - self.theta
            print('The misalignment angle is ' + str(self.theta))
            self.caldone = True

            ROOT_DIR = format(os.getcwd())
            scalefactorcsv = ROOT_DIR + '\ScaleFactor.csv'

            f = open(scalefactorcsv, 'w', newline='')
            writer = csv.writer(f)
            textType = [str(xscalevar)]
            writer.writerow(textType)
            writer = csv.writer(f)
            textType = [str(yscalevar)]
            writer.writerow(textType)
            textType = [str(self.theta)]
            writer.writerow(textType)

        if self.part == 2:
            print('Calibration Complete, click the calibration button to exit calibration mode')
            return

        self.part = self.part + 1

    def changescale(self, event):
        global xscalevar
        global yscalevar

        self.inputcheck('automeasure')
        if self.inputcheckflag == False:
            return

        xscalevar = float(self.xadjust.GetValue())
        yscalevar = float(self.yadjust.GetValue())

        if xscalevar >= 1.5 or yscalevar >= 1.5 or xscalevar <= 0.6 or yscalevar <= 0.6:
            xscalevar = 0.82
            yscalevar = 0.8
            print("Cannot scale by that amount, please choose scaling factors between 0.6 and 1.5")
            return

        print('Set X scaling factor to ' + str(xscalevar))
        print('Set Y scaling factor to ' + str(yscalevar))

        relativePosition = []

        if self.coordMapPanelElec.tbxMotorCoord1.GetValue():
            relativePosition.append(self.coordMapPanelElec.saveelecposition1[0] - self.coordMapPanelElec.saveoptposition1[0] * xscalevar)
            relativePosition.append(self.coordMapPanelElec.saveelecposition1[1] - self.coordMapPanelElec.saveoptposition1[1] * yscalevar)
            relativePosition.append(self.coordMapPanelElec.saveelecposition1[2])
            self.coordMapPanelElec.tbxMotorCoord1.SetValue(str(relativePosition[0]))
            self.coordMapPanelElec.tbyMotorCoord1.SetValue(str(relativePosition[1]))
            self.coordMapPanelElec.tbzMotorCoord1.SetValue(str(relativePosition[2]))
            self.coordMapPanelElec.stxMotorCoordLst[0] = self.coordMapPanelElec.tbxMotorCoord1.GetValue()
            self.coordMapPanelElec.styMotorCoordLst[0] = self.coordMapPanelElec.tbyMotorCoord1.GetValue()
            self.coordMapPanelElec.stzMotorCoordLst[0] = self.coordMapPanelElec.tbzMotorCoord1.GetValue()

        relativePosition = []

        if self.coordMapPanelElec.tbxMotorCoord2.GetValue():
            relativePosition.append(self.coordMapPanelElec.saveelecposition2[0] - self.coordMapPanelElec.saveoptposition2[0] * xscalevar)
            relativePosition.append(self.coordMapPanelElec.saveelecposition2[1] - self.coordMapPanelElec.saveoptposition2[1] * yscalevar)
            relativePosition.append(self.coordMapPanelElec.saveelecposition2[2])
            self.coordMapPanelElec.tbxMotorCoord2.SetValue(str(relativePosition[0]))
            self.coordMapPanelElec.tbyMotorCoord2.SetValue(str(relativePosition[1]))
            self.coordMapPanelElec.tbzMotorCoord2.SetValue(str(relativePosition[2]))
            self.coordMapPanelElec.stxMotorCoordLst[1] = self.coordMapPanelElec.tbxMotorCoord2.GetValue()
            self.coordMapPanelElec.styMotorCoordLst[1] = self.coordMapPanelElec.tbyMotorCoord2.GetValue()
            self.coordMapPanelElec.stzMotorCoordLst[1] = self.coordMapPanelElec.tbzMotorCoord2.GetValue()

        relativePosition = []

        if self.coordMapPanelElec.tbxMotorCoord3.GetValue():
            relativePosition.append(self.coordMapPanelElec.saveelecposition3[0] - self.coordMapPanelElec.saveoptposition3[0] * xscalevar)
            relativePosition.append(self.coordMapPanelElec.saveelecposition3[1] - self.coordMapPanelElec.saveoptposition3[1] * yscalevar)
            relativePosition.append(self.coordMapPanelElec.saveelecposition3[2])
            self.coordMapPanelElec.tbxMotorCoord3.SetValue(str(relativePosition[0]))
            self.coordMapPanelElec.tbyMotorCoord3.SetValue(str(relativePosition[1]))
            self.coordMapPanelElec.tbzMotorCoord3.SetValue(str(relativePosition[2]))
            self.coordMapPanelElec.stxMotorCoordLst[2] = self.coordMapPanelElec.tbxMotorCoord3.GetValue()
            self.coordMapPanelElec.styMotorCoordLst[2] = self.coordMapPanelElec.tbyMotorCoord3.GetValue()
            self.coordMapPanelElec.stzMotorCoordLst[2] = self.coordMapPanelElec.tbzMotorCoord3.GetValue()

        ROOT_DIR = format(os.getcwd())
        scalefactorcsv = ROOT_DIR + '\ScaleFactor.csv'


        f = open(scalefactorcsv, 'w', newline='')
        writer = csv.writer(f)
        textType = [str(xscalevar)]
        writer.writerow(textType)
        writer = csv.writer(f)
        textType = [str(yscalevar)]
        writer.writerow(textType)

    def Event_OnCoordButton(self, event, xcoord):
        """ Called when the button is pressed to get the current motor coordinates, and put it into the text box. """
        elecPosition = self.autoMeasure.motorElec.getPosition()
        xcoord.SetValue(str(elecPosition[0]))
        self.autoMeasure.motorElec.setMinXPosition(elecPosition[0])
        self.autoMeasure.motorElec.minPositionSet = True

    def OnButton_Undo(self, event):
        self.autoMeasure.motorElec.minPositionSet = False
        self.tbxMotorCoord.SetValue('')

    def importObjects(self, listOfDevicesAsObjects):
        """Given a list of electro-optic device objects, this method populates all drop-down menus and
        checklists in the automeasure panel."""
        deviceList = []
        for device in listOfDevicesAsObjects:
            deviceList.append(device.getDeviceID())
            self.autoMeasure.devices.append(device)
        self.devSelectCb.Clear()
        self.devSelectCb.AppendItems(deviceList)
        # Adds items to the checklist
        self.checkList.DeleteAllItems()
        for ii, device in enumerate(deviceList):
            self.checkList.InsertItem(ii, device)
            for dev in listOfDevicesAsObjects:
                if dev.getDeviceID() == device:
                    if not dev.hasRoutines():
                        self.checkList.SetItemTextColour(ii, wx.Colour(211, 211, 211))
        self.checkList.EnableCheckBoxes()
        self.coordMapPanelOpt.PopulateDropDowns(self.parametersImported)
        self.coordMapPanelElec.PopulateDropDowns(self.parametersImported)

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

    def OnButton_Calibrate(self, event):
        if self.calibrationflag == True:
            self.calibrationflag = False
            print('Exiting Calibration Mode')
            self.autoMeasure.motorElec.calflag = False
        elif self.calibrationflag == False:
            self.caldone = False
            self.calibrationflag = True
            self.autoMeasure.motorElec.calflag = True
            print("Entered Calibration Mode")
            self.autoMeasure.motorElec.ybank = 0
            self.autoMeasure.motorElec.xbank = 0
            self.part = 0
            self.calibrationroutine(0)

    def OnButton_SearchChecklist(self, event):
        """Moves devices with searched term present in ID to the top of the checklist. Have to double click
        magnifying glass for search to proceed."""
        term = self.search.GetStringSelection()

        def checkListSort(item1, item2):
            """Used for sorting the checklist of devices on the chip"""
            # Items are the client data associated with each entry
            if term in self.autoMeasure.devices[item2].getDeviceID() and term not in self.autoMeasure.devices[
                item1].getDeviceID():
                return 1
            elif term in self.autoMeasure.devices[item1].getDeviceID() and term not in self.autoMeasure.devices[
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
        for ii in range(self.numDetectors):
            if self.detectorList[ii].GetValue() == True:
                activeDetectorLst.append(ii)
        return activeDetectorLst

    def OnButton_Save(self, event):
        """Saves the gds devices used for alignment as well as motor positions to a csv file"""

        if self.outputFolderTb.GetValue() == '':
           print("Please Select Location to Save Alignment File.")

        else:
            A = self.autoMeasure.findCoordinateTransformOpt(self.coordMapPanelOpt.getMotorCoords(),
                                                            self.coordMapPanelOpt.getGdsCoordsOpt())

            # Make a folder with the current time
            timeStr = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())
            csvFileName = os.path.join(self.outputFolderTb.GetValue(), 'Optical Alignment' + timeStr + '.csv')

            f = open(csvFileName, 'w', newline='')
            writer = csv.writer(f)
            textFilePath = self.testParametersPath
            writer.writerow(textFilePath)
            optCoords = self.coordMapPanelOpt.getMotorCoords()
            Opt = ['Optical Alignment']
            writer.writerow(Opt)
            Opt = ['Device', 'Motor x', 'Motor y', 'Motor z']
            writer.writerow(Opt)
            if not all(item == 0 for item in optCoords):
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
            print('Saved Optical Alignment data to ' + csvFileName)

    def OnButton_Import(self, event):
        """ Opens a file dialog to select a csv alignment file and populates all position fields"""
        try:
            fileDlg = wx.FileDialog(self, "Open", "", "",
                                "Text Files (*.csv)|*.csv",
                                wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            fileDlg.ShowModal()
            filePath = fileDlg.GetPath()
            f = open(filePath, 'r', newline='')
        except:
            return
        reader = csv.reader(f)
        textCoordPath = next(reader)
        for path in textCoordPath:
            if path != "," and path != "":
                self.readYAML(path)
        next(reader)
        next(reader)
        optDev1 = next(reader)
        optDev1 = optDev1  # [dev name, x motor coord, y motor coord, z motor coord]
        self.coordMapPanelOpt.tbGdsDevice1.SetString(0, optDev1[0])
        self.coordMapPanelOpt.tbGdsDevice1.SetSelection(0)
        for dev in self.autoMeasure.devices:
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
        for dev in self.autoMeasure.devices:
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
        for dev in self.autoMeasure.devices:
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
        try:
            fileDlg = wx.FileDialog(self, "Open", "", "",
                                "YAML Files (*.yaml)|*.yaml",
                                wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_FILE_MUST_EXIST)
            fileDlg.ShowModal()
            Files = fileDlg.GetPaths()
        except:
            return

        if not Files:
            print('Please select a file to import')
            return

        for file in Files:
            self.readYAML(file)
            self.testParametersPath.append(file)
        self.parametersImported = True

    def readYAML(self, originalFile):
        """Reads a yaml testing parameters file and stores the information as a list of electro-optic device
         objects to be used for automated measurements as well as a dictionary of routines."""
        if self.parametersImported:
            self.autoMeasure.devices = []
        deviceList = []
        with open(originalFile, 'r') as file:
            loadedYAML = yaml.safe_load(file)

            for device in loadedYAML['Devices']:
                devExists = False
                device = loadedYAML['Devices'][device]
                if len(self.autoMeasure.devices) == 0:
                    deviceToTest = ElectroOpticDevice(device['DeviceID'], device['Wavelength'],
                                                      device['Polarization'], device['Optical Coordinates'],
                                                      device['Type'])
                    deviceToTest.addRoutines(device['Routines'])
                    if device['Electrical Coordinates']:
                            deviceToTest.addElectricalCoordinates(device['Electrical Coordinates'])
                else:
                    for deviceObj in self.autoMeasure.devices:
                        if deviceObj.getDeviceID() == device['DeviceID']:
                            deviceToTest = deviceObj
                            deviceToTest.addRoutines(device['Routines'])
                            deviceToTest.addElectricalCoordinates(device['Electrical Coordinates'])
                            devExists = True
                    if not devExists:
                        deviceToTest = ElectroOpticDevice(device['DeviceID'], device['Wavelength'],
                                                          device['Polarization'], device['Optical Coordinates'],
                                                          device['Type'])
                        deviceToTest.addRoutines(device['Routines'])
                        deviceToTest.addElectricalCoordinates(device['Electrical Coordinates'])
                deviceList.append(deviceToTest)
            for type in loadedYAML['Routines']:
                if type == 'Wavelength Sweep':
                    wavsweep = loadedYAML['Routines']['Wavelength Sweep']
                    for routine in wavsweep:
                        dict = wavsweep[routine]
                        self.autoMeasure.addWavelengthSweep(routine, dict['Start'], dict['Stop'],
                                                            dict['Stepsize'], dict['Sweeppower'],
                                                            dict['Sweepspeed'], dict['Laseroutput'],
                                                            dict['Numscans'], dict['Initialrange'],
                                                            dict['RangeDec'])
                elif type == 'Voltage Sweep':
                    voltsweep = loadedYAML['Routines']['Voltage Sweep']
                    for routine in voltsweep:
                        dict = voltsweep[routine]
                        self.autoMeasure.addVoltageSweep(routine, dict['Min'], dict['Max'],
                                                            dict['Res'], dict['IV'], dict['RV'],
                                                            dict['PV'], dict['Channel A'],
                                                            dict['Channel B'])
                elif type == 'Current Sweep':
                    currsweep = loadedYAML['Routines']['Current Sweep']
                    for routine in currsweep:
                        dict = currsweep[routine]
                        self.autoMeasure.addCurrentSweep(routine, dict['Min'], dict['Max'],
                                                            dict['Res'], dict['IV'], dict['RV'],
                                                            dict['PV'], dict['Channel A'],
                                                            dict['Channel B'])
                elif type == 'Set Wavelength Voltage Sweep':
                    setwvsweep = loadedYAML['Routines']['Set Wavelength Voltage Sweep']
                    for routine in setwvsweep:
                        dict = setwvsweep[routine]
                        self.autoMeasure.addSetWavelengthVoltageSweep(routine, dict['Min'], dict['Max'],
                                                                        dict['Res'], dict['IV'], dict['RV'],
                                                                        dict['PV'], dict['Channel A'],
                                                                        dict['Channel B'], dict['Wavelengths'])
                elif type == 'Set Wavelength Current Sweep':
                    setwcsweep = loadedYAML['Routines']['Set Wavelength Current Sweep']
                    for routine in setwcsweep:
                        dict = setwcsweep[routine]
                        self.autoMeasure.addSetWavelengthCurrentSweep(routine, dict['Min'], dict['Max'],
                                                                        dict['Res'], dict['IV'], dict['RV'],
                                                                        dict['PV'], dict['Channel A'],
                                                                        dict['Channel B'], dict['Wavelengths'])
                elif type == 'Set Voltage Wavelength Sweep':
                    setvwavsweep = loadedYAML['Routines']['Set Voltage Wavelength Sweep']
                    for routine in setvwavsweep:
                        dict = setvwavsweep[routine]
                        self.autoMeasure.addSetVoltageWavelengthSweep(routine, dict['Start'], dict['Stop'],
                                                                        dict['Stepsize'], dict['Sweeppower'],
                                                                        dict['Sweepspeed'], dict['Laseroutput'],
                                                                        dict['Numscans'], dict['Initialrange'],
                                                                        dict['RangeDec'], dict['Channel A'],
                                                                        dict['Channel B'], dict['Voltages'])

        self.importObjects(deviceList)

    def adjustalignment(self):

        if self.caldone == True:
            xdistance = self.autoMeasure.motorOpt.position[0] - self.coordMapPanelElec.startingstageposition[0]
            ydistance = self.autoMeasure.motorOpt.position[1] - self.coordMapPanelElec.startingstageposition[1]

            xadjustmentx = xdistance * math.cos(self.theta)
            yadjustmentx = xdistance * math.sin(self.theta)

            yadjustmenty = ydistance * math.cos(self.theta)
            xadjustmenty = ydistance * math.sin(self.theta)


            if xadjustmentx == 0:
                self.autoMeasure.motorElec.moveRelativeX(xadjustmentx)
                time.sleep(2)
            if yadjustmentx == 0:
                self.autoMeasure.motorElec.moveRelativeY(yadjustmentx)
                time.sleep(2)
            if xadjustmenty == 0:
                self.autoMeasure.motorElec.moveRelativeX(xadjustmenty)
                time.sleep(2)
            if yadjustmenty == 0:
                self.autoMeasure.motorElec.moveRelativeY(yadjustmenty)

    def OnButton_GotoDevice(self, event):
        """
        Move laser and or probe to selected device
        """
        # If laser and probe are connected
        global xscalevar
        global yscalevar
        if self.calibrationflag == False:
            if self.devSelectCb.GetString(self.devSelectCb.GetSelection()) == '':
                print("Please select a device to move to")
                return
        print('Moving to device')
        if self.autoMeasure.laser and self.autoMeasure.motorElec and self.calibrationflag == False:
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
                    gdsCoordElec = (float(device.getElectricalCoordinates()[0][0]), float(device.getElectricalCoordinates()[0][1]))
                    motorCoordElec = self.autoMeasure.gdsToMotorCoordsElec(gdsCoordElec)
                    optPosition = self.autoMeasure.motorOpt.getPosition()
                    elecPosition = self.autoMeasure.motorElec.getPosition()
                    adjustment = self.autoMeasure.motorOpt.getPositionforRelativeMovement()
                    absolutex = motorCoordElec[0] + optPosition[0]*xscalevar
                    absolutey = motorCoordElec[1] + optPosition[1]*yscalevar
                    absolutez = motorCoordElec[2]
                    relativex = absolutex[0] - elecPosition[0]
                    relativey = absolutey[0] - elecPosition[1]
                    relativez = absolutez[0] - elecPosition[2] + 15
                    # Move probe to device
                    self.autoMeasure.motorElec.moveRelativeX(-relativex)
                    time.sleep(2)
                    self.autoMeasure.motorElec.moveRelativeY(-relativey)
                    time.sleep(2)
                    self.adjustalignment()
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
        elif (not self.autoMeasure.laser and self.autoMeasure.motorElec) or (self.autoMeasure.motorElec and self.calibrationflag):
            self.autoMeasure.findCoordinateTransformElec(self.coordMapPanelElec.getMotorCoords(),
                                                         self.coordMapPanelElec.getGdsCoordsElec())
            if self.calibrationflag:
                selectedDevice = self.coordMapPanelElec.GDSDevList[0].GetString(self.coordMapPanelElec.GDSDevList[0].GetSelection())
            else:
                selectedDevice = self.devSelectCb.GetString(self.devSelectCb.GetSelection())
            for device in self.autoMeasure.devices:
                if device.getDeviceID() == selectedDevice:
                    gdsCoord = (
                    float(device.getElectricalCoordinates()[0][0]), float(device.getElectricalCoordinates()[0][1]))
                    motorCoord = self.autoMeasure.gdsToMotorCoordsElec(gdsCoord)
                    self.autoMeasure.motorElec.moveRelativeZ(1000)
                    time.sleep(2)
                    if [self.autoMeasure.motorOpt] and [self.autoMeasure.motorElec]:
                        optPosition = self.autoMeasure.motorOpt.getPosition()
                        elecPosition = self.autoMeasure.motorElec.getPosition()
                        adjustment = self.autoMeasure.motorOpt.getPositionforRelativeMovement()
                        absolutex = motorCoord[0] + optPosition[0]*xscalevar
                        absolutey = motorCoord[1] + optPosition[1]*yscalevar
                        absolutez = motorCoord[2]
                        relativex = absolutex[0] - elecPosition[0]
                        relativey = absolutey[0] - elecPosition[1]
                        relativez = absolutez[0] - elecPosition[2] + 15
                        self.autoMeasure.motorElec.moveRelativeX(-relativex)
                        time.sleep(2)
                        self.autoMeasure.motorElec.moveRelativeY(-relativey)
                        time.sleep(2)
                        self.adjustalignment()
                        time.sleep(2)
                        if self.calibrationflag:
                            self.autoMeasure.motorElec.moveRelativeZ(-relativez + 300)
                        else:
                            self.autoMeasure.motorElec.moveRelativeZ(-relativez)
        self.autoMeasure.graphPanel.canvas.draw()

    def OnButton_SelectOutputFolder(self, event):
        """ Opens a file dialog to select an output directory for automatic measurement results. """
        dirDlg = wx.DirDialog(self, "Open", "", wx.DD_DEFAULT_STYLE)
        dirDlg.ShowModal()
        self.outputFolderTb.SetValue(dirDlg.GetPath())
        dirDlg.Destroy()

    def OnButton_Start(self, event):
        """ Starts an automatic measurement routine. """
        global xscalevar
        global yscalevar

        if self.outputFolderTb.GetValue() == "":
            print("Please Choose Location to Save Measurement Results.")
        else:
            optDevSet = set()
            self.noOptMatrix = False
            for devName in self.coordMapPanelOpt.GDSDevList:
                optDevSet.add(devName)
            if len(optDevSet) < len(self.coordMapPanelOpt.GDSDevList):
                print("Please Use Three Different Devices for the Optical Matrix.")
                self.noOptMatrix = True
            else:
                self.autoMeasure.findCoordinateTransformOpt(self.coordMapPanelOpt.getMotorCoords(),
                                                        self.coordMapPanelOpt.getGdsCoordsOpt())
            self.noElecMatrix = False
            if self.autoMeasure.motorElec and self.autoMeasure.smu:
                elecDevSet = set()
                for devName in self.coordMapPanelElec.GDSDevList:
                    elecDevSet.add(devName)
                if len(elecDevSet) < len(self.coordMapPanelElec.GDSDevList):
                    print("Please Use Three Different Devices for the Electrical Matrix.")
                    self.noElecMatrix = True
                else:
                    self.autoMeasure.findCoordinateTransformElec(self.coordMapPanelElec.getMotorCoords(),
                                                        self.coordMapPanelElec.getGdsCoordsElec())
                    if self.autoMeasure.matrixissueflag == True:
                        return


                if self.noElecMatrix is True or self.noOptMatrix is True:
                    pass
                else:
                    # Disable detector auto measurement
                    if self.autoMeasure.laser:
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

                    # Set scaling factor within automeasure

                    self.autoMeasure.setScale(xscalevar, yscalevar)

                    if not activeDetectors:
                        print("Please Select a Detector.")

                    elif not checkedDevicesText:
                        print("Please Select Devices to Measure.")

                    else:
                        q = Queue()
                        data = []
                        self.autoMeasure.smu.automeasureflag = False
                        p = Thread(target=self.autoMeasure.beginMeasure, args=(
                        checkedDevicesText, self.checkList, activeDetectors, self.camera, data, None, None, True))
                        p.daemon = True
                        p.start()

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

    def inputcheck(self, setting):


        self.inputcheckflag = True

        if setting == 'automeasure':

            if self.xadjust.GetValue().replace('.', '').isnumeric() == False or self.yadjust.GetValue().replace('.', '').isnumeric() == False:
                self.inputcheckflag = False
                print('Please check scale values')

        if setting == 'sweep':

            if self.xadjust.GetValue().replace('.', '').isnumeric() == False or self.yadjust.GetValue().replace('.', '').isnumeric() == False:
                self.inputcheckflag = False
                print('Please check scale values')

    def drawGraph(self, x, y, graphPanel, xlabel, ylabel, legendstring, legend=0):
        self.autoMeasure.graphPanel.axes.cla()
        self.autoMeasure.graphPanel.axes.plot(x, y)
        if legend != 0:
            self.autoMeasure.graphPanel.axes.legend(legendstring)
        self.autoMeasure.graphPanel.axes.ticklabel_format(useOffset=False)
        self.autoMeasure.graphPanel.axes.set_xlabel(xlabel)
        self.autoMeasure.graphPanel.axes.set_ylabel(ylabel)
        self.autoMeasure.graphPanel.canvas.draw()

    def save_pdf(self, deviceObject, x, y, xarr, yarr, saveFolder, routineName, legend, legendstring):
        # Create pdf file
        path = saveFolder
        d1 = deviceObject.getDeviceID().replace(":", "")
        pdfFileName = os.path.join(path, saveFolder + "\\" + routineName + ".pdf")
        plt.figure()
        plt.plot(xarr, yarr)
        plt.xlabel(x)
        plt.ylabel(y)
        if legend != 0:
            plt.legend(legendstring)
        plt.savefig(pdfFileName)
        plt.close()

    def save_mat(self, deviceObject, devNum, motorCoordOpt, xArray, yArray, x, y, saveFolder, routineName):
        path = saveFolder
        d1 = deviceObject.getDeviceID().replace(":", "")
        matFileName = os.path.join(path, saveFolder + "\\" + routineName + ".mat")

        # Save sweep data and metadata to the mat file
        matDict = dict()
        matDict['scandata'] = dict()
        matDict['metadata'] = dict()
        matDict['scandata'][x] = xArray
        matDict['scandata'][y] = yArray
        matDict['metadata']['device'] = deviceObject.getDeviceID()
        matDict['metadata']['gds_x_coord'] = deviceObject.getOpticalCoordinates()[0]
        matDict['metadata']['gds_y_coord'] = deviceObject.getOpticalCoordinates()[1]
        matDict['metadata']['motor_x_coord'] = motorCoordOpt[0]
        matDict['metadata']['motor_y_coord'] = motorCoordOpt[1]
        matDict['metadata']['motor_z_coord'] = motorCoordOpt[2]
        matDict['metadata']['measured_device_number'] = devNum
        timeSeconds = time.time()
        matDict['metadata']['time_seconds'] = timeSeconds
        matDict['metadata']['time_str'] = time.ctime(timeSeconds)
        savemat(matFileName, matDict)

    def save_csv(self, deviceObject, testType, xArray, yArray, start, stop, chipStart, motorCoords, devNum, saveFolder, routineName, xlabel, ylabel):

        path = saveFolder
        d1 = deviceObject.getDeviceID().replace(":", "")
        csvFileName = os.path.join(path, saveFolder + "\\" + routineName + ".csv")
        f = open(csvFileName, 'w', newline='')
        writer = csv.writer(f)
        textType = ["#Test:" + testType]
        writer.writerow(textType)
        user = ["#User:"]
        writer.writerow(user)
        start = ["#Start:" + start]
        writer.writerow(start)
        stop = ["#Stop:" + stop]
        writer.writerow(stop)
        devID = ["#Device ID:" + deviceObject.getDeviceID()]
        writer.writerow(devID)
        gds = ["#Device coordinates (gds):" + '(' + str(deviceObject.getOpticalCoordinates()[0]) + ', ' + str(deviceObject.getOpticalCoordinates()[1]) + ')']
        writer.writerow(gds)
        motor = ["#Device coordinates (motor):" + '(' + str(motorCoords[0]) + ', ' + str(motorCoords[1]) + ', ' + str(motorCoords[2]) + ')']
        writer.writerow(motor)
        chipStart = ["#Chip test start:" + str(chipStart)]
        writer.writerow(chipStart)
        settings = ["#Settings:"]
        writer.writerow(settings)
        laser = ["#Laser:" + self.autoMeasure.laser.getName()]
        writer.writerow(laser)
        detector = ["#Detector:" + self.autoMeasure.laser.getDetector()]
        writer.writerow(detector)
        if testType == 'Wavelength sweep':
            wavsweep = self.autoMeasure.wavelengthSweeps
            speed = ["#Sweep speed:" + wavsweep['Sweepspeed'][devNum]]
            writer.writerow(speed)
            numData = ["#Number of datasets: 1"]
            writer.writerow(numData)
            laserPow = ["#Laser power:" + wavsweep['Sweeppower'][devNum]]
            writer.writerow(laserPow)
            stepSize = ["#Wavelength step-size:" + wavsweep['Stepsize'][devNum]]
            writer.writerow(stepSize)
            startWav = ["#Start wavelength:" + wavsweep['Start'][devNum]]
            writer.writerow(startWav)
            stopWav = ["#Stop wavelength:" + wavsweep['Stop'][devNum]]
            writer.writerow(stopWav)
            stitCount = ["#Stitch count: 0"]
            writer.writerow(stitCount)
            initRange = ["#Init Range:" + wavsweep['InitialRange'][devNum]]
            writer.writerow(initRange)
            newSweep = ["#New sweep plot behaviour: replace"]
            writer.writerow(newSweep)
            laseOff = ["#Turn off laser when done: no"]
            writer.writerow(laseOff)
            metric = ["#Metric Tag"]
            writer.writerow(metric)
            wavSweep = [xlabel]
            wavSweep.extend(xArray)
            writer.writerow(wavSweep)
            for x in range(len(self.autoMeasure.activeDetectors)):
                det1 = ["channel_{}".format(self.autoMeasure.activeDetectors[x] + 1)]
                for point in range(len(yArray)):
                    det1.append(yArray[point][x])
                writer.writerow(det1)
        if testType == 'Wavelength sweep w Bias Voltage':
            wavsweep = self.autoMeasure.setVoltageWavelengthSweeps
            BiasV = ["#Bias Voltage:" + wavsweep['Voltage'][devNum]]
            writer.writerow(BiasV)
            speed = ["#Sweep speed:" + wavsweep['Sweepspeed'][devNum]]
            writer.writerow(speed)
            numData = ["#Number of datasets: 1"]
            writer.writerow(numData)
            laserPow = ["#Laser power:" + wavsweep['Sweeppower'][devNum]]
            writer.writerow(laserPow)
            stepSize = ["#Wavelength step-size:" + wavsweep['Stepsize'][devNum]]
            writer.writerow(stepSize)
            startWav = ["#Start wavelength:" + wavsweep['Start'][devNum]]
            writer.writerow(startWav)
            stopWav = ["#Stop wavelength:" + wavsweep['Stop'][devNum]]
            writer.writerow(stopWav)
            stitCount = ["#Stitch count: 0"]
            writer.writerow(stitCount)
            initRange = ["#Init Range:" + wavsweep['InitialRange'][devNum]]
            writer.writerow(initRange)
            newSweep = ["#New sweep plot behaviour: replace"]
            writer.writerow(newSweep)
            laseOff = ["#Turn off laser when done: no"]
            writer.writerow(laseOff)
            metric = ["#Metric Tag"]
            writer.writerow(metric)
            wavSweep = [xlabel]
            wavSweep.extend(xArray)
            writer.writerow(wavSweep)
            for x in range(len(self.autoMeasure.activeDetectors)):
                det1 = ["channel_{}".format(self.autoMeasure.activeDetectors[x] + 1)]
                for point in range(len(yArray)):
                    det1.append(yArray[point][x])
                writer.writerow(det1)
        if testType == 'Voltage sweep':
            iv = self.autoMeasure.voltageSweeps
            stepSize = ["Resolution:" + iv['VoltRes'][devNum]]
            writer.writerow(stepSize)
            startWav = ["#Start Voltage:" + iv['VoltMin'][devNum]]
            writer.writerow(startWav)
            stopWav = ["#Stop Voltage:" + iv['VoltMax'][devNum]]
            writer.writerow(stopWav)
            wavSweep = [xlabel]
            wavSweep.extend(xArray)
            writer.writerow(wavSweep)
            det1 = [ylabel]
            for point in range(len(yArray)):
                det1.append(yArray[point])
            writer.writerow(det1)
        if testType == 'Current sweep':
            iv = self.autoMeasure.currentSweeps
            stepSize = ["Resolution:" + iv['CurrentRes'][devNum]]
            writer.writerow(stepSize)
            startWav = ["#Start Current:" + iv['CurrentMin'][devNum]]
            writer.writerow(startWav)
            stopWav = ["#Stop Current:" + iv['CurrentMax'][devNum]]
            writer.writerow(stopWav)
            stitCount = ["#Stitch count: 0"]
            writer.writerow(stitCount)
            wavSweep = [xlabel]
            wavSweep.extend(xArray)
            writer.writerow(wavSweep)
            det1 = [ylabel]
            for point in range(len(yArray)):
                det1.append(yArray[point])
            writer.writerow(det1)
        if testType == 'Voltage Sweep w Set Wavelength':
            iv = self.autoMeasure.setWavelengthVoltageSweeps
            wav = ["Wavelength:" + iv['Wavelength'][devNum]]
            writer.writerow(wav)
            stepSize = ["Resolution:" + iv['VoltRes'][devNum]]
            writer.writerow(stepSize)
            startWav = ["#Start Voltage:" + iv['VoltMin'][devNum]]
            writer.writerow(startWav)
            stopWav = ["#Stop Voltage:" + iv['VoltMax'][devNum]]
            writer.writerow(stopWav)
            wavSweep = [xlabel]
            wavSweep.extend(xArray)
            writer.writerow(wavSweep)
            det1 = [ylabel]
            for point in range(len(yArray)):
                det1.append(yArray[point])
            writer.writerow(det1)
        if testType == 'Current Sweep w Set Wavelength':
            iv = self.autoMeasure.setWavelengthCurrentSweeps
            wav = ["Wavelength:" + iv['Wavelength'][devNum]]
            writer.writerow(wav)
            stepSize = ["Resolution:" + iv['CurrentRes'][devNum]]
            writer.writerow(stepSize)
            startWav = ["#Start Current:" + iv['CurrentMin'][devNum]]
            writer.writerow(startWav)
            stopWav = ["#Stop Current:" + iv['CurrentMax'][devNum]]
            writer.writerow(stopWav)
            stitCount = ["#Stitch count: 0"]
            writer.writerow(stitCount)
            wavSweep = [xlabel]
            wavSweep.extend(xArray)
            writer.writerow(wavSweep)
            det1 = [ylabel]
            for point in range(len(yArray)):
                det1.append(yArray[point])
            writer.writerow(det1)
        f.close()

    def saveFiles(self, deviceObject, x, y, devNum, xArray, yArray, testType, motorCoord, start, stop, chipStart, saveFolder, routineName, leg = 0):
        self.save_pdf(deviceObject, x, y, xArray, yArray, saveFolder, routineName, legend = leg, )
        self.save_mat(deviceObject, devNum, motorCoord, xArray, yArray, x, y, saveFolder, routineName)
        self.save_csv(deviceObject, testType, xArray, yArray, start, stop, chipStart, motorCoord, devNum, saveFolder, routineName, x, y)