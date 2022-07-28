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
import sys
import traceback

import wx
import wx.lib.mixins.listctrl
import myMatplotlibPanel
from autoMeasureProgressDialog import autoMeasureProgressDialog
import os
import time
from filterFrame import filterFrame
import csv

global deviceList
global deviceListAsObjects
global fileLoaded


class coordinateMapPanel(wx.Panel):
    def __init__(self, parent, autoMeasure, numDevices):
        super(coordinateMapPanel, self).__init__(parent)
        self.autoMeasure = autoMeasure
        self.numDevices = numDevices
        self.InitUI()

    def InitUI(self):
        gbs = wx.GridBagSizer(0, 0)

        stMotorCoord = wx.StaticText(self, label='Motor Coordinates')

        stxMotorCoord = wx.StaticText(self, label='X')
        styMotorCoord = wx.StaticText(self, label='Y')
        stzMotorCoord = wx.StaticText(self, label='Z')

        gbs.Add(stMotorCoord, pos=(0, 2), span=(1, 2), flag=wx.ALIGN_CENTER)

        gbs.Add(stxMotorCoord, pos=(1, 2), span=(1, 1), flag=wx.ALIGN_CENTER)
        gbs.Add(styMotorCoord, pos=(1, 3), span=(1, 1), flag=wx.ALIGN_CENTER)
        gbs.Add(stzMotorCoord, pos=(1, 4), span=(1, 1), flag=wx.ALIGN_CENTER)

        self.stxMotorCoordLst = []
        self.styMotorCoordLst = []
        self.stzMotorCoordLst = []
        self.stxGdsCoordLst = []
        self.styGdsCoordLst = []
        self.elecxGdsCoordLst = []
        self.elecyGdsCoordLst = []

        self.tbGdsDevice1 = wx.ComboBox(self, size=(80, 20), choices=[], style=wx.CB_DROPDOWN)
        self.tbGdsDevice1.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.on_drop_down)

        self.tbGdsDevice2 = wx.ComboBox(self, size=(80, 20), choices=[], style=wx.CB_DROPDOWN)
        self.tbGdsDevice2.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.on_drop_down)

        self.tbGdsDevice3 = wx.ComboBox(self, size=(80, 20), choices=[], style=wx.CB_DROPDOWN)
        self.tbGdsDevice3.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.on_drop_down)

        self.GDSDevList = [self.tbGdsDevice1, self.tbGdsDevice2, self.tbGdsDevice3]

        for ii in range(self.numDevices):
            row = ii + 2
            stDevice = wx.StaticText(self, label='Device %d' % (ii + 1))
            tbxMotorCoord = wx.TextCtrl(self, size=(80, 20))
            tbyMotorCoord = wx.TextCtrl(self, size=(80, 20))
            tbzMotorCoord = wx.TextCtrl(self, size=(80, 20))

            btnGetMotorCoord = wx.Button(self, label='Get Pos.', size=(50, 20))

            self.stxMotorCoordLst.append(tbxMotorCoord)

            self.styMotorCoordLst.append(tbyMotorCoord)
            self.stzMotorCoordLst.append(tbzMotorCoord)

            if fileLoaded is True:

                global deviceListAsObjects
                for dev in deviceListAsObjects:
                    if self.GDSDevList[ii] == dev.getDeviceID():
                        self.stxGdsCoordLst.append(dev.getOpticalCoordinates()[0])
                        self.styGdsCoordLst.append(dev.getOpticalCoordinates()[1])
                        self.elecxGdsCoordLst.append(dev.getReferenceBondPad()[1])
                        self.elecyGdsCoordLst.append(dev.getReferenceBondPad()[2])

            gbs.Add(stDevice, pos=(row, 0), span=(1, 1))
            gbs.Add(tbxMotorCoord, pos=(row, 2), span=(1, 1))
            gbs.Add(tbyMotorCoord, pos=(row, 3), span=(1, 1))
            gbs.Add(tbzMotorCoord, pos=(row, 4), span=(1, 1))
            gbs.Add(self.GDSDevList[ii], pos=(row, 1), span=(1, 1))
            gbs.Add(btnGetMotorCoord, pos=(row, 6), span=(1, 1))

            # For each button map a function which is called when it is pressed
            btnGetMotorCoord.Bind(wx.EVT_BUTTON,
                                  lambda event, xcoord=tbxMotorCoord, ycoord=tbyMotorCoord,
                                         zcoord=tbzMotorCoord: self.Event_OnCoordButton(
                                      event, xcoord, ycoord, zcoord))

        gbs.AddGrowableCol(1)
        gbs.AddGrowableCol(2)
        gbs.AddGrowableCol(3)
        gbs.AddGrowableCol(4)
        self.SetSizerAndFit(gbs)

    def on_drop_down(self, event):
        global deviceList
        for GDSDevice in self.GDSDevList:
            for dev in deviceList:
                GDSDevice.Append(dev)

    def Event_OnCoordButton(self, event, xcoord, ycoord, zcoord):
        """ Called when the button is pressed to get the current motor coordinates, and put it into the text box. """
        motorPosition = self.autoMeasure.motor.getPosition()
        xcoord.SetValue(str(motorPosition[0]))
        ycoord.SetValue(str(motorPosition[1]))
        zcoord.SetValue(str(motorPosition[2]))

    def getMotorCoords(self):
        """ Reads the motor coordinates from all completed text fields. """
        coordsLst = []
        for tcx, tcy, tcz in zip(self.stxMotorCoordLst, self.styMotorCoordLst, self.stzMotorCoordLst):
            xval = tcx.GetValue()
            yval = tcy.GetValue()
            zval = tcz.GetValue()
            if xval != '' and yval != '' and zval != '':
                coordsLst.append((float(xval), float(yval), float(zval)))
        return coordsLst

    def getGdsCoordsOpt(self):
        """ Reads the GDS coordinates from all completed text fields. """
        coordsLst = []
        for tcx, tcy in zip(self.stxGdsCoordLst, self.styGdsCoordLst):
            xval = tcx.GetValue()
            yval = tcy.GetValue()
            if xval != '' and yval != '':
                coordsLst.append((float(xval), float(yval)))
        return coordsLst

    def getGdsCoordsElec(self):
        """ Reads the GDS coordinates from all completed text fields. """
        coordsLst = []
        for tcx, tcy in zip(self.elecxGdsCoordLst, self.elecyGdsCoordLst):
            xval = tcx.GetValue()
            yval = tcy.GetValue()
            if xval != '' and yval != '':
                coordsLst.append((float(xval), float(yval)))
        return coordsLst


class autoMeasurePanel(wx.Panel):

    def __init__(self, parent, autoMeasureE, autoMeasureO):
        super(autoMeasurePanel, self).__init__(parent)
        self.autoMeasureElec = autoMeasureE
        self.autoMeasureOpt = autoMeasureO
        self.device_list = []
        self.InitUI()

    def InitUI(self):

        global fileLoaded
        fileLoaded = False  # list of devices is currently empty
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
        sbMeasurement = wx.StaticBox(self, label='Move to Device')
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

        selectBox = wx.BoxSizer(wx.HORIZONTAL)
        selectBox.AddMany([(self.checkAllBtn, 0, wx.EXPAND), (self.uncheckAllBtn, 0, wx.EXPAND),
                           (self.filterBtn, 0, wx.EXPAND)])

        # Add devices checklist
        self.checkList = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        self.checkList.InsertColumn(0, 'Device', width=100)
        checkListBox = wx.BoxSizer(wx.HORIZONTAL)
        checkListBox.Add(self.checkList, proportion=1, flag=wx.EXPAND)

        # Add Optical Alignment set up
        self.coordMapPanelOpt = coordinateMapPanel(self, self.autoMeasureOpt, 3)
        opticalBox = wx.BoxSizer(wx.HORIZONTAL)
        opticalBox.Add(self.coordMapPanelOpt, proportion=1, flag=wx.EXPAND)

        # Add Electrical Alignment set up
        self.coordMapPanelElec = coordinateMapPanel(self, self.autoMeasureElec, 3)
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

        self.startBtn = wx.Button(self, label='Start', size=(70, 20))
        self.startBtn.Bind(wx.EVT_BUTTON, self.OnButton_Start)
        self.saveBtn = wx.Button(self, label='Save', size=(70, 20))
        self.saveBtn.Bind(wx.EVT_BUTTON, self.OnButton_Save)
        elecOptButtonBox = wx.BoxSizer(wx.HORIZONTAL)
        elecOptButtonBox.AddMany([(self.startBtn, 0, wx.EXPAND), (self.saveBtn, 0, wx.EXPAND)])

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
                            (saveLabelBox, 0, wx.EXPAND), (saveBox, 0, wx.EXPAND),
                            (checkListBox, 0, wx.EXPAND), (selectBox, 0, wx.EXPAND)])

        # Populate Optical Box with alignment and buttons
        vboxOptical.AddMany([(opticalBox, 0, wx.EXPAND), (optButtonBox, 0, wx.EXPAND)])

        # Populate Electrical Box with alignment and buttons
        vboxElectrical.AddMany([(electricalBox, 0, wx.EXPAND), (elecButtonBox, 0, wx.EXPAND)])

        # Populate Measurement Box with drop down menu and go button
        vboxMeasurement.AddMany([(elecOptButtonBox, 0, wx.EXPAND), (moveLabelBox, 0, wx.EXPAND), (goBoxOpt, 0, wx.EXPAND),
                                 (moveElecLabelBox, 0, wx.EXPAND), (goBoxElec, 0, wx.EXPAND)])

        # Add all boxes to outer box
        vboxOuter.AddMany([(vboxUpload, 0, wx.EXPAND), (vboxOptical, 0, wx.EXPAND),
                           (vboxElectrical, 0, wx.EXPAND), (vboxMeasurement, 0, wx.EXPAND)])
        matPlotBox.Add(vboxOuter, flag=wx.LEFT | wx.TOP | wx.ALIGN_LEFT, border=0, proportion=0)

        self.SetSizer(matPlotBox)

    def checkListSort(self, item1, item2):
        # Items are the client data associated with each entry
        if item2 < item2:
            return -1
        elif item1 > item2:
            return 1
        else:
            return 0

    def createFilterFrame(self):
        """Opens up a frame to facilitate filtering of devices within the checklist."""
        global deviceListAsObjects
        try:
            filterFrame(None, self.checkList, self.device_list)

        except Exception as e:
            dial = wx.MessageDialog(None, 'Could not initiate filter. ' + traceback.format_exc(),
                                    'Error', wx.ICON_ERROR)
            dial.ShowModal()

    def OnButton_ChooseCoordFile(self, event):
        """ Opens a file dialog to select a coordinate file. """
        fileDlg = wx.FileDialog(self, "Open", "", "",
                                "Text Files (*.txt)|*.txt",
                                wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        fileDlg.ShowModal()
        self.coordFileTb.SetValue(fileDlg.GetFilenames()[0])
        # fileDlg.Destroy()
        self.autoMeasureOpt.readCoordFile(fileDlg.GetPath())
        global deviceListAsObjects
        deviceListAsObjects = self.autoMeasureOpt.devices
        self.device_list = deviceListAsObjects
        global deviceList
        deviceList = []
        for device in deviceListAsObjects:
            deviceList.append(device.getDeviceID())
        self.devSelectCb.Clear()
        self.devSelectCb.AppendItems(deviceList)
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
        global fileLoaded
        fileLoaded = True
        self.Refresh()

    def OnButton_CheckAll(self, event):
        """Selects all items in the devices check list"""
        for ii in range(self.checkList.GetItemCount()):
            self.checkList.CheckItem(ii, True)

    def OnButton_GotoDeviceOpt(self, event):
        selectedDevice = self.devSelectCb.GetValue()
        global deviceListAsObjects
        for device in deviceListAsObjects:
            if device.getDeviceID == selectedDevice:
                gdsCoord = (device.getOpticalCoordinates[0], device.getOpticalCoordinates[1])
                motorCoord = self.autoMeasureOpt.gdsToMotorCoords(gdsCoord)
                self.autoMeasureOpt.motor.moveAbsoluteXYZ(motorCoord[0], motorCoord[1], motorCoord[2])

    def OnButton_GotoDeviceElec(self, event):
        selectedDevice = self.devSelectCb.GetValue()
        global deviceListAsObjects
        for device in deviceListAsObjects:
            if device.getDeviceID == selectedDevice:
                gdsCoord = (device.getReferenceBondPad[1], device.getReferenceBondPad[2])
                motorCoord = self.autoMeasureElec.gdsToMotorCoords(gdsCoord)
                self.autoMeasureElec.motor.moveAbsoluteXYZ(motorCoord[0], motorCoord[1], motorCoord[2])

    def OnButton_UncheckAll(self, event):
        """Deselects all items in the devices checklist"""
        for ii in range(self.checkList.GetItemCount()):
            self.checkList.CheckItem(ii, False)

    def OnButton_SelectOutputFolder(self, event):
        """ Opens a file dialog to select an output directory for automatic measurement. """
        dirDlg = wx.DirDialog(self, "Open", "", wx.DD_DEFAULT_STYLE)
        dirDlg.ShowModal()
        self.outputFolderTb.SetValue(dirDlg.GetPath())
        dirDlg.Destroy()

    def OnButton_CalculateOpt(self, event):
        """ Computes the optical coordinate transformation matrix. """
        A = self.autoMeasureOpt.findCoordinateTransform(self.coordMapPanelOpt.getMotorCoords(),
                                                        self.coordMapPanelOpt.getGdsCoordsOpt())
        print('Coordinate transform matrix')
        print(A)

    def OnButton_CalculateElec(self, event):
        """ Computes the electrical coordinate transformation matrix. """
        A = self.autoMeasureElec.findCoordinateTransform(self.coordMapPanelElec.getMotorCoords(),
                                                         self.coordMapPanelElec.getGdsCoordsElec())
        print('Coordinate transform matrix')
        print(A)

    # TODO: Update this for electro-optic measurements and current data formats
    def OnButton_Start(self, event):
        """ Starts an automatic measurement. """

        # Disable detector auto measurement
        self.autoMeasure.laser.ctrlPanel.laserPanel.laserPanel.haltDetTimer()

        # Make a folder with the current time
        timeStr = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())
        self.autoMeasure.saveFolder = os.path.join(self.outputFolderTb.GetValue(), timeStr)
        if not os.path.exists(self.autoMeasure.saveFolder):
            os.makedirs(self.autoMeasure.saveFolder)

        deviceDict = self.autoMeasure.deviceCoordDict
        checkedIndices = self.checkList.getCheckedIndices()
        checkedIds = [self.checkList.GetItemData(id) for id in checkedIndices]
        checkedDevices = [name for name in deviceDict if deviceDict[name]['id'] in checkedIds]
        # self.autoMeasure.beginMeasure(checkedDevices)
        # Copy settings from laser panel
        self.autoMeasure.laser.ctrlPanel.laserPanel.laserPanel.copySweepSettings()
        # Create a measurement progress dialog.
        autoMeasureDlg = autoMeasureProgressDialog(self, title='Automatic measurement')
        autoMeasureDlg.runMeasurement(checkedDevices, self.autoMeasure)

        # Enable detector auto measurement
        self.autoMeasure.laser.ctrlPanel.laserPanel.laserPanel.startDetTimer()

    def OnButton_Filter(self, event):

        self.createFilterFrame()
        self.Refresh()

    def OnButton_Save(self, event):
        """ Computes the coordinate transformation matrix. """
        A = self.autoMeasureOpt.findCoordinateTransform(self.coordMapPanelOpt.getMotorCoords(),
                                                        self.coordMapPanelOpt.getGdsCoordsOpt())

        B = self.autoMeasureElec.findCoordinateTransform(self.coordMapPanelElec.getMotorCoords(),
                                                         self.coordMapPanelElec.getGdsCoordsElec())

        # Make a folder with the current time
        timeStr = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())
        csvFileName = os.path.join(self.outputFolderTb.GetValue(), timeStr + 'Optical Matrix.csv')

        f = open(csvFileName, 'w', newline='')
        writer = csv.writer(f)

        row0 = A[0][0]
        writer.writerow(row0)
        row1 = A[0][1]
        writer.writerow(row1)
        row2 = A[0][2]
        writer.writerow(row2)
        blank = []
        writer.writerow(blank)
        row3 = B[0][0]
        writer.writerow(row3)
        row4 = B[0][1]
        writer.writerow(row4)
        row5 = B[0][2]
        writer.writerow(row5)
        f.close()
