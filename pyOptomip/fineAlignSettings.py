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

# Dialog box containing the fine align settings.
class fineAlignSettings(wx.Dialog):
  
    def __init__(self, parent, fineAlign):
        super(fineAlignSettings, self).__init__(parent, style=wx.RESIZE_BORDER | wx.DEFAULT_DIALOG_STYLE)
        self.fineAlign = fineAlign
        self.InitUI()   
        
    def InitUI(self):
    
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.cbList = []
        self.cbOptions = []        
        # Get options
        for slotInfo in self.fineAlign.laser.pwmSlotMap:
            self.cbOptions.append('Slot %d Detector %d' %(slotInfo[0], slotInfo[1]+1))
        self.cbOptions.append('None')
            
        numRows = len(self.fineAlign.laser.pwmSlotMap)+10
        
        fgs = wx.FlexGridSizer(numRows, 2, 9, 25)
        fgsWidgetList = []
        stTitle = wx.StaticText(self, label='Fine align detector priority') 
        fgsWidgetList.append((stTitle,0))
        fgsWidgetList.append((0,0))
        for ii,slotInfo in enumerate(self.fineAlign.laser.pwmSlotMap):
            # Get the current priority from the file align object. If the priority
            # list is smaller than thenumber of detectors, set extras to None
            if ii >= len(self.fineAlign.detectorPriority):
                currentOption = 'None'
            else:
                currentOption = self.cbOptions[self.fineAlign.detectorPriority[ii]]
                
            st = wx.StaticText(self, label='Priority %d'%(ii+1))
            fgsWidgetList.append((st))
            cb = wx.ComboBox(self, choices = self.cbOptions, style=wx.CB_READONLY, value=currentOption)
            self.cbList.append(cb)
            fgsWidgetList.append((cb))

        stWavelength = wx.StaticText(self, label='Wavelength (nm)')
        fgsWidgetList.append((stWavelength,0))
        self.tcWavelength = wx.TextCtrl(self)
        self.tcWavelength.SetValue(str(self.fineAlign.wavelength*1e9))
        fgsWidgetList.append((self.tcWavelength,0))
        
        stSlot = wx.StaticText(self, label='Laser slot')
        fgsWidgetList.append((stSlot,0))
        laserSelectChoices = ['auto']
        laserSelectChoices.extend(map(str, self.fineAlign.laser.findTLSSlots()))
        
        self.laserSlotCb = wx.ComboBox(self, choices=laserSelectChoices, style=wx.CB_READONLY, value=self.fineAlign.laserSlot)
        fgsWidgetList.append((self.laserSlotCb,0))
        
        stOutput = wx.StaticText(self, label='Laser output')
        fgsWidgetList.append((stOutput,0))
        laserOutputOptions = ['High power', 'Low SSE']
        self.laserOutputMap = dict([('High power', 'highpower'), ('Low SSE', 'lowsse')])
        self.laserOutputMap2 = dict([('highpower', 'High power'), ('lowsse', 'Low SSE')])
        self.laserOutputCb = wx.ComboBox(self, choices=laserOutputOptions, style=wx.CB_READONLY, value=self.laserOutputMap2[self.fineAlign.laserOutput])
        fgsWidgetList.append((self.laserOutputCb,0))
        
        stPower = wx.StaticText(self, label='Power (dBm)')
        fgsWidgetList.append((stPower,0))
        self.tcPower = wx.TextCtrl(self)
        self.tcPower.SetValue(str(self.fineAlign.laserPower))
        fgsWidgetList.append((self.tcPower,0))
        
        stStep = wx.StaticText(self, label='Step size (um)')
        fgsWidgetList.append((stStep,0))
        self.tcStep = wx.TextCtrl(self)
        self.tcStep.SetValue(str(self.fineAlign.stepSize))
        fgsWidgetList.append((self.tcStep,0))

        stIter = wx.StaticText(self, label='Iterations')
        fgsWidgetList.append((stIter,0))
        self.tcIter = wx.TextCtrl(self)
        self.tcIter.SetValue(str(self.fineAlign.numGradientIter))
        fgsWidgetList.append((self.tcIter,0))        
        
        stThresh = wx.StaticText(self, label='Scan threshold (dBm)')
        fgsWidgetList.append((stThresh,0))
        self.tcThresh = wx.TextCtrl(self)
        self.tcThresh.SetValue(str(self.fineAlign.threshold))
        fgsWidgetList.append((self.tcThresh,0))
        
        stWindow = wx.StaticText(self, label='Scan window (um)')
        fgsWidgetList.append((stWindow,0))
        self.tcWindow = wx.TextCtrl(self)
        self.tcWindow.SetValue(str(self.fineAlign.scanWindowSize))
        fgsWidgetList.append((self.tcWindow,0))
        
        fgsWidgetList.append((0,0))
        self.doneBtn = wx.Button(self, label='Done')
        self.doneBtn.Bind( wx.EVT_BUTTON, self.OnButton_Done)
        fgsWidgetList.append((self.doneBtn,0))        
        
        fgs.AddMany(fgsWidgetList)
        hbox.Add(fgs, 1, wx.EXPAND)
        self.SetSizer(hbox)
        self.Fit()
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
    def applySettings(self):
        detPriority = []
        for cb in self.cbList:
            cbSelection = cb.GetValue()
            if cbSelection != 'None':
                detIndex = self.cbOptions.index(cbSelection)
                print (detIndex)
                detPriority.append(detIndex)
        self.fineAlign.laserSlot = self.laserSlotCb.GetValue()
        self.fineAlign.laserPower = float(self.tcPower.GetValue())
        self.fineAlign.detectorPriority = detPriority
        self.fineAlign.wavelength = float(self.tcWavelength.GetValue())/1e9
        self.fineAlign.laserOutput = self.laserOutputMap[self.laserOutputCb.GetValue()]
        self.fineAlign.stepSize = float(self.tcStep.GetValue())
        self.fineAlign.threshold = float(self.tcThresh.GetValue())
        self.fineAlign.scanWindowSize = float(self.tcWindow.GetValue())
        self.fineAlign.numGradientIter = int(float(self.tcIter.GetValue()))

    def OnButton_Done(self, event):
        self.applySettings()
        self.Destroy()
                
    def OnClose(self, event):
        self.applySettings()
        self.Destroy()