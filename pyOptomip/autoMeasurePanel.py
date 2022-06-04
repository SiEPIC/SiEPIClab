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

import wx
import numpy as np
from wx.lib.mixins.listctrl import CheckListCtrlMixin
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from autoMeasureProgressDialog import autoMeasureProgressDialog
import os
import time


class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        ListCtrlAutoWidthMixin.__init__(self) # Sets the width of the last column to take all available space
        CheckListCtrlMixin.__init__(self) # Adds check boxes to listctrl
        
    def CheckAll(self):
        """ Checks all boxes in the list"""
        for ii in xrange(self.GetItemCount()):
            self.CheckItem(ii,True)
    
    def UncheckAll(self):
        """ Unchecks all boxes in the list"""
        for ii in xrange(self.GetItemCount()):
            self.CheckItem(ii,False)
            
    def getCheckedIndices(self):
        """ Returns a list of indices of all checked items in the list. """
        return [ii for ii in xrange(self.GetItemCount()) if self.IsChecked(ii)]
            
class coordinateMapPanel(wx.Panel):
    def __init__(self, parent, autoMeasure, numDevices):
        super(coordinateMapPanel, self).__init__(parent)
        self.autoMeasure = autoMeasure
        self.numDevices = numDevices
        self.InitUI()   
        
    def InitUI(self):
        gbs = wx.GridBagSizer(0,0)
        
        
        stMotorCoord = wx.StaticText(self, label='Motor Coords.')
        stGdsCoord = wx.StaticText(self, label='GDS Coords.')
        
        stxMotorCoord = wx.StaticText(self, label='X')
        styMotorCoord = wx.StaticText(self, label='Y')
        stxGdsCoord = wx.StaticText(self, label='X')
        styGdsCoord = wx.StaticText(self, label='Y')
        
        
        gbs.Add(stMotorCoord, pos=(0,1), span=(1,2), flag = wx.ALIGN_CENTER)
        gbs.Add(stGdsCoord, pos=(0,3), span=(1,2), flag = wx.ALIGN_CENTER)
        
        gbs.Add(stxMotorCoord, pos=(1,1), span=(1,1), flag = wx.ALIGN_CENTER)
        gbs.Add(styMotorCoord, pos=(1,2), span=(1,1), flag = wx.ALIGN_CENTER)
        gbs.Add(stxGdsCoord, pos=(1,3), span=(1,1), flag = wx.ALIGN_CENTER)
        gbs.Add(styGdsCoord, pos=(1,4), span=(1,1), flag = wx.ALIGN_CENTER)
        
        self.stxMotorCoordLst = []
        self.styMotorCoordLst = []
        self.stxGdsCoordLst = []
        self.styGdsCoordLst = []
        
        
        for ii in xrange(self.numDevices):
            row = ii+2
            stDevice = wx.StaticText(self, label='Device %d'%(ii+1))
            tbxMotorCoord = wx.TextCtrl(self, size=(80,20))
            tbyMotorCoord = wx.TextCtrl(self, size=(80,20))
            tbxGdsCoord = wx.TextCtrl(self, size=(80,20))
            tbyGdsCoord = wx.TextCtrl(self, size=(80,20)) 
            btnGetMotorCoord = wx.Button(self, label='Get Pos.', size=(50, 20))
            
            self.stxMotorCoordLst.append(tbxMotorCoord)
            self.styMotorCoordLst.append(tbyMotorCoord)
            self.stxGdsCoordLst.append(tbxGdsCoord)
            self.styGdsCoordLst.append(tbyGdsCoord)
            
            gbs.Add(stDevice, pos=(row,0), span=(1,1))
            gbs.Add(tbxMotorCoord, pos=(row,1), span=(1,1))
            gbs.Add(tbyMotorCoord, pos=(row,2), span=(1,1))
            gbs.Add(tbxGdsCoord, pos=(row,3), span=(1,1))
            gbs.Add(tbyGdsCoord, pos=(row,4), span=(1,1))
            gbs.Add(btnGetMotorCoord, pos=(row,5), span=(1,1))
            # For each button map a function which is called when it is pressed
            btnGetMotorCoord.Bind(wx.EVT_BUTTON, lambda event, xcoord=tbxMotorCoord, ycoord=tbyMotorCoord: self.Event_OnCoordButton(event, xcoord, ycoord) )
            
        gbs.AddGrowableCol(1)
        gbs.AddGrowableCol(2)
        gbs.AddGrowableCol(3)
        gbs.AddGrowableCol(4)
        self.SetSizerAndFit(gbs)
        
    def Event_OnCoordButton(self, event, xcoord, ycoord):
        """ Called when the button is pressed to get the current motor coordinates, and put it into the text box. """
        motorPosition = self.autoMeasure.motor.getPosition()
        xcoord.SetValue(str(motorPosition[0]))
        ycoord.SetValue(str(motorPosition[1]))
        
    def getMotorCoords(self):
        """ Reads the motor coordinates from all completed text fields. """
        coordsLst = []
        for tcx,tcy in zip(self.stxMotorCoordLst,self.styMotorCoordLst):
            xval = tcx.GetValue()
            yval = tcy.GetValue()
            if xval != '' and yval != '':
                coordsLst.append((float(xval),float(yval)))
        return coordsLst
    
    def getGdsCoords(self):
        """ Reads the GDS coordinates from all completed text fields. """
        coordsLst = []
        for tcx,tcy in zip(self.stxGdsCoordLst,self.styGdsCoordLst):
            xval = tcx.GetValue()
            yval = tcy.GetValue()
            if xval != '' and yval != '':
                coordsLst.append((float(xval),float(yval)))
        return coordsLst

# Panel that appears in the Instrument Control window to set up automatic measurements.	
class autoMeasurePanel(wx.Panel):
 
    def __init__(self, parent, autoMeasure):
        super(autoMeasurePanel, self).__init__(parent)
        self.autoMeasure = autoMeasure
        self.InitUI()   
        
        
    def InitUI(self):
        
        sbOuter = wx.StaticBox(self, label='Automatic measurement');
        vboxOuter = wx.StaticBoxSizer(sbOuter, wx.VERTICAL)
        
        
        st1 = wx.StaticText(self, label='Coordinate file:')
        hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        hbox0.Add(st1, proportion=1, flag=wx.EXPAND)
        ##
        self.coordFileTb = wx.TextCtrl(self,style=wx.TE_READONLY)
        self.coordFileTb.SetValue('No file selected')
        self.coordFileSelectBtn = wx.Button(self, wx.ID_OPEN, size=(50, 20))
        self.coordFileSelectBtn.Bind( wx.EVT_BUTTON, self.OnButton_ChooseCoordFile)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.AddMany([(self.coordFileTb, 1, wx.EXPAND), (self.coordFileSelectBtn, 0, wx.EXPAND)])
        ##
        self.checkAllBtn = wx.Button(self, label='Select All', size=(80, 20))
        self.checkAllBtn.Bind( wx.EVT_BUTTON, self.OnButton_CheckAll)  
        self.uncheckAllBtn = wx.Button(self, label='Unselect All', size=(80, 20))
        self.uncheckAllBtn.Bind( wx.EVT_BUTTON, self.OnButton_UncheckAll)      
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.AddMany([(self.checkAllBtn, 0, wx.EXPAND), (self.uncheckAllBtn, 0, wx.EXPAND)])
        ##
        self.checkList = CheckListCtrl(self)
        self.checkList.InsertColumn(0, 'Device', width=100)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3.Add(self.checkList, proportion=1, flag=wx.EXPAND)
        ##
        self.coordMapPanel = coordinateMapPanel(self, self.autoMeasure,5)
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        hbox4.Add(self.coordMapPanel, proportion=1, flag=wx.EXPAND)
        ##
        self.calculateBtn = wx.Button(self, label='Calculate', size=(70, 20))
        self.calculateBtn.Bind( wx.EVT_BUTTON, self.OnButton_Calculate) 
        
        self.startBtn = wx.Button(self, label='Start', size=(70, 20))
        self.startBtn.Bind( wx.EVT_BUTTON, self.OnButton_Start) 
        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        hbox5.AddMany([(self.calculateBtn, 0, wx.EXPAND), (self.startBtn, 0, wx.EXPAND)])
        ##
        
        st2 = wx.StaticText(self, label='Save folder:')
        hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        hbox6.Add(st2, proportion=1, flag=wx.EXPAND)
        ##
        self.outputFolderTb = wx.TextCtrl(self,style=wx.TE_READONLY)
        self.outputFolderBtn = wx.Button(self, wx.ID_OPEN, size=(50, 20))
        self.outputFolderBtn.Bind( wx.EVT_BUTTON, self.OnButton_SelectOutputFolder)   
        hbox7 = wx.BoxSizer(wx.HORIZONTAL)
        hbox7.AddMany([(self.outputFolderTb, 1, wx.EXPAND), (self.outputFolderBtn, 0, wx.EXPAND)])
        ##
        
        st3 = wx.StaticText(self, label='Move to individual device:')
        hbox8 = wx.BoxSizer(wx.HORIZONTAL)
        hbox8.Add(st3, proportion=1, flag=wx.EXPAND)
        ##
        self.devSelectCb = wx.ComboBox(self, style=wx.CB_READONLY, size=(200,20))
        self.gotoDevBtn = wx.Button(self, label='Go', size=(70, 20))
        self.gotoDevBtn.Bind( wx.EVT_BUTTON, self.OnButton_GotoDevice) 
        hbox9 = wx.BoxSizer(wx.HORIZONTAL)
        hbox9.AddMany([(self.devSelectCb, 1, wx.EXPAND), (self.gotoDevBtn, 0, wx.EXPAND)])
        ##
        vboxOuter.AddMany([(hbox0, 0, wx.EXPAND), (hbox1, 0, wx.EXPAND), (hbox2, 0, wx.EXPAND), \
                           (hbox3, 0, wx.EXPAND), (hbox4, 0, wx.EXPAND), (hbox5, 0, wx.EXPAND), \
                           (hbox6, 0, wx.EXPAND), (hbox7, 0, wx.EXPAND), (hbox8, 0, wx.EXPAND), \
                           (hbox9, 0, wx.EXPAND)])
        self.SetSizer(vboxOuter)
        
        
    def checkListSort(self, item1, item2):
        # Items are the client data associated with each entry
        if item2 < item2:
            return -1
        elif item1 > item2:
            return 1
        else:
            return 0
        
        
    def OnButton_ChooseCoordFile(self, event):
        """ Opens a file dialog to select a coordinate file. """
        fileDlg = wx.FileDialog(self, "Open", "", "", 
                                       "Text Files (*.txt)|*.txt", 
                                       wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        fileDlg.ShowModal()
        self.coordFileTb.SetValue(fileDlg.GetFilenames()[0])      
        fileDlg.Destroy()   
        self.autoMeasure.readCoordFile(fileDlg.GetPath())
        deviceDict = self.autoMeasure.deviceCoordDict
        deviceLst = [dev for dev in deviceDict]
        self.devSelectCb.Clear()
        self.devSelectCb.AppendItems(deviceLst)
        # Adds items to the check list
        self.checkList.DeleteAllItems()
        for ii,device in enumerate(deviceDict):
            self.checkList.InsertStringItem(ii, device)
            self.checkList.SetItemData(ii,deviceDict[device]['id'])
        self.checkList.SortItems(self.checkListSort) # Make sure items in list are sorted
        self.Refresh()
        
    def OnButton_CheckAll(self, event):
        self.checkList.CheckAll()
        
    def OnButton_GotoDevice(self, event):
        selectedDevice = self.devSelectCb.GetValue()
        deviceDict = self.autoMeasure.deviceCoordDict
        
        gdsCoord = (deviceDict[selectedDevice]['x'],deviceDict[selectedDevice]['y'])
        motorCoord = self.autoMeasure.gdsToMotorCoords(gdsCoord)

        self.autoMeasure.motor.moveAbsoluteXY(motorCoord[0], motorCoord[1])
        
        
    def OnButton_UncheckAll(self, event):
        self.checkList.UncheckAll()
        
    def OnButton_SelectOutputFolder(self, event):
        """ Opens a file dialog to select an output directory for automatic measurement. """
        dirDlg = wx.DirDialog(self, "Open", "", wx.DD_DEFAULT_STYLE)
        dirDlg.ShowModal()
        self.outputFolderTb.SetValue(dirDlg.GetPath())      
        dirDlg.Destroy()  
        
    def OnButton_Calculate(self, event):
        """ Computes the coordinate transformation matrix. """
        A = self.autoMeasure.findCoordinateTransform(self.coordMapPanel.getMotorCoords(),\
                                                 self.coordMapPanel.getGdsCoords())
        print 'Coordinate transform matrix'
        print A
                                                 
    def OnButton_Start(self, event):
        """ Starts an automatic measurement. """
    
        # Disable detector auto measurement
        self.autoMeasure.laser.ctrlPanel.laserPanel.laserPanel.haltDetTimer()
    
        # Make a folder with the current time
        timeStr = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())
        self.autoMeasure.saveFolder = os.path.join(self.outputFolderTb.GetValue(),timeStr)
        if not os.path.exists(self.autoMeasure.saveFolder):
            os.makedirs(self.autoMeasure.saveFolder)

        deviceDict = self.autoMeasure.deviceCoordDict
        checkedIndices = self.checkList.getCheckedIndices()
        checkedIds = [self.checkList.GetItemData(id) for id in checkedIndices]
        checkedDevices = [name for name in deviceDict if deviceDict[name]['id'] in checkedIds]
        #self.autoMeasure.beginMeasure(checkedDevices)
        # Copy settings from laser panel
        self.autoMeasure.laser.ctrlPanel.laserPanel.laserPanel.copySweepSettings()
        # Create a measurement progress dialog.
        autoMeasureDlg = autoMeasureProgressDialog(self, title='Automatic measurement')
        autoMeasureDlg.runMeasurement(checkedDevices, self.autoMeasure)
        
        # Enable detector auto measurement
        self.autoMeasure.laser.ctrlPanel.laserPanel.laserPanel.startDetTimer()