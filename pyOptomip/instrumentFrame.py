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
from outputlogPanel import outputlogPanel
import sys
from fineAlign import fineAlign
from fineAlignPanel import fineAlignPanel
import traceback
from logWriter import logWriter,logWriterError
from autoMeasurePanel import autoMeasurePanel
from autoMeasure import autoMeasure


class instrumentFrame(wx.Frame):
  
    def __init__(self, parent, instList):
        """
        creates frame that is 3/4 size of the display, calls InitUI to initialize the feature of the frame,
         if it's unable to do this it will disconnect from devices and destroy the created frame
        Args:
            parent:
            instList:
        """
        displaySize = wx.DisplaySize()
        super(instrumentFrame, self).__init__(parent, title='Instrument Control', \
              size=(displaySize[0]*3/4.0, displaySize[1]*3/4.0))
        
        self.instList = instList;
        try:
            self.InitUI()
        except Exception as e:
            for inst in instList:
                inst.disconnect()
            self.Destroy()
            raise
        self.Centre()
        self.Show()  
        
    def InitUI(self):
        """
        using instlist this function will create the necessary panels for the connected devices,
        if the device is a motor it will create a vertical sized box panel if it is anything else
        it will create a horizontal box panel, if laser and motor are connected (using motorfound
        and laserfound) it will add the fine align panel to the vertical motor panel, if the vertical
        motor panel does not exist then error message will appear, if laser and motor found will add
        automeasure panel to vertical motor panel, fills in the rest of the space with panels, sets up
        log display
        """
        self.Bind(wx.EVT_CLOSE, self.OnExitApp)
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        
        for inst in self.instList:
            panel = inst.panelClass(self, inst);
            
            if inst.isMotor:
                motorVbox = wx.BoxSizer(wx.VERTICAL)
                motorVbox.Add(panel, proportion=0, border=0, flag=wx.EXPAND)
            else:
                hbox.Add(panel, proportion=1, border=0, flag=wx.EXPAND)
                
                

        if self.laserFound() and self.motorFound():
            self.fineAlign = fineAlign(self.getLasers()[0], self.getMotors()[0])
            try:
                self.fineAlignPanel = fineAlignPanel(self, self.fineAlign)
            except Exception as e:
                dial = wx.MessageDialog(None, 'Could not initiate instrument control. '+traceback.format_exc(), 'Error', wx.ICON_ERROR)
                dial.ShowModal()
            motorVbox.Add(self.fineAlignPanel, proportion=0, flag=wx.EXPAND)
            
            self.autoMeasure = autoMeasure(self.getLasers()[0], self.getMotors()[0], self.fineAlign)
            
            self.autoMeasurePanel = autoMeasurePanel(self, self.autoMeasure)
            motorVbox.Add(self.autoMeasurePanel, proportion=0, flag=wx.EXPAND) 
        
        if self.motorFound():
            hbox.Add(motorVbox)
        
        
        vbox.Add(hbox, 3, wx.EXPAND)
        self.log = outputlogPanel(self)
        vbox.Add(self.log, 1, wx.EXPAND)
        self.SetSizer(vbox)
        
        
        sys.stdout = logWriter(self.log)
        sys.stderr = logWriterError(self.log)
        

    def motorFound(self):
        """
        check instlist.ismotor to see if instlist contains any motors, if it does returns true
        Returns: True if there is a motor in instlist, false otherwise

        """
        motorFound = False
        for inst in self.instList:
            motorFound = motorFound | inst.isMotor
        return motorFound
        
    def laserFound(self):
        """
        check instlist.isLaser to see if instlist contains any lasers, if it does return true
        Returns:
        """
        laserFound = False
        for inst in self.instList:
            laserFound = laserFound | inst.isLaser
        return laserFound
        
    def getLasers(self):
        """
        finds the location of the lasers in instlist array and places them into laserlist array
        Returns:

        """
        laserList = []
        for inst in self.instList:
            if inst.isLaser:
                laserList.append(inst)
        return laserList
        
    def getMotors(self):
        """
        finds the location of the motors in instlist array and places them into motorlist array
        Returns:

        """
        motorList = []
        for inst in self.instList:
            if inst.isMotor:
                motorList.append(inst)
        return motorList
        
    def OnExitApp(self, event):
        """
        disconnects from devices and destroys the frame
        Args:
            event:
        """
        for inst in self.instList:
            inst.disconnect()
        self.Destroy()
    