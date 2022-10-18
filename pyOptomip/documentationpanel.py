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


class docPanel(wx.Panel):
    def __init__(self, parent):
        super(docPanel, self).__init__(parent)
        self.InitUI()

    def InitUI(self):
        sb = wx.StaticBox(self, label='Documentation')
        vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)

        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.instBtn = wx.Button(self, label='Instrument Information', size=(50, 20))
        self.hbox.Add(self.instBtn, 1, wx.EXPAND)
        self.instBtn.Bind(wx.EVT_BUTTON, self.instruments)

        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.tutorialBtn = wx.Button(self, label='Tutorials', size=(50, 20))
        self.hbox1.Add(self.tutorialBtn, 1, wx.EXPAND)
        self.tutorialBtn.Bind(wx.EVT_BUTTON, self.tutorials)

        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.tutorialBtn = wx.Button(self, label='pyOptomip User Guide', size=(50, 20))
        self.hbox1.Add(self.tutorialBtn, 1, wx.EXPAND)
        self.tutorialBtn.Bind(wx.EVT_BUTTON, self.userguide)

        vbox.AddMany([(self.hbox, 1, wx.EXPAND), (self.hbox1, 1, wx.EXPAND)])
        self.SetSizer(vbox)

    def instruments(self, event):
        pass

    def tutorials(self, event):
        pass

    def userguide(self, event):
        pass


