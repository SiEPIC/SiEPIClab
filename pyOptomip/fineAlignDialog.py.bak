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

# Dialog box that appears while running a fine align.
class fineAlignDialog(wx.Dialog):

    def __init__(self, *args, **kw):
        super(fineAlignDialog, self).__init__(*args, **kw) 
        self.InitUI()
        
    def InitUI(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        st1 = wx.StaticText(self, label='Performing fine align...')
        
        vbox.Add(st1, proportion=0, flag=wx.ALIGN_CENTRE)

        
        self.stopBtn = wx.Button(self, wx.ID_STOP)
        self.stopBtn.Bind( wx.EVT_BUTTON, self.OnButton_Stop)
        vbox.Add(self.stopBtn, proportion=0, flag=wx.ALIGN_CENTRE)
        
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.SetSizerAndFit(vbox)
        
    def OnClose(self, event):
        self.fineAlign.abort = True
        

    def runFineAlign(self, fineAlign):
        self.fineAlign = fineAlign
        self.exception = None
        startWorker(self.fineAlignDoneCb, self.doFineAlign, wargs=[fineAlign])
        self.ShowModal()
        
        
    def doFineAlign(self,fineAlign):
        try:
            fineAlign.abort = False
            fineAlign.doFineAlign()
        except Exception as e:
            self.exception = e
            
    def fineAlignDoneCb(self,result):
        result.get()
        if self.exception:
            print self.exception
        self.fineAlign.abort = False
        self.Destroy()
            
        
    def OnButton_Stop(self,event):
        self.fineAlign.abort = True
        
        
        