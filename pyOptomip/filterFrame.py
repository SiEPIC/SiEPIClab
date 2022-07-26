import wx


class filterFrame(wx.Frame):

    def __init__(self, parent, devList):

        displaySize = wx.DisplaySize()
        super(filterFrame, self).__init__(parent, title='Filter',
                                          size=(displaySize[0] * 3 / 8.0, displaySize[1] * 2 / 4.0))

        self.TE = False
        self.TM = False
        self.thirteen = False
        self.fifteen = False
        self.keywords = set()
        self.deselect = set()

        self.devicesFilter = Filter(self.TE, self.TM, self.thirteen, self.fifteen, self.keywords, self.deselect)


        try:
            self.InitUI()
        except Exception as e:
            raise
        self.Centre()
        self.Show()

    def InitUI(self):
        self.Bind(wx.EVT_CLOSE, self.OnExitApp)

        mode = wx.StaticText(self, label='Mode')

        wavelength = wx.StaticText(self, label='Wavelength')

        keywords = wx.StaticText(self, label='Keywords')

        self.selTE = wx.CheckBox(self, label='TE', pos=(20, 20))
        self.selTE.SetValue(False)
        self.selTE.Bind(wx.EVT_CHECKBOX, self.devicesFilter.setTE)

        self.selTM = wx.CheckBox(self, label='TM', pos=(20, 20))
        self.selTM.SetValue(False)
        self.selTM.Bind(wx.EVT_CHECKBOX, self.devicesFilter.setTM)

        self.sel1310 = wx.CheckBox(self, label='1310nm', pos=(20, 20))
        self.sel1310.SetValue(False)
        self.sel1310.Bind(wx.EVT_CHECKBOX, self.devicesFilter.set1310)

        self.sel1550 = wx.CheckBox(self, label='1550nm', pos=(20, 20))
        self.sel1550.SetValue(False)
        self.sel1550.Bind(wx.EVT_CHECKBOX, self.devicesFilter.set1550)

        btnDone = wx.Button(self, label='Done', size=(50, 20))
        btnDone.Bind(wx.EVT_BUTTON, self.OnDone)

        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        hbox4.Add(btnDone, 1, wx.EXPAND)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.AddMany([(mode, 1, wx.EXPAND), (self.selTE, 1, wx.EXPAND), (self.selTM, 1, wx.EXPAND)])

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.AddMany([(wavelength, 1, wx.EXPAND), (self.sel1310, 1, wx.EXPAND), (self.sel1550, 1, wx.EXPAND)])

        self.keywordset = wx.TextCtrl(self)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        btnSelect = wx.Button(self, label='Select', size=(50, 20))
        btnSelect.Bind(wx.EVT_BUTTON, self.devicesFilter.selectWords(self.keywordset))
        btnUnSelect = wx.Button(self, label='Unselect', size=(50, 20))
        btnUnSelect.Bind(wx.EVT_BUTTON, self.devicesFilter.unselectWords(self.keywordset))
        hbox3.AddMany([(keywords, 1, wx.EXPAND), (self.keywordset, 1, wx.EXPAND), (btnSelect, 1, wx.EXPAND),
                       (btnUnSelect, 1, wx.EXPAND)])

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.AddMany([(hbox1, 1, wx.EXPAND), (hbox2, 1, wx.EXPAND), (hbox3, 0, wx.EXPAND), (hbox4, 0, wx.EXPAND)])

        self.SetSizer(vbox)

    def OnExitApp(self, event):
        self.Destroy()

    def OnDone(self, event):
        self.Destroy()



class Filter:

    def __init__(self, TE, TM, thirteen, fifteen, keywords, deselect):

        self.TE = TE
        self.TM = TM
        self.thirteen = thirteen
        self.fifteen = fifteen
        self.keywords = keywords
        self.deselect = deselect

    def setTE(self, event):
        self.TE = True

    def setTM(self, event):
        self.TM = True

    def set1310(self, event):
        self.thirteen = True

    def set1550(self, event):
        self.fifteen = True

    def selectWords(self, word):
        self.keywords.add(word.GetValue())

    def unselectWords(self, word):
        self.deselect.add(word.GetValue())
