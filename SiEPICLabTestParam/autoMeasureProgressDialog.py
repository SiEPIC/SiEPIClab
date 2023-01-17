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
from wx.lib.delayedresult import startWorker

# Dialog box that appears while an automatic measurement is running.
class autoMeasureProgressDialog(wx.Dialog):

    def __init__(self, *args, **kw):
        super(autoMeasureProgressDialog, self).__init__(*args, **kw) 
        self.InitUI()
        
    def InitUI(self):
        self.abort = False
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.gauge = wx.Gauge(self, range=100, size=(250, 25))
        
        vbox.Add(self.gauge, proportion=0, flag=wx.ALIGN_CENTRE)
        
        self.text = wx.StaticText(self)
        vbox.Add(self.text, proportion=0, flag=wx.ALIGN_CENTRE)
        
        self.stopBtn = wx.Button(self, wx.ID_STOP)
        self.stopBtn.Bind( wx.EVT_BUTTON, self.OnButton_Stop)
        vbox.Add(self.stopBtn, proportion=0, flag=wx.ALIGN_CENTRE)
        
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.SetSizerAndFit(vbox)
        
    def OnClose(self, event):
        self.abort = 1
        

    def runMeasurement(self, devices,autoMeasure):
        """ Runs the automatic measurement."""
        self.numDevices = len(devices)
        self.gauge.SetRange(self.numDevices)
        self.text.SetLabel('0 out of %d devices measured'%self.numDevices)
        # Run the automatic measurement in a separate thread so it doesnt block the GUI.
        startWorker(self.measurementDoneCb, self.doMeasurement, wargs=(autoMeasure,devices,self.checkAborted,self.slowThreadUpdateGauge))
        self.ShowModal()
        
    def checkAborted(self):
        return self.abort
        
    def slowThreadUpdateGauge(self,ii):
        wx.CallAfter(self.updateGauge,ii)
        
    def updateGauge(self,ii):
        self.gauge.SetValue(ii)
        self.text.SetLabel('%d out of %d devices measured'%(ii,self.numDevices))
        
    def doMeasurement(self,autoMeasure, devices, abortFunction, updateFunction):
        self.exception = None
        try:
            autoMeasure.beginMeasure(devices, abortFunction=abortFunction, updateFunction=updateFunction)
        except Exception as e:
            self.exception = e
        return 0
            
    def measurementDoneCb(self,result):
        if self.exception:
            print(self.exception)
        self.Destroy()
            
        
    def OnButton_Stop(self,event):
        self.abort = True
        
        
        