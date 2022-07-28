import wx


class filterFrame(wx.Frame):

    def __init__(self, parent, checklist, deviceList):

        displaySize = wx.DisplaySize()
        super(filterFrame, self).__init__(parent, title='Filter',
                                          size=(displaySize[0] * 3 / 8.0, displaySize[1] * 2 / 4.0))

        self.TE = False
        self.TM = False
        self.thirteen = False
        self.fifteen = False
        self.keywords = set()
        self.deselect = set()

        self.checkList = checklist
        self.device_list = deviceList

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
        self.selTE.Bind(wx.EVT_CHECKBOX, self.OnSetTE)

        self.selTM = wx.CheckBox(self, label='TM', pos=(20, 20))
        self.selTM.SetValue(False)
        self.selTM.Bind(wx.EVT_CHECKBOX, self.OnSetTM)

        self.sel1310 = wx.CheckBox(self, label='1310nm', pos=(20, 20))
        self.sel1310.SetValue(False)
        self.sel1310.Bind(wx.EVT_CHECKBOX, self.OnSet1310)

        self.sel1550 = wx.CheckBox(self, label='1550nm', pos=(20, 20))
        self.sel1550.SetValue(False)
        self.sel1550.Bind(wx.EVT_CHECKBOX, self.OnSet1550)

        btnDone = wx.Button(self, label='Done', size=(50, 20))
        btnDone.Bind(wx.EVT_BUTTON, self.OnDone)

        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        hbox4.Add(btnDone, 1, wx.EXPAND)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.AddMany([(mode, 1, wx.EXPAND), (self.selTE, 1, wx.EXPAND), (self.selTM, 1, wx.EXPAND)])

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.AddMany([(wavelength, 1, wx.EXPAND), (self.sel1310, 1, wx.EXPAND), (self.sel1550, 1, wx.EXPAND)])

        self.keyword = wx.TextCtrl(self)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        btnSelect = wx.Button(self, label='Select', size=(50, 20))
        btnSelect.Bind(wx.EVT_BUTTON, self.OnSelect)
        btnUnSelect = wx.Button(self, label='Unselect', size=(50, 20))
        btnUnSelect.Bind(wx.EVT_BUTTON, self.OnDeSelect)
        hbox3.AddMany([(keywords, 1, wx.EXPAND), (self.keyword, 1, wx.EXPAND), (btnSelect, 1, wx.EXPAND),
                       (btnUnSelect, 1, wx.EXPAND)])

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.AddMany([(hbox1, 1, wx.EXPAND), (hbox2, 1, wx.EXPAND), (hbox3, 0, wx.EXPAND), (hbox4, 0, wx.EXPAND)])

        self.SetSizer(vbox)

    def OnExitApp(self, event):
        self.Destroy()

    def OnDone(self, event):

        if self.TE is True:
            for ii in range(self.checkList.GetItemCount()):
                if self.device_list[self.checkList.GetItemData(ii)].polarization == 'TE':
                    print('TE')
                    self.checkList.CheckItem(ii, True)
        else:
            for i in range(self.checkList.GetItemCount()):
                if self.device_list[self.checkList.GetItemData(i)].polarization == 'TE':
                    print('not TE')
                    self.checkList.CheckItem(i, False)

        if self.TM is True:
            for i in range(self.checkList.GetItemCount()):
                if self.device_list[self.checkList.GetItemData(i)].polarization == 'TM':
                    print('TM')
                    self.checkList.CheckItem(i, True)
        else:
            for i in range(self.checkList.GetItemCount()):
                if self.device_list[self.checkList.GetItemData(i)].polarization == 'TM':
                    print('not TM')
                    self.checkList.CheckItem(i, False)

        if self.thirteen is True:
            for i in range(self.checkList.GetItemCount()):
                if self.device_list[self.checkList.GetItemData(i)].polarization == 1310:
                    print(1310)
                    self.checkList.CheckItem(i, True)
        else:
            for i in range(self.checkList.GetItemCount()):
                if self.device_list[self.checkList.GetItemData(i)].polarization == 1310:
                    print('not 1310')
                    self.checkList.CheckItem(i, False)

        if self.fifteen is True:
            for i in range(self.checkList.GetItemCount()):
                if self.device_list[self.checkList.GetItemData(i)].polarization == 1550:
                    print('1550')
                    self.checkList.CheckItem(i, True)
        else:
            for i in range(self.checkList.GetItemCount()):
                if self.device_list[self.checkList.GetItemData(i)].polarization == 1550:
                    print('not 1550')
                    self.checkList.CheckItem(i, False)

        self.keywords.discard('')
        for select in self.keywords:
            print(select)
            for i in range(self.checkList.GetItemCount()):
                if select in str(self.device_list[self.checkList.GetItemData(i)].device_id):

                    self.checkList.CheckItem(i, True)

        self.deselect.discard('')
        for deselect in self.deselect:
            for i in range(self.checkList.GetItemCount()):
                if str(deselect) in str(self.device_list[self.checkList.GetItemData(i)].device_id):
                    print('uncheck words')
                    self.checkList.CheckItem(i, False)

        self.Destroy()

    def OnSetTE(self, event):

        self.TE = True

    def OnSetTM(self, event):

        self.TM = True

    def OnSet1310(self, event):

        self.thirteen = True

    def OnSet1550(self, event):

        self.fifteen = True

    def OnSelect(self, event):

        self.keywords.add(self.keyword.GetValue())

    def OnDeSelect(self, event):

        self.deselect.add(self.keyword.GetValue())
