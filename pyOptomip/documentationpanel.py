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
import wx.lib.agw.hyperlink as hl


class docPanel(wx.Panel):
    def __init__(self, parent):
        super(docPanel, self).__init__(parent)
        self.InitUI()

    def InitUI(self):
        sb = wx.StaticBox(self, label='Documentation')
        vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)

        panel = wx.Panel(self, -1)
        hyper1 = hl.HyperLinkCtrl(panel, -1, "Instrument Information", pos=(10, 30),
                                  URL="https://docs.google.com/presentation/d/1KjXZtnUT8MfvMXJach9sbHEPFBJqqyslEvHSfhG7LPA/edit?usp=sharing")
        hyper1.AutoBrowse(True)
        hyper1.SetColours("BLUE", "BLUE", "BLUE")
        hyper1.EnableRollover(True)
        hyper1.SetUnderlines(False, False, True)
        hyper1.SetBold(True)
        hyper1.OpenInSameWindow(True)
        hyper1.SetToolTip(wx.ToolTip("Hello World!"))
        hyper1.UpdateLink()
        #hbox1.Add(panel, 1, wx.EXPAND)

        panel2 = wx.Panel(self, -1)
        hyper2 = hl.HyperLinkCtrl(panel2, -1, "Tutorials", pos=(10, 30),
                                  URL="https://drive.google.com/drive/folders/18qO1LZOr10cQBIZJ2r6NZow1ixb2C_aS?usp=sharing")
        hyper2.AutoBrowse(True)
        hyper2.SetColours("BLUE", "BLUE", "BLUE")
        hyper2.EnableRollover(True)
        hyper2.SetUnderlines(False, False, True)
        hyper2.SetBold(True)
        hyper2.OpenInSameWindow(True)
        hyper2.SetToolTip(wx.ToolTip("Hello World!"))
        hyper2.UpdateLink()
        #hbox2.Add(panel2, 1, wx.EXPAND)

        panel3 = wx.Panel(self, -1)
        hyper3 = hl.HyperLinkCtrl(panel3, -1, "pyOptomip User Guide", pos=(10, 30),
                                  URL="https://docs.google.com/presentation/d/1rckUWbI42icnwsOZkhZT6LTTd9LnwFJXpcJrgnMYacI/edit?usp=sharing")
        hyper3.AutoBrowse(True)
        hyper3.SetColours("BLUE", "BLUE", "BLUE")
        hyper3.EnableRollover(True)
        hyper3.SetUnderlines(True, True, True)
        hyper3.SetBold(True)
        hyper3.OpenInSameWindow(True)
        hyper3.SetToolTip(wx.ToolTip("Hello World!"))
        hyper3.UpdateLink()
        #hbox3.Add(panel3, 1, wx.EXPAND)


        vbox.AddMany([(panel, 1, wx.EXPAND), (panel2, 1, wx.EXPAND), (panel3, 1, wx.EXPAND)])
        self.SetSizer(vbox)

    def instruments(self, event):

        print("Opening instrument information")
        panel = wx.Panel(self, -1)
        hyper2 = hl.HyperLinkCtrl(panel, -1, "wxPython Main Page", pos=(100, 100),
                                  URL="http://www.wxpython.org/")

        hyper2.AutoBrowse(False)
        hyper2.SetColours("BLUE", "BLUE", "BLUE")
        hyper2.EnableRollover(True)
        hyper2.SetUnderlines(False, False, True)
        hyper2.SetBold(True)
        hyper2.OpenInSameWindow(True)
        hyper2.SetToolTip(wx.ToolTip("Hello World!"))
        hyper2.UpdateLink()


        print("Instrument information opened")

    def tutorials(self, event):
        pass

    def userguide(self, event):
        pass


