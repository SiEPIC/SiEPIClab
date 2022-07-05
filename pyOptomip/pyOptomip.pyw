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

import  wx
from instrumentFrame import instrumentFrame
import traceback
from CorvusEcoParameters import CorvusEcoParameters
from MGMotorParameters import MGMotorParameters
from hp816x_N77Det_instrParameters import hp816x_N77Det_instrParameters
from hp816x_instrParameters import hp816x_instrParameters
from dummyLaserParameters import dummyLaserParameters
from SMUParameters import SMUParameters
from outputlogPanel import outputlogPanel
from logWriter import logWriter,logWriterError
import sys
import pyvisa as visa
from instrumentFrame_withtabs import instrumentFrame_withtabs

softwareVersion = "1.1"

devTypes = [CorvusEcoParameters, MGMotorParameters, \
            hp816x_N77Det_instrParameters, hp816x_instrParameters, \
            QontrolMotorParameters, \SMUParameters]
        
class ConnectCB(wx.Choicebook):
    def __init__(self, parent, id, connectPanel):
        wx.Choicebook.__init__(self, parent, id)
        self.connectPanel = connectPanel
        # Reduce load time by getting VISA addresses here and passing them to each panel
        rm = visa.ResourceManager()
        visaAddrLst = rm.list_resources()
        for c in devTypes:
            win = wx.Panel(self)
            vbox = wx.BoxSizer(wx.VERTICAL)
            inst_panel = c(win,self.connectPanel, visaAddrLst = visaAddrLst)
            vbox.Add(inst_panel, proportion=1, flag=wx.EXPAND)
            win.SetSizer(vbox)
            self.AddPage(win, c.name)

class pyOptomip(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          "Connect instruments",
                          size=(600,400))
        self.panel = wx.Panel(self)
        self.panel.instList = []
        notebook = ConnectCB(self.panel,-1, self.panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 2, wx.ALL|wx.EXPAND, 5)
        self.doneButton = wx.Button(self.panel, label='Done', size=(75, 20))
        self.doneButton.Bind( wx.EVT_BUTTON, self.OnButton_Done)
        sizer.Add(self.doneButton, 0, wx.ALIGN_RIGHT|wx.ALL)
         
        self.log = outputlogPanel(self.panel)
        sizer.Add(self.log, 1, wx.ALL|wx.EXPAND)
        self.panel.SetSizer(sizer)
        sys.stdout = logWriter(self.log)
        sys.stderr = logWriterError(self.log)
        print("This is pyOptomip version "+softwareVersion)
        self.Layout()
        
        self.Show()

    
    def OnButton_Done(self, event):
        self.createInstrumentFrame();
        self.Destroy();

    def createInstrumentFrame(self):
        try:
            instrumentFrame_withtabs(None, self.panel.instList)
            #instrumentFrame(None, self.panel.instList)
        except Exception as e:
            dial = wx.MessageDialog(None, 'Could not initiate instrument control. '+traceback.format_exc(), 'Error', wx.ICON_ERROR)
            dial.ShowModal()
    
if __name__ == '__main__':
    app = wx.App(redirect=False)
    pyOptomip()
    app.MainLoop()
    app.Destroy()
    del app
    
