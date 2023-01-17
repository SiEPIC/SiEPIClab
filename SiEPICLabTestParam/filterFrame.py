import wx


class filterFrame(wx.Frame):

    def __init__(self, parent, checklist, deviceList):
        """A frame which opens upon clicking the filter button within the auto-measure tab.
        Used to filter which devices are selected within a checklist of electro-optic devices"""
        displaySize = wx.DisplaySize()
        super(filterFrame, self).__init__(parent, title='Filter',
                                          size=(displaySize[0] * 3 / 8.0, displaySize[1] * 2 / 4.0))

        #initial status of the checklist
        self.TE = False
        self.TM = False
        self.routine = False
        self.thirteen = False
        self.fifteen = False
        self.keywords = set()
        self.deselect = set()
        self.devTypes = set()

        #Checklist object
        self.checkList = checklist
        #List of devices as ElectroOpticDevices
        self.device_list = deviceList

        try:
            self.InitUI()
        except Exception as e:
            raise
        self.Centre()
        self.Show()

    def InitUI(self):
        """Layout of the frame"""
        self.Bind(wx.EVT_CLOSE, self.OnExitApp)

        mode = wx.StaticText(self, label='Mode')

        wavelength = wx.StaticText(self, label='Wavelength')

        keywords = wx.StaticText(self, label='Keywords')

        devType = wx.StaticText(self, label='Device Type')

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

        self.selDeviceType = wx.ComboBox(self, size=(80, 20), choices=[], style=wx.CB_DROPDOWN)
        self.selDeviceType.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.on_drop_down)
        btnSelDev = wx.Button(self, label='Select', size=(50, 20))
        btnSelDev.Bind(wx.EVT_BUTTON, self.on_choose_device_type)
        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        hbox5.AddMany([(devType, 1, wx.EXPAND), (self.selDeviceType, 1, wx.EXPAND), (btnSelDev, 1, wx.EXPAND)])

        self.keyword = wx.TextCtrl(self)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        btnSelect = wx.Button(self, label='Select', size=(50, 20))
        btnSelect.Bind(wx.EVT_BUTTON, self.OnSelect)
        btnUnSelect = wx.Button(self, label='Unselect', size=(50, 20))
        btnUnSelect.Bind(wx.EVT_BUTTON, self.OnDeSelect)
        hbox3.AddMany([(keywords, 1, wx.EXPAND), (self.keyword, 1, wx.EXPAND), (btnSelect, 1, wx.EXPAND),
                       (btnUnSelect, 1, wx.EXPAND)])

        hbox3_5 = wx.BoxSizer(wx.HORIZONTAL)
        btnSelectRoutines = wx.Button(self, label='Select Devices with Routines', size=(100, 20))
        btnSelectRoutines.Bind(wx.EVT_BUTTON, self.OnSelectRoutines)
        hbox3_5.Add(btnSelectRoutines, 1, wx.EXPAND)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.AddMany([(hbox1, 1, wx.EXPAND), (hbox2, 1, wx.EXPAND), (hbox5, 0, wx.EXPAND), (hbox3, 0, wx.EXPAND),
                      (hbox3_5, 0, wx.EXPAND),(hbox4, 0, wx.EXPAND)])

        self.SetSizer(vbox)

    def OnExitApp(self, event):
        self.Destroy()

    def OnDone(self, event):
        """Filters devices in checklist before closing. If you wish to deselect a keyword, you must ensure
        to check at least one mode and at least one wavelength, otherwise nothing will be selected."""
        if self.TE is True:
            for ii in range(self.checkList.GetItemCount()):
                if self.device_list[self.checkList.GetItemData(ii)].polarization == 'TE':

                    self.checkList.CheckItem(ii, True)
                    if self.thirteen is True:
                        pass
                    else:
                        for i in range(self.checkList.GetItemCount()):
                            if self.device_list[self.checkList.GetItemData(i)].wavelength == 1310 and \
                                    self.device_list[self.checkList.GetItemData(i)].polarization == 'TE':
                                self.checkList.CheckItem(i, False)
                    if self.fifteen is True:
                        pass
                    else:
                        for i in range(self.checkList.GetItemCount()):
                            if self.device_list[self.checkList.GetItemData(i)].wavelength == 1550 and \
                                    self.device_list[self.checkList.GetItemData(i)].polarization == 'TE':
                                self.checkList.CheckItem(i, False)
        else:
            for i in range(self.checkList.GetItemCount()):
                if self.device_list[self.checkList.GetItemData(i)].polarization == 'TE':

                    self.checkList.CheckItem(i, False)

        if self.TM is True:
            for i in range(self.checkList.GetItemCount()):
                if self.device_list[self.checkList.GetItemData(i)].polarization == 'TM':

                    self.checkList.CheckItem(i, True)
                    if self.thirteen is True:
                        pass
                    else:
                        for i in range(self.checkList.GetItemCount()):
                            if self.device_list[self.checkList.GetItemData(i)].wavelength == 1310 and \
                                    self.device_list[self.checkList.GetItemData(i)].polarization == 'TM':
                                self.checkList.CheckItem(i, False)
                    if self.fifteen is True:
                        pass
                    else:
                        for i in range(self.checkList.GetItemCount()):
                            if self.device_list[self.checkList.GetItemData(i)].wavelength == 1550 and \
                                    self.device_list[self.checkList.GetItemData(i)].polarization == 'TM':
                                self.checkList.CheckItem(i, False)
        else:
            for i in range(self.checkList.GetItemCount()):
                if self.device_list[self.checkList.GetItemData(i)].polarization == 'TM':

                    self.checkList.CheckItem(i, False)

        self.devTypes.discard('')
        for select in self.devTypes:
            for i in range(self.checkList.GetItemCount()):
                if select == str(self.device_list[self.checkList.GetItemData(i)].getDeviceType()):
                    self.checkList.CheckItem(i, True)


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

                    self.checkList.CheckItem(i, False)

        if self.routine:
            for i in range(self.checkList.GetItemCount()):
                if self.device_list[self.checkList.GetItemData(i)].hasRoutines:
                    self.checkList.CheckItem(i, True)

        self.Destroy()

    def OnSetTE(self, event):
        """When the TE box is checked"""
        self.TE = True

    def OnSetTM(self, event):
        """When the TM box is checked"""
        self.TM = True

    def OnSet1310(self, event):
        """When the 1310nm box is checked"""
        self.thirteen = True

    def OnSet1550(self, event):
        """When the 1550nm box is checked"""
        self.fifteen = True

    def OnSelect(self, event):
        """Adds the word typed in to the textctrl object to a set of words to select"""
        self.keywords.add(self.keyword.GetValue())

    def OnDeSelect(self, event):
        """Adds the word typed in to the textctrl object to a set of words to deselect"""
        self.deselect.add(self.keyword.GetValue())

    def on_drop_down(self, event):
        """Populates drop down menu with types of devices used in layout"""
        devTypes = set()
        for device in self.device_list:
            devTypes.add(device.getDeviceType())
        for type_ in devTypes:
            self.selDeviceType.Append(type_)

    def on_choose_device_type(self, event):
        """Adds selected device type to a list containing the type of devices to select"""
        self.devTypes.add(self.selDeviceType.GetValue())

    def OnSelectRoutines(self, event):
        self.routine = True