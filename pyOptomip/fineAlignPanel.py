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
from fineAlignSettings import fineAlignSettings
import traceback
from fineAlignDialog import fineAlignDialog

# Panel that appears in the Instrument Control widow which is used to control
# fine aligning.

class fineAlignPanel(wx.Panel):        
    def __init__(self, parent, fineAlign):
        super(fineAlignPanel, self).__init__(parent)
        
        self.fineAlign = fineAlign;
        self.InitUI()
        
    def InitUI(self):  
        sbOuter = wx.StaticBox(self, label='Fine align');
        vboxOuter = wx.StaticBoxSizer(sbOuter, wx.VERTICAL)
    
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        
        self.fineAlignBtn = wx.Button(self, label='Fine Align', size=(75, 20))
        
        hbox.Add(self.fineAlignBtn, proportion=0, border=0, flag=wx.EXPAND)
        self.fineAlignBtn.Bind(wx.EVT_BUTTON,self.OnButton_fineAlign)
        
        self.fineAlignSettingsBtn = wx.Button(self, label='Settings', size=(75, 20))
        
        hbox.Add(self.fineAlignSettingsBtn, proportion=0, border=0, flag=wx.EXPAND)
        self.fineAlignSettingsBtn.Bind(wx.EVT_BUTTON,self.OnButton_fineAlignSettings)
        
        vboxOuter.Add(hbox, proportion=0)

        self.SetSizer(vboxOuter)
        
    def OnButton_fineAlign(self, event):
        # Disable detector auto measurement
        self.fineAlign.laser.ctrlPanel.laserPanel.laserPanel.haltDetTimer()
        # Create the fine align dialog
        fineAlignDlg = fineAlignDialog(self, title='Fine align', size=(300,150))
        fineAlignDlg.runFineAlign(self.fineAlign)
        # Enable detector auto measurement
        self.fineAlign.laser.ctrlPanel.laserPanel.laserPanel.startDetTimer()
        #self.fineAlign.doFineAlign()
        
    
    def OnButton_fineAlignSettings(self, event):
        try:
            settingsDlg = fineAlignSettings(self, self.fineAlign)
        except Exception as e:
            dial = wx.MessageDialog(None, 'Could not initiate instrument control. '+traceback.format_exc(), 'Error', wx.ICON_ERROR)
            dial.ShowModal()
        settingsDlg.ShowModal()
        settingsDlg.Destroy()