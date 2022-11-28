
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
import os
import wx
import re
import yaml
from outputlogPanel import outputlogPanel
from logWriter import logWriter, logWriterError
import sys
from ElectroOpticDevice import ElectroOpticDevice


class testParameters(wx.Frame):

    def __init__(self):

        displaySize = wx.DisplaySize()
        super(testParameters, self).__init__(None, title='Instrument Control', size=(int(displaySize[0] * 5 / 8.0), int(displaySize[1] * 3 / 4.0)))
        try:
            self.InitUI()
        except Exception as e:
            self.Destroy()
            raise
        self.Centre()
        self.Show()


    def InitUI(self):
        """
        Creates the highest level formatting for the testing parameters frame
        Returns
        -------

        """
        self.Bind(wx.EVT_CLOSE, self.OnExitApp)
        vbox = wx.BoxSizer(wx.VERTICAL)
        panel = TopPanel(self)
        vbox.Add(panel, proportion=1, border=0, flag=wx.EXPAND)
        self.log = outputlogPanel(self)
        vbox.Add(self.log, 1, wx.EXPAND)
        self.SetSizer(vbox)
        sys.stdout = logWriter(self.log)
        sys.stderr = logWriterError(self.log)


    def OnExitApp(self, event):
        """
        Terminates the window on close
        Parameters
        ----------
        event :

        Returns
        -------

        """
        self.Destroy()


# Panel which contains the panels used for controlling the laser and detectors. It also
# contains the graph.
class TopPanel(wx.Panel):

    def __init__(self, parent, automeasurePanel):
        super(TopPanel, self).__init__(parent)
        self.routineflag = ""
        self.setpanel = SetPanel(self)#BlankPanel(self)
        self.instructpanel = InstructPanel(self, self.setpanel)
        self.autoMeasurePanel = automeasurePanel
        self.autoMeasure = automeasurePanel.autoMeasure
        self.selected = []
        self.retrievedataselected = []
        self.setflag = False
        self.highlightchecked = []
        self.beginning = False
        self.end = False
        self.routinenum = 0
        self.retrievedataflag = False
        self.deviceListset = []
        self.data = {'index': [], 'device': [], 'ELECflag': [], 'OPTICflag': [], 'setwflag': [], 'setvflag': [], 'Voltsel': [],
                     'Currentsel': [], 'VoltMin': [], 'VoltMax': [], 'CurrentMin': [], 'CurrentMax': [],
                     'VoltRes': [], 'CurrentRes': [], 'IV': [], 'RV': [], 'PV': [], 'ChannelA': [], 'ChannelB': [],
                     'Start': [], 'Stop': [], 'Stepsize': [], 'Sweeppower': [], 'Sweepspeed': [], 'Laseroutput': [],
                     'Numscans': [], 'InitialRange': [], 'RangeDec': [] ,'setwVoltsel': [],'setwCurrentsel': [],
                     'setwVoltMin': [], 'setwVoltMax': [], 'setwCurrentMin': [], 'setwCurrentMax': [],
                     'setwVoltRes': [], 'setwCurrentRes': [], 'setwIV': [], 'setwRV': [], 'setwPV': [],
                     'setwChannelA': [], 'setwChannelB': [], 'Wavelengths': [], 'setvStart': [], 'setvStop': [],
                     'setvStepsize': [], 'setvSweeppower': [], 'setvSweepspeed': [], 'setvLaseroutput': [],
                     'setvNumscans': [], 'setvInitialRange': [], 'setvRangeDec': [], 'setvChannelA': [],
                     'setvChannelB': [], 'Voltages': [], 'RoutineNumber': [], 'Wavelength': [], 'Polarization': [], 'Opt x': [], 'Opt y': [], 'type': [], 'Elec x': [], 'Elec y': []}
        #self.autoMeasurePanel = automeasurePanel
        self.InitUI()


    def InitUI(self):

        sbOuter = wx.StaticBox(self, label='Test Parameter Creation')
        vboxOuter = wx.StaticBoxSizer(sbOuter, wx.VERTICAL)

        #Coordinate file select
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.coordFileTb = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.coordFileTb.SetValue('No file selected')
        self.coordFileSelectBtn = wx.Button(self, wx.ID_OPEN, size=(50, 20))
        self.coordFileSelectBtn.Bind(wx.EVT_BUTTON, self.OnButton_ChooseCoordFile)
        hbox.AddMany([(self.coordFileTb, 1, wx.EXPAND), (self.coordFileSelectBtn, 0, wx.EXPAND)])

        #select all button, unselect all button, select keyword button, unselect keyword button, retreive data button
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.checkAllBtn = wx.Button(self, label='Select All', size=(80, 20))
        self.checkAllBtn.Bind(wx.EVT_BUTTON, self.OnButton_CheckAll)
        self.uncheckAllBtn = wx.Button(self, label='Unselect All', size=(80, 20))
        self.uncheckAllBtn.Bind(wx.EVT_BUTTON, self.OnButton_UncheckAll)
        self.searchFile = wx.TextCtrl(self)
        self.searchFile.SetValue('')
        self.searchFile.Bind(wx.EVT_TEXT, self.highlight)
        self.searchBtn = wx.Button(self, label='Select keyword', size=(100, 20))
        self.searchBtn.Bind(wx.EVT_BUTTON, self.SearchDevices)
        self.unsearchBtn = wx.Button(self, label='Unselect keyword', size=(100, 20))
        self.unsearchBtn.Bind(wx.EVT_BUTTON, self.unSearchDevices)
        self.retrievedataBtn = wx.Button(self, label='Retrieve Data', size=(100, 20))
        self.retrievedataBtn.Bind(wx.EVT_BUTTON, self.retrievedata)
        self.indicator = wx.StaticText(self, label='')
        self.printbtn = wx.Button(self, label='Print data', size=(100, 20))
        self.printbtn.Bind(wx.EVT_BUTTON, self.printdata)
        hbox2.AddMany([(self.checkAllBtn, 0, wx.EXPAND), (self.uncheckAllBtn, 0, wx.EXPAND), (self.searchFile, 0, wx.EXPAND), (self.searchBtn, 0, wx.EXPAND), (self.unsearchBtn, 0, wx.EXPAND), (self.printbtn, 0, wx.EXPAND), (self.retrievedataBtn, 0, wx.EXPAND), (self.indicator, 0, wx.EXPAND)])

        #create checklist
        self.checkList = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        self.checkList.InsertColumn(0, 'Device', width=100)
        self.checkList.Bind(wx.EVT_LIST_ITEM_CHECKED, self.checkListchecked)
        self.checkList.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.checkListunchecked)
        vboxdevices = wx.BoxSizer(wx.VERTICAL)
        vboxdevices.AddMany([(self.checkList, 0, wx.EXPAND), (self.instructpanel, 0, wx.EXPAND)])

        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        hbox5.Add(self.setpanel, 0, wx.EXPAND)

        #create output folder selection box
        hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(self, label='Save folder:')
        self.outputFolderTb = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.outputFolderBtn = wx.Button(self, wx.ID_OPEN, size=(50, 20))
        self.outputFolderBtn.Bind(wx.EVT_BUTTON, self.OnButton_SelectOutputFolder)
        hbox6.AddMany([(st2, 1, wx.EXPAND), (self.outputFolderTb, 1, wx.EXPAND), (self.outputFolderBtn, 0, wx.EXPAND)])

        #set button, import button and export button
        hbox7 = wx.BoxSizer(wx.HORIZONTAL)
        self.setBtn = wx.Button(self, label='Set', size=(50, 20))
        self.setBtn.Bind(wx.EVT_BUTTON, self.SetButton)
        self.importBtn = wx.Button(self, label='Import', size=(50, 20))
        self.importBtn.Bind(wx.EVT_BUTTON, self.ImportButton)
        self.exportBtn = wx.Button(self, label='Export', size=(50, 20))
        self.exportBtn.Bind(wx.EVT_BUTTON, self.ExportButton)
        hbox7.AddMany([(self.setBtn, 0, wx.EXPAND), (self.importBtn, 0, wx.EXPAND), (self.exportBtn, 0, wx.EXPAND)])

        hboxouter = wx.BoxSizer(wx.HORIZONTAL)
        hboxouter.AddMany([(vboxdevices, 1 , wx.EXPAND), (hbox5, 0, wx.EXPAND)])
        #put it all together
        vboxOuter.AddMany([(hbox, 0, wx.EXPAND), (hbox2, 0, wx.EXPAND), (hboxouter, 0, wx.EXPAND),
                           (hbox6, 0, wx.ALIGN_LEFT), (hbox7, 0, wx.ALIGN_RIGHT)])


        self.SetSizer(vboxOuter)


    def printdata(self, event):

        for keys, values in self.data.items():
            print(keys)
            print(values)


    def OnButton_ChooseCoordFile(self, event):
        """
        When event is triggered this function opens the chosen coordinate file and displays the devices in a checklist
        Parameters
        ----------
        event : the event triggered by clicking the open button to choose the auto-coordinate file

        Returns
        -------

        """

        """ Opens a file dialog to select a coordinate file. """
        fileDlg = wx.FileDialog(self, "Open", "", "",
                                "Text Files (*.txt)|*.txt",
                                wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        fileDlg.ShowModal()
        self.filter = []
        self.coordFileTb.SetValue(fileDlg.GetFilenames()[0])
        # fileDlg.Destroy()
        self.autoMeasure.readCoordFile(fileDlg.GetPath())
        global deviceListAsObjects
        deviceListAsObjects = self.autoMeasure.devices
        self.device_list = deviceListAsObjects
        global deviceList
        deviceList = []
        for device in deviceListAsObjects:
            deviceList.append(device.getDeviceID())
        # Adds items to the check list
        self.checkList.DeleteAllItems()
        for ii, device in enumerate(deviceList):
            self.checkList.InsertItem(ii, device)
            for dev in deviceListAsObjects:
                if dev.getDeviceID() == device:
                    index = deviceListAsObjects.index(dev)  # Stores index of device in list
            self.checkList.SetItemData(ii, index)
        self.checkList.SortItems(self.checkListSort)  # Make sure items in list are sorted
        self.checkList.EnableCheckBoxes()
        self.set = [False] * self.checkList.GetItemCount()

       # for ii in range(self.checkList.GetItemCount()):
            #self.data['index'] = ii
        self.devicedict = {}
        for dev in deviceList:
            self.devicedict[dev] = {}
            self.devicedict[dev]['index'] = []
            self.devicedict[dev]['ELECflag'] = []
            self.devicedict[dev]['OPTICflag'] = []
            self.devicedict[dev]['setwflag'] = []
            self.devicedict[dev]['setvflag'] = []
            self.devicedict[dev]['Voltsel'] = []
            self.devicedict[dev]['Currentsel'] = []
            self.devicedict[dev]['VoltMin'] = []
            self.devicedict[dev]['VoltMax'] = []
            self.devicedict[dev]['CurrentMin'] = []
            self.devicedict[dev]['CurrentMax'] = []
            self.devicedict[dev]['VoltRes'] = []
            self.devicedict[dev]['CurrentRes'] = []
            self.devicedict[dev]['IV'] = []
            self.devicedict[dev]['RV'] = []
            self.devicedict[dev]['PV'] = []
            self.devicedict[dev]['ChannelA'] = []
            self.devicedict[dev]['ChannelB'] = []
            self.devicedict[dev]['Start'] = []
            self.devicedict[dev]['Stop'] = []
            self.devicedict[dev]['Stepsize'] = []
            self.devicedict[dev]['Sweeppower'] = []
            self.devicedict[dev]['Sweepspeed'] = []
            self.devicedict[dev]['Laseroutput'] = []
            self.devicedict[dev]['Numscans'] = []
            self.devicedict[dev]['InitialRange'] = []
            self.devicedict[dev]['RangeDec'] = []
            self.devicedict[dev]['setwVoltsel'] = []
            self.devicedict[dev]['setwCurrentsel'] = []
            self.devicedict[dev]['setwVoltMin'] = []
            self.devicedict[dev]['setwVoltMax'] = []
            self.devicedict[dev]['setwCurrentMin'] = []
            self.devicedict[dev]['setwCurrentMax'] = []
            self.devicedict[dev]['setwVoltRes'] = []
            self.devicedict[dev]['setwCurrentRes'] = []
            self.devicedict[dev]['setwIV'] = []
            self.devicedict[dev]['setwRV'] = []
            self.devicedict[dev]['setwPV'] = []
            self.devicedict[dev]['setwChannelA'] = []
            self.devicedict[dev]['setwChannelB'] = []
            self.devicedict[dev]['Wavelengths'] = []
            self.devicedict[dev]['setvStart'] = []
            self.devicedict[dev]['setvStop'] = []
            self.devicedict[dev]['setvStepsize'] = []
            self.devicedict[dev]['setvSweeppower'] = []
            self.devicedict[dev]['setvSweepspeed'] = []
            self.devicedict[dev]['setvLaseroutput'] = []
            self.devicedict[dev]['setvNumscans'] = []
            self.devicedict[dev]['setvInitialRange'] = []
            self.devicedict[dev]['setvRangeDec'] = []
            self.devicedict[dev]['setvChannelA'] = []
            self.devicedict[dev]['setvChannelB'] = []
            self.devicedict[dev]['Voltages'] = []
            self.devicedict[dev]['RoutineNumber'] = []
            self.devicedict[dev]['Wavelength'] = []
            self.devicedict[dev]['Polarization'] = []
            self.devicedict[dev]['Opt x'] = []
            self.devicedict[dev]['Opt y'] = []
            self.devicedict[dev]['type'] = []
            self.devicedict[dev]['Elec x'] = []
            self.devicedict[dev]['Elec y'] = []

        for dev in self.device_list:
            self.filter.append(self.devicedict[dev.getDeviceID()]['DeviceID'])
            self.devicedict[dev.getDeviceID()]['Wavelength'].append(dev.getDeviceWavelength())
            self.devicedict[dev.getDeviceID()]['Polarization'].append(dev.getDevicePolarization())
            self.devicedict[dev.getDeviceID()]['Opt x'].append(dev.getOpticalCoordinates()[0])
            self.devicedict[dev.getDeviceID()]['Opt y'].append(dev.getOpticalCoordinates()[1])
            self.devicedict[dev.getDeviceID()]['type'].append(dev.getDeviceType())
            if dev.getElectricalCoordinates():
                self.devicedict[dev.getDeviceID()]['Elec x'].append(dev.getElectricalCoordinates()[0][1])
                self.devicedict[dev.getDeviceID()]['Elec y'].append(dev.getElectricalCoordinates()[0][2])
            else:
                self.devicedict[dev.getDeviceID()]['Elec x'].append(0)
                self.devicedict[dev.getDeviceID()]['Elec y'].append(0)


        global fileLoaded
        fileLoaded = True
        self.Refresh()


    def OnButton_CheckAll(self, event):
        """
        Checks all the devices in the checklist, will not check the devices that have already been set
        Parameters
        ----------
        event : the event triggered when the select all button is pushed

        Returns
        -------

        """

        if self.retrievedataflag == False:
            for ii in range(self.checkList.GetItemCount()):
                if self.set[ii] == False:
                    self.checkList.CheckItem(ii, True)
        else:
            return


    def retrievedata(self, event):
        """
        configures the switch from set data mode to retrieve data mode by setting or unsetting various flags
        Parameters
        ----------
        event : the event triggered when the user presses the retrieve data button

        Returns
        -------

        """

        if self.retrievedataflag == False:
            print("Entering routine extraction mode")
            self.indicator.SetLabel('Retrieve Data Mode')
            self.retrievedataflag = True
            self.beginning = True
            for c in self.selected:
                self.checkList.CheckItem(c, False)
            self.beginning = False
            return

        self.end = True
        for c in self.retrievedataselected:
            self.checkList.CheckItem(c, False)

        for c in self.selected:
            self.checkList.CheckItem(c, True)
        self.end = False

        self.highlightchecked = []
        self.retrievedataselected = []

        for x in range(self.checkList.GetItemCount()):
            self.checkList.SetItemBackgroundColour(x, wx.Colour(255, 255, 255))


        self.indicator.SetLabel('')
        self.retrievedataflag = False
        print("Exiting routine extraction mode")

        #self.retrievedataselected
        #for c in self.set


    def OnButton_UncheckAll(self, event):
        """
        Uncheck all items in the checklist
        Parameters
        ----------
        event : the event triggered by pressing the unselect all button

        Returns
        -------

        """

        for ii in range(self.checkList.GetItemCount()):
            self.checkList.CheckItem(ii, False)


    def highlight(self, event):
        """
        Highlights the items in the checklist that contain the string in the searchfile textctrl box
        Parameters
        ----------
        event : the event triggered by pressing the select keyword button

        Returns
        -------

        """

        for c in range(self.checkList.GetItemCount()):
            if self.set[c] != True and self.searchFile.GetValue() != None and self.searchFile.GetValue() in self.checkList.GetItemText(c, 0):
                self.checkList.SetItemBackgroundColour(c, wx.Colour(255, 255, 0))
            else:
                self.checkList.SetItemBackgroundColour(c, wx.Colour(255,255,255))

            if self.searchFile.GetValue() == '':
                self.checkList.SetItemBackgroundColour(c, wx.Colour(255,255,255))


    def retrievehighlight(self, index):
        """
        When an item is selected while in retrieve data mode this function highlights all the items that have the same
        routine (routine similarity is based on when the routine was originally set, not whether of not the routines are
        numerically the same)
        Parameters
        ----------
        index : the index of the checklist device chosen while in retrieve data mode

        Returns
        -------

        """

        flag = False
        if self.set[index] == True:
            flag = True

        if flag == False:
            return

        num = []
        for d in self.highlightchecked:
            for a in range(len(self.data['index'])):
                if self.data['index'][a] == d:
                    num.append(a)

        for d in range(len(num)):
            if self.data['RoutineNumber'][num[d]] != self.data['RoutineNumber'][index]:
                return

        self.highlightchecked.append(index)



        for c in range(len(self.data['RoutineNumber'])):
            if self.data['RoutineNumber'][c] == self.data['RoutineNumber'][index]:
                d = self.data['index'][c]
                self.checkList.SetItemBackgroundColour(d, wx.Colour(255, 255, 0))


    def retrieveunhighlight(self, index):
        """
        When the device that was previosuly selected becomes unselected this function unhighlights all similar routine devices
        Parameters
        ----------
        index : the index of the checklist device being unselected

        Returns
        -------

        """

        num = []
        for d in self.highlightchecked:
            for a in range(len(self.data['index'])):
                if self.data['index'][a] == d:
                    num.append(a)

        for d in range(len(num)):
            if self.data['RoutineNumber'][num[d]] != self.data['RoutineNumber'][index]:
                return

        self.highlightchecked.remove(index)

        if self.highlightchecked == []:
            for c in range(len(self.data['RoutineNumber'])):
                if self.data['RoutineNumber'][c] == self.data['RoutineNumber'][index]:
                    d = self.data['index'][c]
                    self.checkList.SetItemBackgroundColour(d, wx.Colour(255, 255, 255))


    def SearchDevices(self, event):
        """
        When the search devices button is clicked this function selects all devices in the checklist that contain the string in searchfile textctrl box
        Parameters
        ----------
        event : the event triggered by pressing the search keyword button

        Returns
        -------

        """

        for c in range(len(self.set)):
            if self.set[c] != True and self.searchFile.GetValue() != '' and self.searchFile.GetValue() in self.checkList.GetItemText(c, 0):
                self.checkList.CheckItem(c, True)


    def unSearchDevices(self, event):
        """
        Unselects all devices in checklist that contain the string in searchfile textctrl box
        Parameters
        ----------
        event : the event triggered on pressing the unselect keyword button

        Returns
        -------

        """

        for c in range(len(self.set)):
            if self.set[c] != True and self.searchFile.GetValue() != '' and self.searchFile.GetValue() in self.checkList.GetItemText(c, 0):
                self.checkList.CheckItem(c, False)


    def checkListSort(self, item1, item2):
        """
        Sorts two items passed to it, used to sort the items in the checklist on creation
        Parameters
        ----------
        item1 : integer value
        item2 : integer value

        Returns
        -------
        A -1, a 1 or a 0 depending on the size of the items

        """
        # Items are the client data associated with each entry
        if item2 < item2:
            return -1
        elif item1 > item2:
            return 1
        else:
            return 0


    def checkListchecked(self, event):
        """
        If in set data mode this function adds the now checked device to a list of selected devices, if in retrieve
        data mode this function calls reteivedataswap beginning the data reteival process for the device in quuestion
        Parameters
        ----------
        event : the event triggered by selecting a device in the list

        Returns
        -------

        """
        c = event.GetIndex()

        if self.retrievedataflag == False:
            self.selected.append(c)
        elif self.end == True:
            pass
        elif self.retrievedataflag == True:
            if len(self.retrievedataselected) >= 1:
                print("You may only select one device at a time while in retrieve data mode")
                self.checkList.CheckItem(c, False)
            else:
                self.retrievedataswap(c)
            #self.retrievehighlight(c)


    def retrievedataswap(self, c):
        """
        Swaps the data in the parameters menu to that of the selected device when in retrieve data mode
        Parameters
        ----------
        c : the index of the selected device in the checklist

        Returns
        -------

        """

        self.retrievedataselected.append(c)

        #if self.set[c] == False:
           # print('Please select a preset device')
           # self.checkList.CheckItem(c, False)
           # return

        number = []

        for d in range(len(self.data['device'])):

            print(self.data['device'][d])
            print(self.checkList.GetItemText(c, 0))

            if self.data['device'][d] == self.checkList.GetItemText(c, 0):
                number.append(d)

        print(number)

        ELECcount = 0
        OPTcount = 0
        SETWcount = 0
        SETVcount = 0
        suborder = []
        order = []

        for q in number:

            if self.data['ELECflag'][q] == 'True' or self.data['ELECflag'][q] == True:
                ELECcount = ELECcount + 1
                suborder.append('ELEC')
            if self.data['OPTICflag'][q] == 'True' or self.data['OPTICflag'][q] == True:
                OPTcount = OPTcount + 1
                suborder.append('OPTIC')
            if self.data['setvflag'][q] == 'True' or self.data['setvflag'][q] == True:
                SETVcount = SETVcount + 1
                suborder.append('SETV')
            if self.data['setwflag'][q] == 'True' or self.data['setwflag'][q] == True:
                SETWcount = SETWcount + 1
                suborder.append('SETW')
            attach = suborder
            order.append(attach)
            suborder = []

        print(ELECcount)
        print(OPTcount)
        print(SETWcount)
        print(SETVcount)

        print(order)

        self.instructpanel.elecroutine.SetValue(str(ELECcount))
        self.instructpanel.optroutine.SetValue(str(OPTcount))
        self.instructpanel.setvroutine.SetValue(str(SETVcount))
        self.instructpanel.setwroutine.SetValue(str(SETWcount))

        elecoptions = []
        optoptions = []
        setvoptions = []
        setwoptions = []

        if ELECcount != '' and ELECcount != '0':
            for x in range(int(ELECcount)):
                x = x + 1
                elecoptions.append(str(x))

        if OPTcount != '' and OPTcount != '0':
            for x in range(int(OPTcount)):
                x = x + 1
                optoptions.append(str(x))

        if SETVcount != '' and SETVcount != '0':
            for x in range(int(SETVcount)):
                x = x + 1
                setvoptions.append(str(x))

        if SETWcount != '' and SETWcount != '0':
            options = []
            for x in range(int(SETWcount)):
                x = x + 1
                setwoptions.append(str(x))

        # Electrical set#############################################################################################
        self.setpanel.routineselectelec.SetItems(elecoptions)
        self.setpanel.elecvolt = [''] * int(ELECcount)
        self.setpanel.eleccurrent = [''] * int(ELECcount)
        self.setpanel.elecvmax = [''] * int(ELECcount)
        self.setpanel.elecvmin = [''] * int(ELECcount)
        self.setpanel.elecimin = [''] * int(ELECcount)
        self.setpanel.elecimax = [''] * int(ELECcount)
        self.setpanel.elecires = [''] * int(ELECcount)
        self.setpanel.elecvres = [''] * int(ELECcount)
        self.setpanel.eleciv = [''] * int(ELECcount)
        self.setpanel.elecrv = [''] * int(ELECcount)
        self.setpanel.elecpv = [''] * int(ELECcount)
        self.setpanel.elecchannelA = [''] * int(ELECcount)
        self.setpanel.elecchannelB = [''] * int(ELECcount)
        self.setpanel.elecflagholder = [''] * int(ELECcount)

        # Optical set################################################################################################
        self.setpanel.routineselectopt.SetItems(optoptions)
        self.setpanel.start = [''] * int(OPTcount)
        self.setpanel.stop = [''] * int(OPTcount)
        self.setpanel.step = [''] * int(OPTcount)
        self.setpanel.sweeppow = [''] * int(OPTcount)
        self.setpanel.sweepsped = [''] * int(OPTcount)
        self.setpanel.laserout = [''] * int(OPTcount)
        self.setpanel.numscans = [''] * int(OPTcount)
        self.setpanel.initialran = [''] * int(OPTcount)
        self.setpanel.rangedecre = [''] * int(OPTcount)
        self.setpanel.opticflagholder = [''] * int(OPTcount)

        # Setw set###################################################################################################
        self.setpanel.routineselectsetw.SetItems(setwoptions)
        self.setpanel.setwvolt = [''] * int(SETWcount)
        self.setpanel.setwcurrent = [''] * int(SETWcount)
        self.setpanel.setwvmax = [''] * int(SETWcount)
        self.setpanel.setwvmin = [''] * int(SETWcount)
        self.setpanel.setwimin = [''] * int(SETWcount)
        self.setpanel.setwimax = [''] * int(SETWcount)
        self.setpanel.setwires = [''] * int(SETWcount)
        self.setpanel.setwvres = [''] * int(SETWcount)
        self.setpanel.setwiv = [''] * int(SETWcount)
        self.setpanel.setwrv = [''] * int(SETWcount)
        self.setpanel.setwpv = [''] * int(SETWcount)
        self.setpanel.setwchannelA = [''] * int(SETWcount)
        self.setpanel.setwchannelB = [''] * int(SETWcount)
        self.setpanel.setwwavelengths = [''] * int(SETWcount)
        self.setpanel.setwflagholder = [''] * int(SETWcount)

        # setv set###################################################################################################
        self.setpanel.routineselectsetv.SetItems(setvoptions)
        self.setpanel.setvstart = [''] * int(SETVcount)
        self.setpanel.setvstop = [''] * int(SETVcount)
        self.setpanel.setvstep = [''] * int(SETVcount)
        self.setpanel.setvsweeppow = [''] * int(SETVcount)
        self.setpanel.setvsweepsped = [''] * int(SETVcount)
        self.setpanel.setvlaserout = [''] * int(SETVcount)
        self.setpanel.setvnumscans = [''] * int(SETVcount)
        self.setpanel.setvinitialran = [''] * int(SETVcount)
        self.setpanel.setvrangedecre = [''] * int(SETVcount)
        self.setpanel.setvchannelA = [''] * int(SETVcount)
        self.setpanel.setvchannelB = [''] * int(SETVcount)
        self.setpanel.setvvoltages = [''] * int(SETVcount)
        self.setpanel.setvflagholder = [''] * int(SETVcount)

        electracker = 0
        opttracker = 0
        setvtracker = 0
        setwtracker = 0
        tracker = 0

        for d in order:
            for a in d:

                if a == 'ELEC':
                    if self.data['Voltsel'][number[tracker]] == 'True':
                        self.data['Voltsel'][number[tracker]] = True
                    if self.data['Voltsel'][number[tracker]] == 'False':
                        self.data['Voltsel'][number[tracker]] = False
                    self.setpanel.elecvolt[electracker] = self.data['Voltsel'][number[tracker]]
                    if self.data['Currentsel'][number[tracker]] == 'True':
                        self.data['Currentsel'][number[tracker]] = True
                    if self.data['Currentsel'][number[tracker]] == 'False':
                        self.data['Currentsel'][number[tracker]] = False
                    self.setpanel.eleccurrent[electracker] = self.data['Currentsel'][number[tracker]]
                    self.setpanel.elecvmax[electracker] = self.data['VoltMax'][number[tracker]]
                    self.setpanel.elecvmin[electracker] = self.data['VoltMin'][number[tracker]]
                    self.setpanel.elecimin[electracker] = self.data['CurrentMin'][number[tracker]]
                    self.setpanel.elecimax[electracker] = self.data['CurrentMax'][number[tracker]]
                    self.setpanel.elecires[electracker] = self.data['CurrentRes'][number[tracker]]
                    self.setpanel.elecvres[electracker] = self.data['VoltRes'][number[tracker]]
                    if self.data['IV'][number[tracker]] == 'True':
                        self.data['IV'][number[tracker]] = True
                    if self.data['IV'][number[tracker]] == 'False':
                        self.data['IV'][number[tracker]] = False
                    self.setpanel.eleciv[electracker] = self.data['IV'][number[tracker]]
                    if self.data['RV'][number[tracker]] == 'True':
                        self.data['RV'][number[tracker]] = True
                    if self.data['RV'][number[tracker]] == 'False':
                        self.data['RV'][number[tracker]] = False
                    self.setpanel.elecrv[electracker] = self.data['RV'][number[tracker]]
                    if self.data['PV'][number[tracker]] == 'True':
                        self.data['PV'][number[tracker]] = True
                    if self.data['PV'][number[tracker]] == 'False':
                        self.data['PV'][number[tracker]] = False
                    self.setpanel.elecpv[electracker] = self.data['PV'][number[tracker]]
                    if self.data['ChannelA'][number[tracker]] == 'True':
                        self.data['ChannelA'][number[tracker]] = True
                    if self.data['ChannelA'][number[tracker]] == 'False':
                        self.data['ChannelA'][number[tracker]] = False
                    self.setpanel.elecchannelA[electracker] = self.data['ChannelA'][number[tracker]]
                    if self.data['ChannelB'][number[tracker]] == 'True':
                        self.data['ChannelB'][number[tracker]] = True
                    if self.data['ChannelB'][number[tracker]] == 'False':
                        self.data['ChannelB'][number[tracker]] = False
                    self.setpanel.elecchannelB[electracker] = self.data['ChannelB'][number[tracker]]
                    self.setpanel.elecflagholder[electracker] = self.data['ELECflag'][number[tracker]]
                    electracker = electracker + 1

                if a == 'OPTIC':
                    self.setpanel.start[opttracker] = self.data['Start'][number[tracker]]
                    self.setpanel.stop[opttracker] = self.data['Stop'][number[tracker]]
                    self.setpanel.step[opttracker] = self.data['Stepsize'][number[tracker]]
                    self.setpanel.sweeppow[opttracker] = self.data['Sweeppower'][number[tracker]]
                    self.setpanel.sweepsped[opttracker] = self.data['Sweepspeed'][number[tracker]]
                    self.setpanel.laserout[opttracker] = self.data['Laseroutput'][number[tracker]]
                    self.setpanel.numscans[opttracker] = self.data['Numscans'][number[tracker]]
                    self.setpanel.initialran[opttracker] = self.data['InitialRange'][number[tracker]]
                    self.setpanel.rangedecre[opttracker] = self.data['RangeDec'][number[tracker]]
                    self.setpanel.opticflagholder[opttracker] = self.data['OPTICflag'][number[tracker]]
                    opttracker = opttracker + 1

                if a == 'SETW':
                    if self.data['setwVoltsel'][number[tracker]] == 'True':
                        self.data['setwVoltsel'][number[tracker]] = True
                    if self.data['setwVoltsel'][number[tracker]] == 'False':
                        self.data['setwVoltsel'][number[tracker]] = False
                    self.setpanel.setwvolt[setwtracker] = self.data['setwVoltsel'][number[tracker]]
                    if self.data['setwCurrentsel'][number[tracker]] == 'True':
                        self.data['setwCurrentsel'][number[tracker]] = True
                    if self.data['setwCurrentsel'][number[tracker]] == 'False':
                        self.data['setwCurrentsel'][number[tracker]] = False
                    self.setpanel.setwcurrent[setwtracker] = self.data['setwCurrentsel'][number[tracker]]
                    self.setpanel.setwvmax[setwtracker] = self.data['setwVoltMax'][number[tracker]]
                    self.setpanel.setwvmin[setwtracker] = self.data['setwVoltMin'][number[tracker]]
                    self.setpanel.setwimin[setwtracker] = self.data['setwCurrentMin'][number[tracker]]
                    self.setpanel.setwimax[setwtracker] = self.data['setwCurrentMax'][number[tracker]]
                    self.setpanel.setwires[setwtracker] = self.data['setwCurrentRes'][number[tracker]]
                    self.setpanel.setwvres[setwtracker] = self.data['setwVoltRes'][number[tracker]]
                    if self.data['setwIV'][number[tracker]] == 'True':
                        self.data['setwIV'][number[tracker]] = True
                    if self.data['setwIV'][number[tracker]] == 'False':
                        self.data['setwIV'][number[tracker]] = False
                    self.setpanel.setwiv[setwtracker] = self.data['setwIV'][number[tracker]]
                    if self.data['setwRV'][number[tracker]] == 'True':
                        self.data['setwRV'][number[tracker]] = True
                    if self.data['setwRV'][number[tracker]] == 'False':
                        self.data['setwRV'][number[tracker]] = False
                    self.setpanel.setwrv[setwtracker] = self.data['setwRV'][number[tracker]]
                    if self.data['setwPV'][number[tracker]] == 'True':
                        self.data['setwPV'][number[tracker]] = True
                    if self.data['setwPV'][number[tracker]] == 'False':
                        self.data['setwPV'][number[tracker]] = False
                    self.setpanel.setwpv[setwtracker] = self.data['setwPV'][number[tracker]]
                    if self.data['setwChannelA'][number[tracker]] == 'True':
                        self.data['setwChannelA'][number[tracker]] = True
                    if self.data['setwChannelA'][number[tracker]] == 'False':
                        self.data['setwChannelA'][number[tracker]] = False
                    self.setpanel.setwchannelA[setwtracker] = self.data['setwChannelA'][number[tracker]]
                    if self.data['setwChannelB'][number[tracker]] == 'True':
                        self.data['setwChannelB'][number[tracker]] = True
                    if self.data['setwChannelB'][number[tracker]] == 'False':
                        self.data['setwChannelB'][number[tracker]] = False
                    self.setpanel.setwchannelB[setwtracker] = self.data['setwChannelB'][number[tracker]]
                    self.setpanel.setwwavelengths[setwtracker] = self.data['Wavelengths'][number[tracker]]
                    self.setpanel.setwflagholder[setwtracker] = self.data['setwflag'][number[tracker]]
                    setwtracker = setwtracker + 1

                if a == 'SETV':
                    self.setpanel.setvstart[setvtracker] = self.data['setvStart'][number[tracker]]
                    self.setpanel.setvstop[setvtracker] = self.data['setvStop'][number[tracker]]
                    self.setpanel.setvstep[setvtracker] = self.data['setvStepsize'][number[tracker]]
                    self.setpanel.setvsweeppow[setvtracker] = self.data['setvSweeppower'][number[tracker]]
                    self.setpanel.setvsweepsped[setvtracker] = self.data['setvSweepspeed'][number[tracker]]
                    self.setpanel.setvlaserout[setvtracker] = self.data['setvLaseroutput'][number[tracker]]
                    self.setpanel.setvnumscans[setvtracker] = self.data['setvNumscans'][number[tracker]]
                    self.setpanel.setvinitialran[setvtracker] = self.data['setvInitialRange'][number[tracker]]
                    self.setpanel.setvrangedecre[setvtracker] = self.data['setvRangeDec'][number[tracker]]
                    if self.data['setvChannelA'][number[tracker]] == 'True':
                        self.data['setvChannelA'][number[tracker]] = True
                    if self.data['setvChannelA'][number[tracker]] == 'False':
                        self.data['setvChannelA'][number[tracker]] = False
                    self.setpanel.setvchannelA[setvtracker] = self.data['setvChannelA'][number[tracker]]
                    if self.data['setvChannelB'][number[tracker]] == 'True':
                        self.data['setvChannelB'][number[tracker]] = True
                    if self.data['setvChannelB'][number[tracker]] == 'False':
                        self.data['setvChannelB'][number[tracker]] = False
                    self.setpanel.setvchannelB[setvtracker] = self.data['setvChannelB'][number[tracker]]
                    self.setpanel.setvvoltages[setvtracker] = self.data['Voltages'][number[tracker]]
                    self.setpanel.setvflagholder[setvtracker] = self.data['setvflag'][number[tracker]]
                    setvtracker = setvtracker + 1
            tracker = tracker + 1


    def checkListunchecked(self, event):
        """
        If in set data mode this function removes the now unchecked device from the list of selected devices, if in
        retrieve data mode this function removes the device from the list of selected retrieve data devices and
        unhighlights the similar routine devices
        Parameters
        ----------
        event : the event triggered by unselecting a device in the list

        Returns
        -------

        """
        x = event.GetIndex()
        if self.setflag == False and self.retrievedataflag == False:
            self.selected.remove(x)
        elif self.retrievedataflag == True and self.retrievedataselected[0] == x:
            self.retrievedataselected.remove(x)
        elif self.beginning == False and self.end == False and self.retrievedataflag == True:
            #self.retrievedataselected.remove(x)
            #self.retrieveunhighlight(x)
            pass
        elif self.end == True:
            pass


    def OnButton_SelectOutputFolder(self, event):
        """
        Opens the file explorer and allows user to choose the location to save the exported csv file
        Parameters
        ----------
        event : the event triggered by pressing the "open" button to choose the output save location

        Returns
        -------

        """
        dirDlg = wx.DirDialog(self, "Open", "", wx.DD_DEFAULT_STYLE)
        dirDlg.ShowModal()
        self.outputFolderTb.SetValue(dirDlg.GetPath())
        dirDlg.Destroy()


    def OnButton_SelectImportFile(self, event):
        """
        Opens the file explorer and allows user to choose the location to save the exported csv file
        Parameters
        ----------
        event : the event triggered by pressing the "open" button to choose the output save location

        Returns
        -------

        """
        dirDlg = wx.DirDialog(self, "Open", "", wx.DD_DEFAULT_STYLE)
        dirDlg.ShowModal()
        self.importFolderTb = dirDlg.GetPath()
        dirDlg.Destroy()


    def SetButton(self, event):
        """
        This function converts the data input by the user into the various parameter locations and loads it into a
        dictionary that can then be used to either export the data or directly control the equipment
        Parameters
        ----------
        event : the event triggered by pressing the set button

        Returns
        -------

        """

        #do not allow user to set routine while in retrieve data mode
        if self.retrievedataflag == True:
            print('Cannot set data while in retrieve data mode, please change to set data mode to set data')
            return


        #set data to electoopticdevice object for each device by cycling through user inputs
        n = 0

        for dev in deviceListAsObjects:

            for x in self.selected:
                if n == x:
                    for i in range(int(self.instructpanel.elecroutine.GetValue())):
                        if self.setpanel.elecvolt[i] == True:
                            dev.addVoltageSweep(self.setpanel.elecvmin[i], self.setpanel.elecvmax[i],
                                                self.setpanel.elecvres[i],
                                                self.setpanel.eleciv[i], self.setpanel.elecrv[i],
                                                self.setpanel.elecpv[i],
                                                self.setpanel.elecchannelA[i], self.setpanel.elecchannelB[i])
                        elif self.setpanel.eleccurrent[i] == True:
                            dev.addCurrantSweep(self.setpanel.elecimin[i], self.setpanel.elecimax[i],
                                                self.setpanel.elecires[i],
                                                self.setpanel.eleciv[i], self.setpanel.elecrv[i],
                                                self.setpanel.elecpv[i],
                                                self.setpanel.elecchannelA[i], self.setpanel.elecchannelB[i])

                    for i in range(int(self.instructpanel.optroutine.GetValue())):
                        dev.addWavelengthSweep(self.setpanel.start[i], self.setpanel.stop[i], self.setpanel.step[i],
                                               self.setpanel.sweeppow[i], self.setpanel.sweepsped[i], self.setpanel.laserout[i],
                                               self.setpanel.numscans[i],
                                               self.setpanel.initialran[i], self.setpanel.rangedecre[i])

                    for i in range(int(self.instructpanel.setwroutine.GetValue())):
                        if self.setpanel.setwvolt[i] == True:
                            dev.addSetWavelengthVoltageSweep(self.setpanel.setwvmin[i], self.setpanel.setwvmax[i],
                                                             self.setpanel.setwvres[i], self.setpanel.setwiv[i],
                                                             self.setpanel.setwrv[i], self.setpanel.setwpv[i],
                                                             self.setpanel.setwchannelA[i],
                                                             self.setpanel.setwchannelB[i],
                                                             self.setpanel.setwwavelengths[i])
                        elif self.setpanel.setwcurrent[i] == True:
                            dev.addSetWavelengthVoltageSweep(self.setpanel.setwimin[i], self.setpanel.setwimax[i],
                                                             self.setpanel.setwires[i], self.setpanel.setwiv[i],
                                                             self.setpanel.setwrv[i], self.setpanel.setwpv[i],
                                                             self.setpanel.setwchannelA[i],
                                                             self.setpanel.setwchannelB[i],
                                                             self.setpanel.setwwavelengths[i])

                    for i in range(int(self.instructpanel.setwroutine.GetValue())):
                        dev.addSetVoltageWavelengthSweep(self.setpanel.setvstart[i], self.setpanel.setvstop[i],
                                                         self.setpanel.setvstep[i], self.setpanel.setvsweeppow[i],
                                                         self.setpanel.setvsweepsped[i], self.setpanel.setvlaserout[i],
                                                         self.setpanel.setvnumscans[i], self.setpanel.setvinitialran[i],
                                                         self.setpanel.setvrangedecre[i], self.setpanel.setvchannelA[i],
                                                         self.setpanel.setvchannelB[i], self.setpanel.setvvoltages[i])

                n = n + 1

        #
        list.sort(self.selected, reverse=True)
        self.setflag = True
        self.routinenum = self.routinenum + 1

        self.big = max([self.instructpanel.elecroutine.GetValue(), self.instructpanel.optroutine.GetValue(), self.instructpanel.setwroutine.GetValue(), self.instructpanel.setvroutine.GetValue()])

        #to ensure all lists are the same length we find the largest list and append blank strings to the other lists until they match the largest string

        while len(self.setpanel.elecvolt) < int(self.big):
            self.setpanel.elecvolt.append('')
            self.setpanel.eleccurrent.append('')
            self.setpanel.elecvmin.append('')
            self.setpanel.elecvmax.append('')
            self.setpanel.elecimin.append('')
            self.setpanel.elecimax.append('')
            self.setpanel.elecvres.append('')
            self.setpanel.elecires.append('')
            self.setpanel.eleciv.append('')
            self.setpanel.elecrv.append('')
            self.setpanel.elecpv.append('')
            self.setpanel.elecchannelA.append('')
            self.setpanel.elecchannelB.append('')
            self.setpanel.elecflagholder.append('')

        while len(self.setpanel.start) < int(self.big):
            self.setpanel.start.append('')
            self.setpanel.stop.append('')
            self.setpanel.step.append('')
            self.setpanel.sweeppow.append('')
            self.setpanel.sweepsped.append('')
            self.setpanel.laserout.append('')
            self.setpanel.numscans.append('')
            self.setpanel.initialran.append('')
            self.setpanel.rangedecre.append('')
            self.setpanel.opticflagholder.append('')

        while len(self.setpanel.setwvolt) < int(self.big):
            self.setpanel.setwvolt.append('')
            self.setpanel.setwcurrent.append('')
            self.setpanel.setwvmin.append('')
            self.setpanel.setwvmax.append('')
            self.setpanel.setwimin.append('')
            self.setpanel.setwimax.append('')
            self.setpanel.setwvres.append('')
            self.setpanel.setwires.append('')
            self.setpanel.setwiv.append('')
            self.setpanel.setwrv.append('')
            self.setpanel.setwpv.append('')
            self.setpanel.setwchannelA.append('')
            self.setpanel.setwchannelB.append('')
            self.setpanel.setwwavelengths.append('')
            self.setpanel.setwflagholder.append('')

        while len(self.setpanel.setvstart) < int(self.big):
            self.setpanel.setvstart.append('')
            self.setpanel.setvstop.append('')
            self.setpanel.setvstep.append('')
            self.setpanel.setvsweeppow.append('')
            self.setpanel.setvsweepsped.append('')
            self.setpanel.setvlaserout.append('')
            self.setpanel.setvnumscans.append('')
            self.setpanel.setvinitialran.append('')
            self.setpanel.setvrangedecre.append('')
            self.setpanel.setvchannelA.append('')
            self.setpanel.setvchannelB.append('')
            self.setpanel.setvvoltages.append('')
            self.setpanel.setvflagholder.append('')


        for c in range(len(self.selected)):

            save = []

            for a in range(len(self.data['index'])):

                if int(self.data['index'][a]) == int(self.selected[c]):
                    save.append(a)

            list.sort(save, reverse=True)


            for i in range(int(self.big)):
                self.data['device'].append(self.checkList.GetItemText(int(self.selected[c]), 0))
                self.data['index'].append(int(self.selected[c]))


            for i in range(int(self.big)):

                self.data['Voltsel'].append(self.setpanel.elecvolt[i])
                self.data['Currentsel'].append(self.setpanel.eleccurrent[i])
                self.data['VoltMin'].append(self.setpanel.elecvmin[i])
                self.data['VoltMax'].append(self.setpanel.elecvmax[i])
                self.data['CurrentMin'].append(self.setpanel.elecimin[i])
                self.data['CurrentMax'].append(self.setpanel.elecimax[i])
                self.data['VoltRes'].append(self.setpanel.elecvres[i])
                self.data['CurrentRes'].append(self.setpanel.elecires[i])
                self.data['IV'].append(self.setpanel.eleciv[i])
                self.data['RV'].append(self.setpanel.elecrv[i])
                self.data['PV'].append(self.setpanel.elecpv[i])
                self.data['ChannelA'].append(self.setpanel.elecchannelA[i])
                self.data['ChannelB'].append(self.setpanel.elecchannelB[i])
                self.data['ELECflag'].append(self.setpanel.elecflagholder[i])


            for i in range(int(self.big)):

                self.data['Start'].append(self.setpanel.start[i])
                self.data['Stop'].append(self.setpanel.stop[i])
                self.data['Stepsize'].append(self.setpanel.step[i])
                self.data['Sweeppower'].append(self.setpanel.sweeppow[i])
                self.data['Sweepspeed'].append(self.setpanel.sweepsped[i])
                self.data['Laseroutput'].append(self.setpanel.laserout[i])
                self.data['Numscans'].append(self.setpanel.numscans[i])
                self.data['InitialRange'].append(self.setpanel.initialran[i])
                self.data['RangeDec'].append(self.setpanel.rangedecre[i])
                self.data['OPTICflag'].append(self.setpanel.opticflagholder[i])

            for i in range(int(self.big)):

                self.data['setwVoltsel'].append(self.setpanel.setwvolt[i])
                self.data['setwCurrentsel'].append(self.setpanel.setwcurrent[i])
                self.data['setwVoltMin'].append(self.setpanel.setwvmin[i])
                self.data['setwVoltMax'].append(self.setpanel.setwvmax[i])
                self.data['setwCurrentMin'].append(self.setpanel.setwimin[i])
                self.data['setwCurrentMax'].append(self.setpanel.setwimax[i])
                self.data['setwVoltRes'].append(self.setpanel.setwvres[i])
                self.data['setwCurrentRes'].append(self.setpanel.setwires[i])
                self.data['setwIV'].append(self.setpanel.setwiv[i])
                self.data['setwRV'].append(self.setpanel.setwrv[i])
                self.data['setwPV'].append(self.setpanel.setwpv[i])
                self.data['setwChannelA'].append(self.setpanel.setwchannelA[i])
                self.data['setwChannelB'].append(self.setpanel.setwchannelB[i])
                self.data['Wavelengths'].append(self.setpanel.setwwavelengths[i])
                self.data['setwflag'].append(self.setpanel.setwflagholder[i])

            for i in range(int(self.big)):

                self.data['setvStart'].append(self.setpanel.setvstart[i])
                self.data['setvStop'].append(self.setpanel.setvstop[i])
                self.data['setvStepsize'].append(self.setpanel.setvstep[i])
                self.data['setvSweeppower'].append(self.setpanel.setvsweeppow[i])
                self.data['setvSweepspeed'].append(self.setpanel.setvsweepsped[i])
                self.data['setvLaseroutput'].append(self.setpanel.setvlaserout[i])
                self.data['setvNumscans'].append(self.setpanel.setvnumscans[i])
                self.data['setvInitialRange'].append(self.setpanel.setvinitialran[i])
                self.data['setvRangeDec'].append(self.setpanel.setvrangedecre[i])
                self.data['setvChannelA'].append(self.setpanel.setvchannelA[i])
                self.data['setvChannelB'].append(self.setpanel.setvchannelB[i])
                self.data['Voltages'].append(self.setpanel.setvvoltages[i])
                self.data['setvflag'].append(self.setpanel.setvflagholder[i])

            self.checkList.SetItemTextColour(self.selected[c], wx.Colour(211, 211, 211))
            self.checkList.SetItemBackgroundColour(c, wx.Colour(255, 255, 255))
            self.checkList.CheckItem(self.selected[c], False)
            self.set[self.selected[c]] = True

            print('Testing parameters for ' + self.checkList.GetItemText(self.selected[c], 0) + ' set')

        for c in range(int(len(self.selected))*int(self.big)):
            self.data['RoutineNumber'].append(self.routinenum)


        #reset user inputs and selected devices back to default so that next routine can be set
        self.selected = []
        self.setflag = False
        self.setpanel.elecvolt = []
        self.setpanel.eleccurrent = []
        self.setpanel.elecvmax = []
        self.setpanel.elecvmin = []
        self.setpanel.elecimin = []
        self.setpanel.elecimax = []
        self.setpanel.elecires = []
        self.setpanel.elecvres = []
        self.setpanel.eleciv = []
        self.setpanel.elecrv = []
        self.setpanel.elecpv = []
        self.setpanel.elecchannelA = []
        self.setpanel.elecchannelB = []
        self.setpanel.elecflagholder = []

        self.setpanel.start = []
        self.setpanel.stop = []
        self.setpanel.step = []
        self.setpanel.sweeppow = []
        self.setpanel.sweepsped = []
        self.setpanel.laserout = []
        self.setpanel.numscans = []
        self.setpanel.initialran = []
        self.setpanel.rangedecre = []
        self.setpanel.opticflagholder = []

        self.setpanel.setwvolt = []
        self.setpanel.setwcurrent = []
        self.setpanel.setwvmax = []
        self.setpanel.setwvmin = []
        self.setpanel.setwimin = []
        self.setpanel.setwimax = []
        self.setpanel.setwires = []
        self.setpanel.setwvres = []
        self.setpanel.setwiv = []
        self.setpanel.setwrv = []
        self.setpanel.setwpv = []
        self.setpanel.setwchannelA = []
        self.setpanel.setwchannelB = []
        self.setpanel.setwwavelengths = []
        self.setpanel.setwflagholder = []

        self.setpanel.setvstart = []
        self.setpanel.setvstop = []
        self.setpanel.setvstep = []
        self.setpanel.setvsweeppow = []
        self.setpanel.setvsweepsped = []
        self.setpanel.setvlaserout = []
        self.setpanel.setvnumscans = []
        self.setpanel.setvinitialran = []
        self.setpanel.setvrangedecre = []
        self.setpanel.setvvoltages = []
        self.setpanel.setvchannelA = []
        self.setpanel.setvchannelB = []
        self.setpanel.setvflagholder = []

        optionsblank = []

        self.setpanel.routineselectelec.SetItems(optionsblank)
        self.setpanel.routineselectopt.SetItems(optionsblank)
        self.setpanel.routineselectsetw.SetItems(optionsblank)
        self.setpanel.routineselectsetv.SetItems(optionsblank)

        self.instructpanel.elecroutine.SetValue('')
        self.instructpanel.optroutine.SetValue('')
        self.instructpanel.setwroutine.SetValue('')
        self.instructpanel.setvroutine.SetValue('')

        #reset electrical panel parameters
        self.setpanel.voltsel.SetValue(False)
        self.setpanel.currentsel.SetValue(False)
        self.setpanel.maxsetvoltage.SetValue('')
        self.setpanel.maxsetcurrent.SetValue('')
        self.setpanel.minsetvoltage.SetValue('')
        self.setpanel.minsetcurrent.SetValue('')
        self.setpanel.resovoltage.SetValue('')
        self.setpanel.resocurrent.SetValue('')
        self.setpanel.typesel.SetValue(False)
        self.setpanel.type2sel.SetValue(False)
        self.setpanel.type3sel.SetValue(False)
        self.setpanel.Asel.SetValue(True)
        self.setpanel.Bsel.SetValue(False)

        # reset optical panel parameters
        self.setpanel.startWvlTc.SetValue('')
        self.setpanel.stopWvlTc.SetValue('')
        self.setpanel.stepWvlTc.SetValue('')
        self.setpanel.sweepPowerTc.SetValue('')
        self.setpanel.sweepinitialrangeTc.SetValue('')
        self.setpanel.rangedecTc.SetValue('')

        # reset setv panel parameters
        self.setpanel.startWvlTc2.SetValue('')
        self.setpanel.stopWvlTc2.SetValue('')
        self.setpanel.stepWvlTc2.SetValue('')
        self.setpanel.sweepPowerTc2.SetValue('')
        self.setpanel.sweepinitialrangeTc2.SetValue('')
        self.setpanel.rangedecTc2.SetValue('')
        self.setpanel.voltagesetTc2.SetValue('')

        # reset setw panel parameters
        self.setpanel.voltsel2.SetValue(False)
        self.setpanel.currentsel2.SetValue(False)
        self.setpanel.maxsetvoltage2.SetValue('')
        self.setpanel.maxsetcurrent2.SetValue('')
        self.setpanel.minsetvoltage2.SetValue('')
        self.setpanel.minsetcurrent2.SetValue('')
        self.setpanel.resovoltage2.SetValue('')
        self.setpanel.resocurrent2.SetValue('')
        self.setpanel.typesel2.SetValue(False)
        self.setpanel.type2sel2.SetValue(False)
        self.setpanel.type3sel2.SetValue(False)
        self.setpanel.Asel2.SetValue(True)
        self.setpanel.Bsel2.SetValue(False)
        self.setpanel.wavesetTc2.SetValue('')

        #if want to see items in dictionary uncommment code below
        #for keys, values in self.data.items():
         #   print(keys)
          #  print(values)

        print('Data has been set')


    def ExportButton(self, event):
        """
        This function takes the data contained in the data dictionary and formats it into a csv file
        Parameters
        ----------
        event : The event triggered by clicking the export button

        Returns
        -------

        """

        # set paths for saving file to current working directory
        ROOT_DIR = format(os.getcwd())
        primarysavefilecsv = ROOT_DIR + '\TestParameters.csv'
        primarysavefileymlcwd = ROOT_DIR + '\TestParameters.yaml'

        # set path for saving yaml file to selected output folder
        savelocation = self.outputFolderTb.GetValue()
        primarysavefileyml = savelocation + '\TestParameters.yaml'


        # dump deviceListAsObjects which contains all the electroopticdevice objects to a file in selected output folder
        with open(primarysavefileyml, 'w') as f:
            documents = yaml.dump(deviceListAsObjects, f)

        # dump deviceListAsObjects which contains all the electroopticdevice objects to a file in current working directory
        with open(primarysavefileymlcwd, 'w') as f:
            documents = yaml.dump(self.devicedict, f)

        #formatting and outputting data to csv file, (no longer required for code to work but still nice to have)
        with open(primarysavefilecsv, 'w', newline='') as f:
            f.write(',,,,,,,,,,,,,,,,\n')
            f.write(',,,,,,IV Sweep,,,,,,,,,,,,,Optical Sweep,,,,,,,,,Set Wavelength,,,,,,,,,,,,,,SetVoltage,,,,,,Device Properties \n')
            f.write('RoutineNumber, Device ID, ELECFlag, OPTICflag, setwflag, setvflag, Volt Select, Current Select,'
                    ' Volt Min,Volt Max,Current Min,Current Max,Volt Resolution,Current Resolution,IV/VI,RV/RI,PV/PI, '
                    'Channel A, Channel B,Start,Stop,Stepsize,Sweep power,Sweep speed,Laser Output,Number of scans,'
                    ' Initial Range, Range Dec, Volt Select, Current Select, Volt Min,Volt Max,Current Min,Current Max,'
                    'Volt Resolution,Current Resolution,IV/VI,RV/RI,PV/PI, Channel A, Channel B, Wavelength, Start, Stop,'
                    ' Stepsize, Sweep power,Sweep speed,Laser Output,Number of scans, Initial Range, Range Dec,'
                    ' Channel A, Channel B, Voltages, Wavelength, Polarization, Opt x, Opt y, type, Elec x, Elec y \n')

            print(range(len(self.data['device'])))
            print(range(len(self.device_list)))

            len(self.data['Wavelength'])

            for c in range(len(self.data['device']) - len(self.data['Wavelength'])):
                self.data['Wavelength'].append('')
                self.data['Polarization'].append('')
                self.data['Opt x'].append('')
                self.data['Opt y'].append('')
                self.data['type'].append('')
                self.data['Elec x'].append('')
                self.data['Elec y'].append('')

            for c in range(len(self.data['device'])):
                for d in range(len(self.device_list)):
                    print()
                    if self.data['device'][c] == self.device_list[d].getDeviceID():
                        self.data['Wavelength'][c] = self.device_list[d].getDeviceWavelength()
                        self.data['Polarization'][c] = self.device_list[d].getDevicePolarization()
                        x, y = self.device_list[d].getOpticalCoordinates()
                        self.data['Opt x'][c] = x
                        self.data['Opt y'][c] = y
                        self.data['type'][c] = self.device_list[d].getDeviceType()
                        if self.device_list[d].getElectricalCoordinates():
                            coordlist = self.device_list[d].getElectricalCoordinates()
                            bondPad = coordlist[0]
                            x = bondPad[1]
                            y = bondPad[2]
                        else:
                            x= 0
                            y= 0
                        self.data['Elec x'][c] = x
                        self.data['Elec y'][c] = y



            print(len(self.data['device']))
            print(self.data['RoutineNumber'])

            for c in range(len(self.data['device'])):
                f.write(str('N/A') + ',' + str(self.data['device'][c]) + ',' + str(
                    self.data['ELECflag'][c]) + ',' + str(self.data['OPTICflag'][c]) + ',' + str(
                    self.data['setwflag'][c]) + ',' + str(self.data['setvflag'][c]) + ',' + str(
                    self.data['Voltsel'][c]) + ',' + str(self.data['Currentsel'][c]) + ',' + str(
                    self.data['VoltMin'][c]) + ',' + str(self.data['VoltMax'][c])
                        + ',' + str(self.data['CurrentMin'][c]) + ',' + str(self.data['CurrentMax'][c]) + ',' +
                        str(self.data['VoltRes'][c]) + ',' + str(self.data['CurrentRes'][c]) + ',' + str(
                    self.data['IV'][c]) + ','
                        + str(self.data['RV'][c]) + ',' + str(self.data['PV'][c]) + ',' + str(
                    self.data['ChannelA'][c]) + ',' + str(self.data['ChannelB'][c]) + ',' + str(
                    self.data['Start'][c]) + ','
                        + str(self.data['Stop'][c]) + ',' + str(self.data['Stepsize'][c]) + ',' + str(
                    self.data['Sweeppower'][c])
                        + ',' + str(self.data['Sweepspeed'][c]) + ',' + str(self.data['Laseroutput'][c]) + ','
                        + str(self.data['Numscans'][c]) + ',' + str(self.data['InitialRange'][c]) + ',' + str(
                    self.data['RangeDec'][c]) + ',' + str(self.data['setwVoltsel'][c]) + ',' + str(
                    self.data['setwCurrentsel'][c]) + ',' + str(self.data['setwVoltMin'][c]) + ',' + str(
                    self.data['setwVoltMax'][c])
                        + ',' + str(self.data['setwCurrentMin'][c]) + ',' + str(self.data['setwCurrentMax'][c]) + ',' +
                        str(self.data['setwVoltRes'][c]) + ',' + str(self.data['setwCurrentRes'][c]) + ',' + str(
                    self.data['setwIV'][c]) + ','
                        + str(self.data['setwRV'][c]) + ',' + str(self.data['setwPV'][c]) + ',' + str(
                    self.data['setwChannelA'][c]) + ',' + str(self.data['setwChannelB'][c]) + ',' + str(
                    self.data['Wavelengths'][c]) + ',' + str(self.data['setvStart'][c]) + ','
                        + str(self.data['setvStop'][c]) + ',' + str(self.data['setvStepsize'][c]) + ',' + str(
                    self.data['setvSweeppower'][c])
                        + ',' + str(self.data['setvSweepspeed'][c]) + ',' + str(self.data['setvLaseroutput'][c]) + ','
                        + str(self.data['setvNumscans'][c]) + ',' + str(self.data['setvInitialRange'][c]) + ',' + str(
                    self.data['setvRangeDec'][c]) + ',' + str(self.data['setvChannelA'][c]) + ',' + str(
                    self.data['setvChannelB'][c]) + ',' + str(self.data['Voltages'][c]) + ',' + str(
                    self.data['Wavelength'][c]) + ',' + str(self.data['Polarization'][c]) + ',' + str(
                    self.data['Opt x'][c]) + ',' + str(self.data['Opt y'][c]) + ',' + str(self.data['type'][c]) + ','
                        + str(self.data['Elec x'][c]) + ',' + str(self.data['Elec y'][c]) + ',' +'\n')

        if self.outputFolderTb.GetValue() != '':

            savelocation = self.outputFolderTb.GetValue()
            savefile = savelocation + '/TestingParameters.csv'
            savefilestring = savelocation + '\TestingParameters.csv'

            with open(savefile, 'w', newline='') as f:
                f.write(',,,,,,,,,,,,,,,,\n')
                f.write(',,,,,,IV Sweep,,,,,,,,,,,,,Optical Sweep,,,,,,,,,Set Wavelength,,,,,,,,,,,,,,SetVoltage,,,,,,,,,,,,Device Properties\n')
                f.write('RoutineNumber, Device ID, ELECFlag, OPTICflag, setwflag, setvflag, Volt Select,'
                        ' Current Select, Volt Min,Volt Max,Current Min,Current Max,Volt Resolution,Current Resolution,'
                        'IV/VI,RV/RI,PV/PI, Channel A, Channel B,Start,Stop,Stepsize,Sweep power,Sweep speed,'
                        'Laser Output,Number of scans, Initial Range, Range Dec, Volt Select, Current Select, Volt Min,'
                        'Volt Max,Current Min,Current Max,Volt Resolution,Current Resolution,IV/VI,RV/RI,PV/PI,'
                        ' Channel A, Channel B, Wavelength, Start, Stop, Stepsize, Sweep power,Sweep speed,Laser Output,'
                        'Number of scans, Initial Range, Range Dec, Channel A, Channel B, Voltages, Wavelength, Polarization, Opt x, Opt y, type, Elec x, Elec y \n')



                for c in range(len(self.data['device'])):

                    f.write(str('N/A') + ',' + str(self.data['device'][c]) + ',' +
                            str(self.data['ELECflag'][c]) + ',' + str(self.data['OPTICflag'][c]) + ',' +
                            str(self.data['setwflag'][c]) + ',' + str(self.data['setvflag'][c]) + ',' +
                            str(self.data['Voltsel'][c]) + ',' + str(self.data['Currentsel'][c]) + ',' +
                            str(self.data['VoltMin'][c]) + ',' + str(self.data['VoltMax'][c])
                            + ',' + str(self.data['CurrentMin'][c]) + ',' + str(self.data['CurrentMax'][c]) + ',' +
                            str(self.data['VoltRes'][c]) + ',' + str(self.data['CurrentRes'][c]) + ',' +
                            str(self.data['IV'][c]) + ',' + str(self.data['RV'][c]) + ',' + str(self.data['PV'][c]) +
                            ',' + str(self.data['ChannelA'][c]) + ',' + str(self.data['ChannelB'][c]) + ',' +
                            str(self.data['Start'][c]) + ',' + str(self.data['Stop'][c]) + ',' +
                            str(self.data['Stepsize'][c]) + ',' + str(self.data['Sweeppower'][c]) + ',' +
                            str(self.data['Sweepspeed'][c]) + ',' + str(self.data['Laseroutput'][c]) + ',' +
                            str(self.data['Numscans'][c]) + ',' + str(self.data['InitialRange'][c]) + ',' +
                            str(self.data['RangeDec'][c]) + ',' + str(self.data['setwVoltsel'][c]) + ',' +
                            str(self.data['setwCurrentsel'][c]) + ',' + str(self.data['setwVoltMin'][c]) + ',' +
                            str(self.data['setwVoltMax'][c]) + ',' + str(self.data['setwCurrentMin'][c]) + ',' +
                            str(self.data['setwCurrentMax'][c]) + ',' + str(self.data['setwVoltRes'][c]) + ',' +
                            str(self.data['setwCurrentRes'][c]) + ',' + str(self.data['setwIV'][c]) + ',' +
                            str(self.data['setwRV'][c]) + ',' + str(self.data['setwPV'][c]) + ',' +
                            str(self.data['setwChannelA'][c]) + ',' + str(self.data['setwChannelB'][c]) + ',' +
                            str(self.data['Wavelengths'][c]) + ',' + str(self.data['setvStart'][c]) + ',' +
                            str(self.data['setvStop'][c]) + ',' + str(self.data['setvStepsize'][c]) + ',' +
                            str(self.data['setvSweeppower'][c]) + ',' + str(self.data['setvSweepspeed'][c]) + ',' +
                            str(self.data['setvLaseroutput'][c]) + ',' + str(self.data['setvNumscans'][c]) + ',' +
                            str(self.data['setvInitialRange'][c]) + ',' + str(self.data['setvRangeDec'][c]) + ',' +
                            str(self.data['setvChannelA'][c]) + ',' + str(self.data['setvChannelB'][c]) + ',' +
                            str(self.data['Voltages'][c]) + ',' + str(
                            self.data['Wavelength'][c]) + ',' + str(self.data['Polarization'][c]) + ',' + str(
                            self.data['Opt x'][c]) + ',' + str(self.data['Opt y'][c]) + ',' + str(self.data['type'][c]) + ','
                            + str(self.data['Elec x'][c]) + ',' + str(self.data['Elec y'][c]) + ',' +'\n')
                    count = c

                devicesetcheck = [False] * len(self.device_list)


                for c in range(len(self.device_list)):
                    for d in range(len(self.data['device'])):
                        print(self.device_list[c].getDeviceID())
                        print(self.data['device'][d])
                        if self.device_list[c].getDeviceID() == self.data['device'][d]:
                            devicesetcheck[c] = True
                            break
                        else:
                            pass

                print(devicesetcheck)

                for c in range(len(self.device_list)):

                    if devicesetcheck[c] == False:
                        if self.device_list[c].getElectricalCoordinates():
                            f.write(',' + str(self.device_list[c].getDeviceID()) + ',' +
                                     ',' + ',' + ','  + ',' + ','  + ',' + ',' + ','  + ',' + ',' + ',' + ',' + ',' + ',' +
                                    ',' + ',' + ',' + ',' + ',' + ',' + ',' + ',' + ',' + ',' + ',' + ',' + ',' + ',' + ','
                                    + ',' + ',' + ',' + ',' + ',' + ',' + ',' + ',' + ',' + ',' + ',' + ',' + ',' + ',' +
                                    ',' + ',' +',' + ',' + ',' + ',' + ',' + ',' + ',' + str(self.device_list[c].getDeviceWavelength())
                                    + ',' + str(self.device_list[c].getDevicePolarization()) + ',' + str(
                                self.device_list[c].getOpticalCoordinates()[0]) + ',' + str(self.device_list[c].getOpticalCoordinates()[1]) + ',' + str(
                                self.device_list[c].getDeviceType()) + ',' + str(self.device_list[c].getElectricalCoordinates()[0][1])
                                    + ',' + str(self.device_list[c].getElectricalCoordinates()[0][2]) + ',' + '\n')



                print('Data exported to ' + savefilestring)


    def ImportButton(self, event):

        #open file explorer to find file to import
        filDlg = wx.FileDialog(self, "Open", "")
        filDlg.ShowModal()
        self.importFolderTb = filDlg.GetPath()
        filDlg.Destroy()

        originalfile = self.importFolderTb

        #if import file is a yaml file, use this to populate devicelistasobjects
        if '.yaml' in originalfile:

            with open(originalfile, 'r') as file:
                deviceListAsObjects = yaml.safe_load(file)

            self.device_list = deviceListAsObjects
            global deviceList
            deviceList = []
            for device in deviceListAsObjects:
                deviceList.append(device.getDeviceID())
            # Adds items to the check list
            self.checkList.DeleteAllItems()
            for ii, device in enumerate(deviceList):
                self.checkList.InsertItem(ii, device)
                for dev in deviceListAsObjects:
                    if dev.getDeviceID() == device:
                        index = deviceListAsObjects.index(dev)  # Stores index of device in list
                self.checkList.SetItemData(ii, index)
            self.checkList.SortItems(self.checkListSort)  # Make sure items in list are sorted
            self.checkList.EnableCheckBoxes()
            self.set = [False] * self.checkList.GetItemCount()



        elif '.csv' in originalfile:
            # check to see that user has actually selected a file
            if originalfile == '':
                print('Please select a file to import')
                return

            self.data['device'].clear()
            self.data['index'].clear()
            self.data['Voltsel'].clear()
            self.data['Currentsel'].clear()
            self.data['VoltMin'].clear()
            self.data['VoltMax'].clear()
            self.data['CurrentMin'].clear()
            self.data['CurrentMax'].clear()
            self.data['VoltRes'].clear()
            self.data['CurrentRes'].clear()
            self.data['IV'].clear()
            self.data['RV'].clear()
            self.data['PV'].clear()
            self.data['ChannelA'].clear()
            self.data['ChannelB'].clear()
            self.data['ELECflag'].clear()
            self.data['Start'].clear()
            self.data['Stop'].clear()
            self.data['Stepsize'].clear()
            self.data['Sweeppower'].clear()
            self.data['Sweepspeed'].clear()
            self.data['Laseroutput'].clear()
            self.data['Numscans'].clear()
            self.data['InitialRange'].clear()
            self.data['RangeDec'].clear()
            self.data['OPTICflag'].clear()
            self.data['setwVoltsel'].clear()
            self.data['setwCurrentsel'].clear()
            self.data['setwVoltMin'].clear()
            self.data['setwVoltMax'].clear()
            self.data['setwCurrentMin'].clear()
            self.data['setwCurrentMax'].clear()
            self.data['setwVoltRes'].clear()
            self.data['setwCurrentRes'].clear()
            self.data['setwIV'].clear()
            self.data['setwRV'].clear()
            self.data['setwPV'].clear()
            self.data['setwChannelA'].clear()
            self.data['setwChannelB'].clear()
            self.data['Wavelengths'].clear()
            self.data['setwflag'].clear()
            self.data['setvStart'].clear()
            self.data['setvStop'].clear()
            self.data['setvStepsize'].clear()
            self.data['setvSweeppower'].clear()
            self.data['setvSweepspeed'].clear()
            self.data['setvLaseroutput'].clear()
            self.data['setvNumscans'].clear()
            self.data['setvInitialRange'].clear()
            self.data['setvRangeDec'].clear()
            self.data['setvChannelA'].clear()
            self.data['setvChannelB'].clear()
            self.data['Voltages'].clear()
            self.data['setvflag'].clear()
            self.data['RoutineNumber'].clear()
            self.data['Wavelength'].clear()
            self.data['Polarization'].clear()
            self.data['Opt x'].clear()
            self.data['Opt y'].clear()
            self.data['type'].clear()
            self.data['Elec x'].clear()
            self.data['Elec y'].clear()

            with open(originalfile, 'r') as file:
                rows = []
                for row in file:
                    rows.append(row)

                rows.pop(2)
                rows.pop(1)
                rows.pop(0)

                i = 0

                for d in range(len(rows)):
                    x = rows[d].split(',')

                    if x[2] == 'True' or x[3] == 'True' or x[4] == 'True' or x[5] == 'True':
                        i = i + 1

                for c in range(i):
                    x = rows[c].split(',')

                    self.data['device'].append(x[1])
                    self.data['ELECflag'].append(x[2])
                    self.data['OPTICflag'].append(x[3])
                    self.data['setwflag'].append(x[4])
                    self.data['setvflag'].append(x[5])
                    self.data['Voltsel'].append(x[6])
                    self.data['Currentsel'].append(x[7])
                    self.data['VoltMin'].append(x[8])
                    self.data['VoltMax'].append(x[9])
                    self.data['CurrentMin'].append(x[10])
                    self.data['CurrentMax'].append(x[11])
                    self.data['VoltRes'].append(x[12])
                    self.data['CurrentRes'].append(x[13])
                    self.data['IV'].append(x[14])
                    self.data['RV'].append(x[15])
                    self.data['PV'].append(x[16])
                    self.data['ChannelA'].append(x[17])
                    self.data['ChannelB'].append(x[18])
                    self.data['Start'].append(x[19])
                    self.data['Stop'].append(x[20])
                    self.data['Stepsize'].append(x[21])
                    self.data['Sweeppower'].append(x[22])
                    self.data['Sweepspeed'].append(x[23])
                    self.data['Laseroutput'].append(x[24])
                    self.data['Numscans'].append(x[25])
                    self.data['InitialRange'].append(x[26])
                    self.data['RangeDec'].append(x[27])
                    self.data['setwVoltsel'].append(x[28])
                    self.data['setwCurrentsel'].append(x[29])
                    self.data['setwVoltMin'].append(x[30])
                    self.data['setwVoltMax'].append(x[31])
                    self.data['setwCurrentMin'].append(x[32])
                    self.data['setwCurrentMax'].append(x[33])
                    self.data['setwVoltRes'].append(x[34])
                    self.data['setwCurrentRes'].append(x[35])
                    self.data['setwIV'].append(x[36])
                    self.data['setwRV'].append(x[37])
                    self.data['setwPV'].append(x[38])
                    self.data['setwChannelA'].append(x[39])
                    self.data['setwChannelB'].append(x[40])
                    self.data['Wavelengths'].append(x[41])
                    self.data['setvStart'].append(x[42])
                    self.data['setvStop'].append(x[43])
                    self.data['setvStepsize'].append(x[44])
                    self.data['setvSweeppower'].append(x[45])
                    self.data['setvSweepspeed'].append(x[46])
                    self.data['setvLaseroutput'].append(x[47])
                    self.data['setvNumscans'].append(x[48])
                    self.data['setvInitialRange'].append(x[49])
                    self.data['setvRangeDec'].append(x[50])
                    self.data['setvChannelA'].append(x[51])
                    self.data['setvChannelB'].append(x[52])
                    self.data['Voltages'].append(x[53])
                    self.data['Wavelength'].append(x[54])
                    self.data['Polarization'].append(x[55])
                    self.data['Opt x'].append(x[56])
                    self.data['Opt y'].append(x[57])
                    self.data['type'].append(x[58])
                    self.data['Elec x'].append(x[59])
                    self.data['Elec y'].append(x[60])

            for keys, values in self.data.items():
                print(keys)
                print(values)

            # self.checkList.DeleteAllItems()
            # devicelist = []
            # for c in range(len(self.dataimport['Device'])):
            #   devicelist.append(self.dataimport['Device'][c])

            deviceListAsObjects = self.autoMeasurePanel.readCSV(originalfile)
            self.device_list = deviceListAsObjects
            deviceList = []
            for device in deviceListAsObjects:
                deviceList.append(device.getDeviceID())
            # Adds items to the check list
            self.checkList.DeleteAllItems()
            for ii, device in enumerate(deviceList):
                self.checkList.InsertItem(ii, device)
                for dev in deviceListAsObjects:
                    if dev.getDeviceID() == device:
                        index = deviceListAsObjects.index(dev)  # Stores index of device in list
                self.checkList.SetItemData(ii, index)
            self.checkList.SortItems(self.checkListSort)  # Make sure items in list are sorted
            self.checkList.EnableCheckBoxes()
            self.set = [False] * self.checkList.GetItemCount()


class autoMeasure(object):

    def __init__(self):
        self.saveFolder = os.getcwd()

    def readCoordFile(self, fileName):

        with open(fileName, 'r') as f:
            data = f.readlines()

        # Remove the first line since it is the header and remove newline char
        dataStrip = [line.strip() for line in data[1:]]
        dataStrip2 = []
        for x in dataStrip:
            j = x.replace(" ", "")
            dataStrip2.append(j)
        # x,y,polarization,wavelength,type,deviceid,params
        reg = re.compile(r'(.-?[0-9]*),(.-?[0-9]*),(T(E|M)),([0-9]+),(.+?),(.+),(.*)')
        # x, y, deviceid, padname, params
        regElec = re.compile(r'(.-?[0-9]+),(.-?[0-9]+),(.+),(.+),(.*)')

        self.devices = []
        self.devSet = set()

        for ii, line in enumerate(dataStrip2):
            if reg.match(line):
                matchRes = reg.findall(line)[0]
                devName = matchRes[6]
                self.devSet.add(devName)

        # Parse the data in each line and put it into a list of devices
        for ii, line in enumerate(dataStrip2):
            if reg.match(line):
                matchRes = reg.findall(line)[0]
                devName = matchRes[6]
                if devName in self.devSet:
                    devName = "X:"+matchRes[0]+"Y:"+matchRes[1]+devName
                self.devSet.add(devName)
                device = ElectroOpticDevice(devName, matchRes[3], matchRes[2], float(matchRes[0]), float(matchRes[1]),
                                            matchRes[5])
                self.devices.append(device)
            else:
                if regElec.match(line):
                    print(line)
                    matchRes = reg.findall(line)[0]
                    devName = matchRes[2]
                    if devName in self.devSet:
                        devName = "X:" + matchRes[0] + "Y:" + matchRes[1] + devName
                    for device in self.devices:
                        if device.getDeviceID() == devName:
                            device.addElectricalCoordinates(matchRes[3], float(matchRes[0]), float(matchRes[1]))
                else:
                    if line == "" or line == "%X-coord,Y-coord,deviceID,padName,params":
                        pass
                    else:
                        print('Warning: The entry\n%s\nis not formatted correctly.' % line)

    def readCSV(self, originalFile):
        """Reads a csv testing parameters file and stores the information as a list of electro-optic device
         objects to be used for automated measurements."""

        global deviceListAsObjects
        deviceListAsObjects = []

        with open(originalFile, 'r') as file:
            rows = []
            for row in file:
                rows.append(row)

            rows.pop(2)
            rows.pop(1)
            rows.pop(0)

            for c in range(len(rows)):
                x = rows[c].split(',')

                deviceToTest = False
                deviceToTestFlag = True

                if len(deviceListAsObjects) == 0:
                    deviceToTest = ElectroOpticDevice(x[1], x[54], x[55], x[56], x[57], x[58])
                else:
                    for device in deviceListAsObjects:
                        if device.getDeviceID() == x[1]:
                            deviceToTest = device
                            deviceToTestFlag = False
                    if deviceToTest == False:
                        print("got here")
                        deviceToTest = ElectroOpticDevice(x[1], x[54], x[55], x[56], x[57], x[58])

                if x[2] == "True":
                    """electrical routine"""
                    if x[6] == "True":
                        """voltage sweep"""
                        deviceToTest.addVoltageSweep(x[8], x[9], x[12], x[14], x[15], x[16], x[17], x[18])
                    if x[7] == "True":
                        """Current sweep"""
                        deviceToTest.addCurrentSweep(x[10], x[11], x[13], x[14], x[15], x[16], x[17], x[18])
                if x[3] == "True":
                    """optical routine"""
                    deviceToTest.addWavelengthSweep(x[19], x[20], x[21], x[22], x[23], x[24], x[25], x[26], x[27])
                if x[4] == "True":
                    """set wavelength iv"""
                    if x[28] == "True":
                        """voltage sweep"""
                        deviceToTest.addSetWavelengthVoltageSweep(x[30], x[31], x[34], x[36], x[37], x[38], x[39], x[40], x[41])
                    if x[29] == "True":
                        """current sweep"""
                        deviceToTest.addSetWavelengthCurrentSweep(x[32], x[33], x[35], x[36], x[37], x[38], x[39], x[40], x[41])
                if x[5] == "True":
                    """set voltage optical sweep"""
                    deviceToTest.addSetVoltageWavelengthSweep(x[42], x[43], x[44], x[45], x[46], x[47], x[48],
                                                              x[49], x[50], x[51], x[52], x[53])
                if deviceToTestFlag:
                    deviceListAsObjects.append(deviceToTest)


#This panel class contains the instructions for going about inputting the routine data for the devices as well as the
#selection menu for the number of different routines
class InstructPanel(wx.Panel):

    def __init__(self, parent, setpanel):
        super(InstructPanel, self).__init__(parent)
        self.setpanel = setpanel
        self.InitUI()


    def InitUI(self):

        # INSTRUCTIONS###################################################################################################

        sbw = wx.StaticBox(self, label='Instructions')
        instructions = wx.StaticBoxSizer(sbw, wx.VERTICAL)

        # create sizers and text for instructions
        steps = wx.BoxSizer(wx.VERTICAL)
        step1 = wx.BoxSizer(wx.HORIZONTAL)
        stp1 = wx.StaticText(self, label='1. Upload automated test coordinate file')
        step1.Add(stp1, 1, wx.EXPAND)

        step1_5 = wx.BoxSizer(wx.HORIZONTAL)
        stp1_5 = wx.StaticText(self, label='coordinate file')
        step1_5.Add(stp1_5, 1, wx.EXPAND)

        step2 = wx.BoxSizer(wx.HORIZONTAL)
        stp2 = wx.StaticText(self, label='2. Select devices you wish to create routines for')
        step2.Add(stp2, 1, wx.EXPAND)

        step2_5 = wx.BoxSizer(wx.HORIZONTAL)
        stp2_5 = wx.StaticText(self, label='create routines for')
        step2_5.Add(stp2_5, 1, wx.EXPAND)

        step3 = wx.BoxSizer(wx.HORIZONTAL)
        stp3 = wx.StaticText(self, label='3. Select number of routines per type of routine')
        step3.Add(stp3, 1, wx.EXPAND)

        step3_5 = wx.BoxSizer(wx.HORIZONTAL)
        stp3_5 = wx.StaticText(self, label='per type of routine')
        step3_5.Add(stp3_5, 1, wx.EXPAND)

        step4 = wx.BoxSizer(wx.HORIZONTAL)
        stp4 = wx.StaticText(self, label='4. Fill in routine data')
        step4.Add(stp4, 1, wx.EXPAND)

        step5 = wx.BoxSizer(wx.HORIZONTAL)
        stp5 = wx.StaticText(self, label='5. Click set button')
        step5.Add(stp5, 1, wx.EXPAND)

        step6 = wx.BoxSizer(wx.HORIZONTAL)
        stp6 = wx.StaticText(self, label='6. Repeat from step 2')
        step6.Add(stp6, 1, wx.EXPAND)

        # format steps
        steps.AddMany([(step1, 1, wx.EXPAND), (step1_5, 1, wx.EXPAND), (step2, 1, wx.EXPAND), (step2_5, 1, wx.EXPAND), (step3, 1, wx.EXPAND), (step3_5, 1, wx.EXPAND), (step4, 1, wx.EXPAND),
                       (step5, 1, wx.EXPAND), (step6, 1, wx.EXPAND)])
        instructions.Add(steps, 1, wx.EXPAND)

        # NUMBER OF ROUTINES SELECTION###################################################################################

        # create general sizer for routine selection
        sb1_3 = wx.StaticBox(self, label='Routine Select')
        routineselect = wx.StaticBoxSizer(sb1_3, wx.VERTICAL)

        # Electrical, set number of routines selection
        electricalroutine = wx.BoxSizer(wx.HORIZONTAL)
        st10_2 = wx.StaticText(self, label='Electrical Routine')
        self.elecroutine = wx.TextCtrl(self, size=(40, 20))
        self.elecroutine.name = 'elecroutine'
        self.elecroutine.SetValue('0')
        self.elecroutine.Bind(wx.EVT_TEXT, self.setnumroutine)
        electricalroutine.AddMany([(st10_2, 1, wx.EXPAND), (self.elecroutine, 0)])

        # Optical, set number of routines selection
        opticalroutine = wx.BoxSizer(wx.HORIZONTAL)
        st11_2 = wx.StaticText(self, label='Optical Routine')
        self.optroutine = wx.TextCtrl(self, size=(40, 20))
        self.optroutine.name = 'optroutine'
        self.optroutine.SetValue('0')
        self.optroutine.Bind(wx.EVT_TEXT, self.setnumroutine)
        opticalroutine.AddMany([(st11_2, 1, wx.EXPAND), (self.optroutine, 0)])

        # Set voltage, wavelength sweep, set number of routines selection
        setvwsweeproutine = wx.BoxSizer(wx.HORIZONTAL)
        st12_2 = wx.StaticText(self, label='Set Voltage')
        self.setvroutine = wx.TextCtrl(self, size=(40, 20))
        self.setvroutine.name = 'setvroutine'
        self.setvroutine.SetValue('0')
        self.setvroutine.Bind(wx.EVT_TEXT, self.setnumroutine)
        setvwsweeproutine.AddMany([(st12_2, 1, wx.EXPAND), (self.setvroutine, 0)])

        # Set wavelength, voltage sweep, set number of routines selection
        setwvsweeproutine = wx.BoxSizer(wx.HORIZONTAL)
        st13_2 = wx.StaticText(self, label='Set Wavelength')
        self.setwroutine = wx.TextCtrl(self, size=(40, 20))
        self.setwroutine.name = 'setwroutine'
        self.setwroutine.SetValue('0')
        self.setwroutine.Bind(wx.EVT_TEXT, self.setnumroutine)
        setwvsweeproutine.AddMany([(st13_2, 1, wx.EXPAND), (self.setwroutine)])

        # format routine selection sizers
        routineselect.AddMany(
            [(instructions, 0, wx.EXPAND), (electricalroutine, 0, wx.EXPAND), (opticalroutine, 0, wx.EXPAND),
             (setvwsweeproutine, 0, wx.EXPAND), (setwvsweeproutine, 0, wx.EXPAND)])

        self.SetSizer(routineselect)


    def setnumroutine(self, event):
        """
        Based on the input for number of different routines this function will create lists for each routine with
        the length equal to the number of routines input
        :param event: the event created on input of number into number of routine menu
        Parameters
        ----------
        event : the event triggered on input of number into number of routine menu

        Returns
        -------

        """
        c = event.GetEventObject()

        optionsblank = []

        if c.GetValue().isdigit() != True and c.GetValue() != '':
            c.SetValue('')
            print('Routine number must be a positive integer')
            return

        if c.GetValue() != '':
            options = []
            for x in range(int(c.GetValue())):
                x = x + 1
                options.append(str(x))

            if c.name == 'elecroutine':
                self.setpanel.routineselectelec.SetItems(options)
                self.setpanel.elecvolt = [''] * int(c.GetValue())
                self.setpanel.eleccurrent = [''] * int(c.GetValue())
                self.setpanel.elecvmax = [''] * int(c.GetValue())
                self.setpanel.elecvmin = ['']* int(c.GetValue())
                self.setpanel.elecimin = [''] * int(c.GetValue())
                self.setpanel.elecimax = [''] * int(c.GetValue())
                self.setpanel.elecires = [''] * int(c.GetValue())
                self.setpanel.elecvres = [''] * int(c.GetValue())
                self.setpanel.eleciv = [''] * int(c.GetValue())
                self.setpanel.elecrv = [''] * int(c.GetValue())
                self.setpanel.elecpv = [''] * int(c.GetValue())
                self.setpanel.elecchannelA = [''] * int(c.GetValue())
                self.setpanel.elecchannelB = [''] * int(c.GetValue())
                self.setpanel.elecflagholder = [''] * int(c.GetValue())

            if c.name == 'optroutine':
                self.setpanel.routineselectopt.SetItems(options)
                self.setpanel.start = [''] * int(c.GetValue())
                self.setpanel.stop = [''] * int(c.GetValue())
                self.setpanel.step = [''] * int(c.GetValue())
                self.setpanel.sweeppow = [''] * int(c.GetValue())
                self.setpanel.sweepsped = [''] * int(c.GetValue())
                self.setpanel.laserout = [''] * int(c.GetValue())
                self.setpanel.numscans = [''] * int(c.GetValue())
                self.setpanel.initialran = [''] * int(c.GetValue())
                self.setpanel.rangedecre = [''] * int(c.GetValue())
                self.setpanel.opticflagholder = [''] * int(c.GetValue())

            if c.name == 'setwroutine':
                self.setpanel.routineselectsetw.SetItems(options)
                self.setpanel.setwvolt = [''] * int(c.GetValue())
                self.setpanel.setwcurrent = [''] * int(c.GetValue())
                self.setpanel.setwvmax = [''] * int(c.GetValue())
                self.setpanel.setwvmin = [''] * int(c.GetValue())
                self.setpanel.setwimin = [''] * int(c.GetValue())
                self.setpanel.setwimax = [''] * int(c.GetValue())
                self.setpanel.setwires = [''] * int(c.GetValue())
                self.setpanel.setwvres = [''] * int(c.GetValue())
                self.setpanel.setwiv = [''] * int(c.GetValue())
                self.setpanel.setwrv = [''] * int(c.GetValue())
                self.setpanel.setwpv = [''] * int(c.GetValue())
                self.setpanel.setwchannelA = [''] * int(c.GetValue())
                self.setpanel.setwchannelB = [''] * int(c.GetValue())
                self.setpanel.setwwavelengths = [''] * int(c.GetValue())
                self.setpanel.setwflagholder = [''] * int(c.GetValue())

            if c.name == 'setvroutine':
                self.setpanel.routineselectsetv.SetItems(options)
                self.setpanel.setvstart = [''] * int(c.GetValue())
                self.setpanel.setvstop = [''] * int(c.GetValue())
                self.setpanel.setvstep = [''] * int(c.GetValue())
                self.setpanel.setvsweeppow = [''] * int(c.GetValue())
                self.setpanel.setvsweepsped = [''] * int(c.GetValue())
                self.setpanel.setvlaserout = [''] * int(c.GetValue())
                self.setpanel.setvnumscans = [''] * int(c.GetValue())
                self.setpanel.setvinitialran = [''] * int(c.GetValue())
                self.setpanel.setvrangedecre = [''] * int(c.GetValue())
                self.setpanel.setvchannelA = [''] * int(c.GetValue())
                self.setpanel.setvchannelB = [''] * int(c.GetValue())
                self.setpanel.setvvoltages = [''] * int(c.GetValue())
                self.setpanel.setvflagholder = [''] * int(c.GetValue())

        if c.GetValue() == '':
            if c.name == 'elecroutine':
                self.setpanel.routineselectelec.SetItems(optionsblank)
            if c.name == 'optroutine':
                self.setpanel.routineselectopt.SetItems(optionsblank)
            if c.name == 'setwroutine':
                self.setpanel.routineselectsetw.SetItems(optionsblank)
            if c.name == 'setvroutine':
                self.setpanel.routineselectsetv.SetItems(optionsblank)


#the Panel responsible for the user input of parameters
class SetPanel(wx.Panel):

    def __init__(self, parent):
        super(SetPanel, self).__init__(parent)
        self.elecvolt = []
        self.eleccurrent = []
        self.elecvmax = []
        self.elecvmin = []
        self.elecimin = []
        self.elecimax = []
        self.elecires = []
        self.elecvres = []
        self.eleciv = []
        self.elecrv = []
        self.elecpv = []
        self.elecchannelA = []
        self.elecchannelB = []
        self.elecflagholder = []

        self.start = []
        self.stop = []
        self.step = []
        self.sweeppow = []
        self.sweepsped = []
        self.laserout = []
        self.numscans = []
        self.initialran = []
        self.rangedecre = []
        self.opticflagholder = []

        self.setwvolt = []
        self.setwcurrent = []
        self.setwvmax = []
        self.setwvmin = []
        self.setwimin = []
        self.setwimax = []
        self.setwires = []
        self.setwvres = []
        self.setwiv = []
        self.setwrv = []
        self.setwpv = []
        self.setwchannelA = []
        self.setwchannelB = []
        self.setwwavelengths = []
        self.setwflagholder = []

        self.setvstart = []
        self.setvstop = []
        self.setvstep = []
        self.setvsweeppow = []
        self.setvsweepsped = []
        self.setvlaserout = []
        self.setvnumscans = []
        self.setvinitialran = []
        self.setvrangedecre = []
        self.setvvoltages = []
        self.setvchannelA = []
        self.setvchannelB = []
        self.setvflagholder = []

        self.InitUI()


    def InitUI(self):

        ##CREATE ELECTRICAL PANEL#######################################################################################

        #create electrical panel sizer and necessary vboxes and hboxes
        sb = wx.StaticBox(self, label='Electrical')
        elecvbox = wx.StaticBoxSizer(sb, wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        evbox = wx.BoxSizer(wx.VERTICAL)
        tophbox = wx.BoxSizer(wx.HORIZONTAL)

        #Electrical routine selection tab
        hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        sq0_1 = wx.StaticText(self, label='Select Routine ')
        options = []
        self.routineselectelec = wx.ComboBox(self, choices=options, style=wx.CB_READONLY, value='1', size=(80, -1))
        self.routineselectelec.name = 'routineselectelec'
        self.routineselectelec.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.routinepanel)
        self.routineselectelec.Bind(wx.EVT_COMBOBOX, self.swaproutine)
        hbox0.AddMany([(sq0_1, 1, wx.EXPAND), (self.routineselectelec, 0, wx.EXPAND)])

        #Independent Variable selection
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        sq1_1 = wx.StaticText(self, label='Select Independent Variable: ')
        self.voltsel = wx.CheckBox(self, label='Voltage', pos=(20, 20), size=(40, -1))
        self.voltsel.SetValue(False)
        self.voltsel.Bind(wx.EVT_CHECKBOX, self.trueorfalse)
        self.currentsel = wx.CheckBox(self, label='Current', pos=(20, 20))
        self.currentsel.SetValue(False)
        self.currentsel.Bind(wx.EVT_CHECKBOX, self.trueorfalse)
        hbox1.AddMany([(sq1_1, 1, wx.EXPAND), (self.voltsel, 1, wx.EXPAND), (self.currentsel, 1, wx.EXPAND)])

        #Voltage and Current maximum select
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        sw1 = wx.StaticText(self, label='Set Max:')
        self.maxsetvoltage = wx.TextCtrl(self, size=(60, -1))
        self.maxsetvoltage.SetValue('V')
        self.maxsetvoltage.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        self.maxsetvoltage.SetForegroundColour(wx.Colour(211, 211, 211))
        self.maxsetcurrent = wx.TextCtrl(self, size=(60, -1))
        self.maxsetcurrent.SetValue('mA')
        self.maxsetcurrent.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        self.maxsetcurrent.SetForegroundColour(wx.Colour(211,211,211))
        hbox2.AddMany([(sw1, 1, wx.EXPAND), (self.maxsetvoltage, 0, wx.EXPAND), (self.maxsetcurrent, 0, wx.EXPAND)])

        #Voltage and current minimum select
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        sw2 = wx.StaticText(self, label='Set Min:')
        self.minsetcurrent = wx.TextCtrl(self, size=(60, -1))
        self.minsetcurrent.SetValue('mA')
        self.minsetcurrent.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        self.minsetcurrent.SetForegroundColour(wx.Colour(211, 211, 211))
        self.minsetvoltage = wx.TextCtrl(self, size=(60, -1))
        self.minsetvoltage.SetValue('V')
        self.minsetvoltage.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        self.minsetvoltage.SetForegroundColour(wx.Colour(211, 211, 211))
        hbox3.AddMany([(sw2, 1, wx.EXPAND), (self.minsetvoltage, 0, wx.EXPAND), (self.minsetcurrent, 0, wx.EXPAND)])

        #Voltage and Current resolution select
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        sw3 = wx.StaticText(self, label='Set Resolution:')
        self.resovoltage = wx.TextCtrl(self, size=(60, -1))
        self.resovoltage.SetValue('V')
        self.resovoltage.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        self.resovoltage.SetForegroundColour(wx.Colour(211, 211, 211))
        self.resocurrent = wx.TextCtrl(self, size=(60, -1))
        self.resocurrent.SetValue('mA')
        self.resocurrent.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        self.resocurrent.SetForegroundColour(wx.Colour(211, 211, 211))
        hbox4.AddMany([(sw3, 1, wx.EXPAND), (self.resovoltage, 0, wx.EXPAND), (self.resocurrent, 0, wx.EXPAND)])

        #Plot type selection checkboxes
        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        sh2 = wx.StaticText(self, label='Plot Type:')
        self.typesel = wx.CheckBox(self, label='IV/VI', pos=(20, 20))
        self.typesel.SetValue(False)
        self.type2sel = wx.CheckBox(self, label='RV/RI', pos=(20, 20))
        self.type2sel.SetValue(False)
        self.type3sel = wx.CheckBox(self, label='PV/PI', pos=(20, 20))
        self.type3sel.SetValue(False)
        hbox5.AddMany([(sh2, 1, wx.EXPAND), (self.typesel, 1, wx.EXPAND), (self.type2sel, 1, wx.EXPAND),
                       (self.type3sel, 1, wx.EXPAND)])

        #electrical SMU channel select checkboxes and elecrical save button
        hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        sq6_1 = wx.StaticText(self, label='Select SMU Channel: ')
        self.Asel = wx.CheckBox(self, label='A', pos=(20, 20))
        self.Asel.SetValue(False)
        self.Bsel = wx.CheckBox(self, label='B', pos=(20, 20))
        self.Bsel.SetValue(False)
        self.Asel.Bind(wx.EVT_CHECKBOX, self.trueorfalse)
        self.Bsel.Bind(wx.EVT_CHECKBOX, self.trueorfalse)
        self.elecsave = wx.Button(self, label='Save', size=(50, 20))
        self.elecsave.Bind(wx.EVT_BUTTON, self.routinesaveelec)
        hbox6.AddMany([(sq6_1, 1, wx.EXPAND), (self.Asel, 1, wx.EXPAND), (self.Bsel, 1, wx.EXPAND), (self.elecsave, 1, wx.EXPAND)])

        #format sizers
        evbox.AddMany([(hbox0, 1, wx.EXPAND), (hbox1, 1, wx.EXPAND), (hbox2, 1, wx.EXPAND), (hbox3, 1, wx.EXPAND),
                       (hbox4, 1, wx.EXPAND), (hbox5, 1, wx.EXPAND), (hbox6, 1, wx.EXPAND)])
        hbox.AddMany([(evbox, 1, wx.EXPAND)])
        elecvbox.Add(hbox, 1, wx.EXPAND)

        #CREATE OPTICAL PANEL###########################################################################################

        #create optical panel sizer and necessary hboxes and vboxes
        sb1 = wx.StaticBox(self, label='Optical')
        opticvbox = wx.StaticBoxSizer(sb1, wx.VERTICAL)
        opvbox = wx.BoxSizer(wx.VERTICAL)
        opvbox2 = wx.BoxSizer(wx.VERTICAL)
        ophbox = wx.BoxSizer(wx.HORIZONTAL)

        #optical routine select tab
        opt_hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        sq0_2 = wx.StaticText(self, label='Select Routine ')
        self.routineselectopt = wx.ComboBox(self, choices=options, style=wx.CB_READONLY, value='1')
        self.routineselectopt.name = 'routineselectopt'
        self.routineselectopt.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.routinepanel)
        self.routineselectopt.Bind(wx.EVT_COMBOBOX, self.swaproutine)
        opt_hbox0.AddMany([(sq0_2, 1, wx.EXPAND), (self.routineselectopt, 1, wx.EXPAND)])

        #optical start wavelength select
        opt_hbox = wx.BoxSizer(wx.HORIZONTAL)
        st4 = wx.StaticText(self, label='Start (nm)')
        self.startWvlTc = wx.TextCtrl(self)
        self.startWvlTc.SetValue('0')
        opt_hbox.AddMany([(st4, 1, wx.EXPAND), (self.startWvlTc, 1, wx.EXPAND)])

        #optical stop wavelength select
        opt_hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st5 = wx.StaticText(self, label='Stop (nm)')
        self.stopWvlTc = wx.TextCtrl(self)
        self.stopWvlTc.SetValue('0')
        opt_hbox2.AddMany([(st5, 1, wx.EXPAND), (self.stopWvlTc, 1, wx.EXPAND)])

        #optical step size select
        opt_hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        st6 = wx.StaticText(self, label='Step (nm)')
        self.stepWvlTc = wx.TextCtrl(self)
        self.stepWvlTc.SetValue('0')
        opt_hbox3.AddMany([(st6, 1, wx.EXPAND), (self.stepWvlTc, 1, wx.EXPAND)])

        #optical sweep power tab
        opt_hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        sweepPowerSt = wx.StaticText(self, label='Sweep power (dBm)')
        self.sweepPowerTc = wx.TextCtrl(self)
        self.sweepPowerTc.SetValue('0')
        opt_hbox4.AddMany([(sweepPowerSt, 1, wx.EXPAND), (self.sweepPowerTc, 1, wx.EXPAND)])

        #optical Initial range tab
        opt_hbox4_5 = wx.BoxSizer(wx.HORIZONTAL)
        sweepinitialrangeSt = wx.StaticText(self, label='Initial Range (dBm)')
        self.sweepinitialrangeTc = wx.TextCtrl(self)
        self.sweepinitialrangeTc.SetValue('0')
        opt_hbox4_5.AddMany([(sweepinitialrangeSt, 1, wx.EXPAND), (self.sweepinitialrangeTc, 1, wx.EXPAND)])

        #optical range decrement tab
        opt_hbox4_6 = wx.BoxSizer(wx.HORIZONTAL)
        rangedecSt = wx.StaticText(self, label='Range Decrement (dBm)')
        self.rangedecTc = wx.TextCtrl(self)
        self.rangedecTc.SetValue('0')
        opt_hbox4_6.AddMany([(rangedecSt, 1, wx.EXPAND), (self.rangedecTc, 0, wx.EXPAND)])

        #optical sweep speed tab
        opt_hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        st7 = wx.StaticText(self, label='Sweep speed')
        sweepSpeedOptions = ['80 nm/s', '40 nm/s', '20 nm/s', '10 nm/s', '5 nm/s', '0.5 nm/s', 'auto']
        self.sweepSpeedCb = wx.ComboBox(self, choices=sweepSpeedOptions, style=wx.CB_READONLY, value='auto')
        opt_hbox5.AddMany([(st7, 1, wx.EXPAND), (self.sweepSpeedCb, 1, wx.EXPAND)])

        #optical laser output tab
        opt_hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        st8 = wx.StaticText(self, label='Laser output')
        laserOutputOptions = ['High power', 'Low SSE']
        self.laserOutputCb = wx.ComboBox(self, choices=laserOutputOptions, style=wx.CB_READONLY, value='High power')
        opt_hbox6.AddMany([(st8, 1, wx.EXPAND), (self.laserOutputCb, 1, wx.EXPAND)])

        #optical number of scans tab
        opt_hbox7 = wx.BoxSizer(wx.HORIZONTAL)
        st9 = wx.StaticText(self, label='Number of scans')
        numSweepOptions = ['1', '2', '3']
        self.numSweepCb = wx.ComboBox(self, choices=numSweepOptions, style=wx.CB_READONLY, value='1')
        opt_hbox7.AddMany([(st9, 1, wx.EXPAND), (self.numSweepCb, 1, wx.EXPAND)])

        #optical save box, to save parameters to temporary list
        optsavebox = wx.BoxSizer(wx.HORIZONTAL)
        self.optsave = wx.Button(self, label='Save', size=(120, 25))
        self.optsave.Bind(wx.EVT_BUTTON, self.routinesaveopt)
        optsavebox.AddMany([((1,1),1), (self.optsave, 0, wx.EXPAND)])

        #format sizers
        opvbox0 = wx.BoxSizer(wx.HORIZONTAL)
        opvbox0.AddMany([(opt_hbox0, 1, wx.EXPAND)])
        opvbox.AddMany([(opt_hbox, 1, wx.EXPAND), (opt_hbox2, 1, wx.EXPAND), (opt_hbox3, 1, wx.EXPAND), (opt_hbox4, 1, wx.EXPAND), (opt_hbox4_5, 1, wx.EXPAND)])
        opvbox2.AddMany([(opt_hbox5, 1, wx.EXPAND), (opt_hbox6, 1, wx.EXPAND), (opt_hbox7, 1, wx.EXPAND), (opt_hbox4_6, 1, wx.EXPAND)])
        ophbox.AddMany([(opvbox, 0, wx.EXPAND), (opvbox2, 0, wx.EXPAND)])
        opticvbox.AddMany([(opvbox0, 0, wx.EXPAND), ((0,0),1), (ophbox, 0, wx.EXPAND), ((1,1), 1), (optsavebox, 0, wx.EXPAND)])

        ##CREATE SET WAVELENGTH, VOLTAGE SWEEP BOX######################################################################

        #initialize sizers
        sb_2 = wx.StaticBox(self, label='Set Wavelength, Electrical sweep')
        elecvbox2 = wx.StaticBoxSizer(sb_2, wx.VERTICAL)
        hboxsetw = wx.BoxSizer(wx.HORIZONTAL)
        evbox2 = wx.BoxSizer(wx.VERTICAL)
        tophbox2 = wx.BoxSizer(wx.HORIZONTAL)

        #set wavelength, routine select tab
        hbox0_2 = wx.BoxSizer(wx.HORIZONTAL)
        sq0_1_2 = wx.StaticText(self, label='Select Routine ')
        self.routineselectsetw = wx.ComboBox(self, choices=options, style=wx.CB_READONLY, value='1')
        self.routineselectsetw.name = 'routineselectsetw'
        self.routineselectsetw.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.routinepanel)
        self.routineselectsetw.Bind(wx.EVT_COMBOBOX, self.swaproutine)
        hbox0_2.AddMany([(sq0_1_2, 1, wx.EXPAND), (self.routineselectsetw, 1, wx.EXPAND)])

        #set wavelength, independant variable checkboxes
        hbox1_2 = wx.BoxSizer(wx.HORIZONTAL)
        sq1_1_2 = wx.StaticText(self, label='Select Independant Variable: ')
        self.voltsel2 = wx.CheckBox(self, label='Voltage', pos=(20, 20))
        self.voltsel2.SetValue(False)
        self.currentsel2 = wx.CheckBox(self, label='Current', pos=(20, 20))
        self.currentsel2.SetValue(False)
        self.voltsel2.Bind(wx.EVT_CHECKBOX, self.trueorfalse)
        self.currentsel2.Bind(wx.EVT_CHECKBOX, self.trueorfalse)
        hbox1_2.AddMany([(sq1_1_2, 1, wx.EXPAND), (self.voltsel2, 1, wx.EXPAND), (self.currentsel2, 1, wx.EXPAND)])

        #set wavelength, voltage and current maximum select
        hbox2_2 = wx.BoxSizer(wx.HORIZONTAL)
        sw1_2 = wx.StaticText(self, label='Set Max:')
        self.maxsetvoltage2 = wx.TextCtrl(self)
        self.maxsetvoltage2.SetValue('V')
        self.maxsetvoltage2.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        self.maxsetvoltage2.SetForegroundColour(wx.Colour(211, 211, 211))
        self.maxsetcurrent2 = wx.TextCtrl(self)
        self.maxsetcurrent2.SetValue('mA')
        self.maxsetcurrent2.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        self.maxsetcurrent2.SetForegroundColour(wx.Colour(211, 211, 211))
        hbox2_2.AddMany([(sw1_2, 1, wx.EXPAND), (self.maxsetvoltage2, 1, wx.EXPAND), (self.maxsetcurrent2, 1, wx.EXPAND)])

        #set wavelength, voltage and current minimum select
        hbox3_2 = wx.BoxSizer(wx.HORIZONTAL)
        sw2_2 = wx.StaticText(self, label='Set Min:')
        self.minsetcurrent2 = wx.TextCtrl(self)
        self.minsetcurrent2.SetValue('mA')
        self.minsetcurrent2.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        self.minsetcurrent2.SetForegroundColour(wx.Colour(211, 211, 211))
        self.minsetvoltage2 = wx.TextCtrl(self)
        self.minsetvoltage2.SetValue('V')
        self.minsetvoltage2.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        self.minsetvoltage2.SetForegroundColour(wx.Colour(211, 211, 211))
        hbox3_2.AddMany([(sw2_2, 1, wx.EXPAND), (self.minsetvoltage2, 1, wx.EXPAND), (self.minsetcurrent2, 1, wx.EXPAND)])

        #set wavelength, voltage and current resolution set
        hbox4_2 = wx.BoxSizer(wx.HORIZONTAL)
        sw3_2 = wx.StaticText(self, label='Set Resolution:')
        self.resovoltage2 = wx.TextCtrl(self)
        self.resovoltage2.SetValue('V')
        self.resovoltage2.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        self.resovoltage2.SetForegroundColour(wx.Colour(211, 211, 211))
        self.resocurrent2 = wx.TextCtrl(self)
        self.resocurrent2.SetValue('mA')
        self.resocurrent2.Bind(wx.EVT_SET_FOCUS, self.cleartext)
        self.resocurrent2.SetForegroundColour(wx.Colour(211, 211, 211))
        hbox4_2.AddMany([(sw3_2, 1, wx.EXPAND), (self.resovoltage2, 1, wx.EXPAND), (self.resocurrent2, 1, wx.EXPAND)])

        #set wavelength, plot type checkboxes
        hbox5_2 = wx.BoxSizer(wx.HORIZONTAL)
        sh2_2 = wx.StaticText(self, label='Plot Type:')
        self.typesel2 = wx.CheckBox(self, label='IV/VI', pos=(20, 20))
        self.typesel2.SetValue(False)
        self.type2sel2 = wx.CheckBox(self, label='RV/RI', pos=(20, 20))
        self.type2sel2.SetValue(False)
        self.type3sel2 = wx.CheckBox(self, label='PV/PI', pos=(20, 20))
        self.type3sel2.SetValue(False)
        hbox5_2.AddMany([(sh2_2, 1, wx.EXPAND), (self.typesel2, 1, wx.EXPAND), (self.type2sel2, 1, wx.EXPAND),
                         (self.type3sel2, 1, wx.EXPAND)])

        #set wavelength, select smu channel and save button
        hbox6_2 = wx.BoxSizer(wx.HORIZONTAL)
        sq6_2 = wx.StaticText(self, label='Select SMU Channel: ')
        self.Asel2 = wx.CheckBox(self, label='A', pos=(20, 20))
        self.Asel2.SetValue(False)
        self.Bsel2 = wx.CheckBox(self, label='B', pos=(20, 20))
        self.Bsel2.SetValue(False)
        self.Asel2.Bind(wx.EVT_CHECKBOX, self.trueorfalse)
        self.Bsel2.Bind(wx.EVT_CHECKBOX, self.trueorfalse)
        self.setwsave = wx.Button(self, label='Save', size=(50, 20))
        self.setwsave.Bind(wx.EVT_BUTTON, self.routinesavesetw)
        hbox6_2.AddMany([(sq6_2, 1, wx.EXPAND), (self.Asel2, 1, wx.EXPAND), (self.Bsel2, 1, wx.EXPAND), (self.setwsave, 1, wx.EXPAND)])

        #set wavelength, wavelength select
        hbox7_2 = wx.BoxSizer(wx.HORIZONTAL)
        wavesetst = wx.StaticText(self, label='Wavelengths (nm)')
        self.wavesetTc2 = wx.TextCtrl(self)
        self.wavesetTc2.SetValue('0')
        hbox7_2.AddMany([(wavesetst, 1, wx.EXPAND), (self.wavesetTc2, 1, wx.EXPAND)])

        #set wavelength, format sizers
        evbox2.AddMany([(hbox0_2, 1, wx.EXPAND), (hbox1_2, 1, wx.EXPAND), (hbox2_2, 1, wx.EXPAND),
                        (hbox3_2, 1, wx.EXPAND), (hbox4_2, 1, wx.EXPAND), (hbox5_2, 1, wx.EXPAND),
                        (hbox7_2, 1, wx.EXPAND), (hbox6_2, 1, wx.EXPAND)])
        hboxsetw.AddMany([(evbox2, 1, wx.EXPAND)])
        elecvbox2.Add(hboxsetw, 1, wx.EXPAND)

        #SET VOLTAGE SWEEP WAVELENGTH###################################################################################

        #create set voltage, wavelength sweep sizer
        sb1_2 = wx.StaticBox(self, label='Set Electrical, Wavelength Sweep')
        opticvbox_2 = wx.StaticBoxSizer(sb1_2, wx.VERTICAL)
        opvbox_2 = wx.BoxSizer(wx.VERTICAL)
        opvbox2_2 = wx.BoxSizer(wx.VERTICAL)
        ophbox_2 = wx.BoxSizer(wx.HORIZONTAL)

        #set voltage, routine select tab
        hbox0_2_2 = wx.BoxSizer(wx.HORIZONTAL)
        sq0_1_2_2 = wx.StaticText(self, label='Select Routine ')
        self.routineselectsetv = wx.ComboBox(self, choices=options, style=wx.CB_READONLY, value='1')
        self.routineselectsetv.name = 'routineselectsetv'
        self.routineselectsetv.SetItems(options)
        self.routineselectsetv.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.routinepanel)
        self.routineselectsetv.Bind(wx.EVT_COMBOBOX, self.swaproutine)
        hbox0_2_2.AddMany([(sq0_1_2_2, 1, wx.EXPAND), (self.routineselectsetv, 1, wx.EXPAND)])

        #set voltage, wavelength start select
        opt_hbox_2 = wx.BoxSizer(wx.HORIZONTAL)
        st4_2 = wx.StaticText(self, label='Start (nm)')
        self.startWvlTc2 = wx.TextCtrl(self)
        self.startWvlTc2.SetValue('0')
        opt_hbox_2.AddMany([(st4_2, 1, wx.EXPAND), (self.startWvlTc2, 1, wx.EXPAND)])

        #set voltage, wavelength stop select
        opt_hbox2_2 = wx.BoxSizer(wx.HORIZONTAL)
        st5_2 = wx.StaticText(self, label='Stop (nm)')
        self.stopWvlTc2 = wx.TextCtrl(self)
        self.stopWvlTc2.SetValue('0')
        opt_hbox2_2.AddMany([(st5_2, 1, wx.EXPAND), (self.stopWvlTc2, 1, wx.EXPAND)])

        #set voltage, step size select
        opt_hbox3_2 = wx.BoxSizer(wx.HORIZONTAL)
        st6_2 = wx.StaticText(self, label='Step (nm)')
        self.stepWvlTc2 = wx.TextCtrl(self)
        self.stepWvlTc2.SetValue('0')
        opt_hbox3_2.AddMany([(st6_2, 1, wx.EXPAND), (self.stepWvlTc2, 1, wx.EXPAND)])

        #set voltage, sweep power select
        opt_hbox4_2 = wx.BoxSizer(wx.HORIZONTAL)
        sweepPowerSt2 = wx.StaticText(self, label='Sweep power (dBm)')
        self.sweepPowerTc2 = wx.TextCtrl(self)
        self.sweepPowerTc2.SetValue('0')
        opt_hbox4_2.AddMany([(sweepPowerSt2, 1, wx.EXPAND), (self.sweepPowerTc2, 1, wx.EXPAND)])

        #set voltage, initial range select
        opt_hbox4_5_2 = wx.BoxSizer(wx.HORIZONTAL)
        sweepinitialrangeSt2 = wx.StaticText(self, label='Initial Range (dBm)')
        self.sweepinitialrangeTc2 = wx.TextCtrl(self)
        self.sweepinitialrangeTc2.SetValue('0')
        opt_hbox4_5_2.AddMany([(sweepinitialrangeSt2, 1, wx.EXPAND), (self.sweepinitialrangeTc2, 1, wx.EXPAND)])

        #set voltage, range decrement select
        opt_hbox4_6_2 = wx.BoxSizer(wx.HORIZONTAL)
        rangedecSt2 = wx.StaticText(self, label='Range Decrement (dBm)')
        self.rangedecTc2 = wx.TextCtrl(self)
        self.rangedecTc2.SetValue('0')
        opt_hbox4_6_2.AddMany([(rangedecSt2, 1, wx.EXPAND), (self.rangedecTc2, 1, wx.EXPAND)])

        #set voltage sweep speed tab
        opt_hbox5_2 = wx.BoxSizer(wx.HORIZONTAL)
        st7_2 = wx.StaticText(self, label='Sweep speed')
        sweepSpeedOptions2 = ['80 nm/s', '40 nm/s', '20 nm/s', '10 nm/s', '5 nm/s', '0.5 nm/s', 'auto']
        self.sweepSpeedCb2 = wx.ComboBox(self, choices=sweepSpeedOptions2, style=wx.CB_READONLY, value='auto')
        opt_hbox5_2.AddMany([(st7_2, 1, wx.EXPAND), (self.sweepSpeedCb2, 1, wx.EXPAND)])

        #set voltage laser output tab
        opt_hbox6_2 = wx.BoxSizer(wx.HORIZONTAL)
        st8_2 = wx.StaticText(self, label='Laser output')
        laserOutputOptions2 = ['High power', 'Low SSE']
        self.laserOutputCb2 = wx.ComboBox(self, choices=laserOutputOptions2, style=wx.CB_READONLY, value='High power')
        opt_hbox6_2.AddMany([(st8_2, 1, wx.EXPAND), (self.laserOutputCb2, 1, wx.EXPAND)])

        #set voltage number of scans tab
        opt_hbox7_2 = wx.BoxSizer(wx.HORIZONTAL)
        st9_2 = wx.StaticText(self, label='Number of scans')
        numSweepOptions2 = ['1', '2', '3']
        self.numSweepCb2 = wx.ComboBox(self, choices=numSweepOptions2, style=wx.CB_READONLY, value='1')
        opt_hbox7_2.AddMany([(st9_2, 1, wx.EXPAND), (self.numSweepCb2, 1, wx.EXPAND)])

        #set voltage, voltage selection
        opt_hbox8_2 = wx.BoxSizer(wx.HORIZONTAL)
        voltagesetst = wx.StaticText(self, label='Voltages (V)')
        self.voltagesetTc2 = wx.TextCtrl(self)
        self.voltagesetTc2.SetValue('0')
        opt_hbox8_2.AddMany([(voltagesetst, 1, wx.EXPAND), (self.voltagesetTc2, 1, wx.EXPAND)])

        #set voltage SMU channel selection checkboxes
        opt_hbox9_2 = wx.BoxSizer(wx.HORIZONTAL)
        sq9_2 = wx.StaticText(self, label='Select SMU Channel: ')
        self.Asel3 = wx.CheckBox(self, label='A', pos=(20, 20))
        self.Asel3.SetValue(False)
        self.Bsel3 = wx.CheckBox(self, label='B', pos=(20, 20))
        self.Bsel3.SetValue(False)
        self.Asel3.Bind(wx.EVT_CHECKBOX, self.trueorfalse)
        self.Bsel3.Bind(wx.EVT_CHECKBOX, self.trueorfalse)
        opt_hbox9_2.AddMany([(sq9_2, 1, wx.EXPAND), (self.Asel3, 1, wx.EXPAND), (self.Bsel3, 1, wx.EXPAND)])

        #set voltage save button
        opt_hbox10_2 = wx.BoxSizer(wx.HORIZONTAL)
        self.setvsave = wx.Button(self, label='Save', size=(120, 25))
        self.setvsave.Bind(wx.EVT_BUTTON, self.routinesavesetv)
        opt_hbox10_2.AddMany([((1, 1), 1), (self.setvsave, 0, wx.EXPAND)])

        #format set voltage sizers
        opvbox_2.AddMany([(opt_hbox_2, 1, wx.EXPAND), (opt_hbox2_2, 1, wx.EXPAND), (opt_hbox3_2, 1, wx.EXPAND), (opt_hbox4_2, 1, wx.EXPAND), (opt_hbox4_5_2, 1, wx.EXPAND)])
        opvbox2_2.AddMany([(opt_hbox5_2, 1, wx.EXPAND), (opt_hbox6_2, 1, wx.EXPAND), (opt_hbox7_2, 1, wx.EXPAND), (opt_hbox8_2, 0, wx.EXPAND), (opt_hbox4_6_2, 0, wx.EXPAND)])
        ophbox_2.AddMany([(opvbox_2, 1, wx.EXPAND), (opvbox2_2, 1, wx.EXPAND)])
        ophbox_2_2 = wx.BoxSizer(wx.HORIZONTAL)
        ophbox_2_2.AddMany([(hbox0_2_2, 1, wx.EXPAND)])
        opticvbox_2.AddMany([(ophbox_2_2, 0, wx.EXPAND), (ophbox_2, 0, wx.EXPAND), (opt_hbox9_2, 0, wx.EXPAND), (opt_hbox10_2, 0, wx.EXPAND)])

        #format all sizers
        tophbox.AddMany([(elecvbox, 0, wx.EXPAND), (opticvbox, 1, wx.EXPAND)])
        tophbox2.AddMany([(elecvbox2, 0, wx.EXPAND), (opticvbox_2, 1, wx.EXPAND)])
        highestvbox = wx.BoxSizer(wx.VERTICAL)
        #highesthbox = wx.BoxSizer(wx.HORIZONTAL)
        highestvbox.AddMany([(tophbox, 1, wx.EXPAND), (tophbox2, 1, wx.EXPAND)])
        #highesthbox.AddMany([(routineselect, 0, wx.EXPAND), (highestvbox, 1, wx.EXPAND)])
        self.SetSizer(highestvbox)


    def cleartext(self, event):
        """
        Clears the text in the textctrl boxes on user clicking the box
        Parameters
        ----------
        event : The event triggered when the user clicks the textctrl box

        Returns
        -------

        """
        e = event.GetEventObject()
        if e.GetValue() == 'mA' or e.GetValue() == 'mV' or e.GetValue() == 'V':
            e.SetValue('')
            e.SetForegroundColour(wx.Colour(0, 0, 0))
        if e.GetValue() == '':
            e.SetForegroundColour(wx.Colour(0, 0, 0))
        event.Skip()


    def setnumroutine(self, event):
        """

        :param event:
        :type event:
        :return:
        :rtype:
        """
        c = event.GetEventObject()

        optionsblank = []
        #if c == self.elecroutine:

        if c.GetValue() != '':
            options = []
            for x in range(int(c.GetValue())):
                x = x + 1
                options.append(str(x))

            print(c.name)
            if c.name == 'elecroutine':
                self.routineselectelec.SetItems(options)
                self.elecvolt = [''] * int(c.GetValue())
                self.eleccurrent = [''] * int(c.GetValue())
                self.elecvmax = [''] * int(c.GetValue())
                self.elecvmin = ['']* int(c.GetValue())
                self.elecimin = [''] * int(c.GetValue())
                self.elecimax = [''] * int(c.GetValue())
                self.elecires = [''] * int(c.GetValue())
                self.elecvres = [''] * int(c.GetValue())
                self.eleciv = [''] * int(c.GetValue())
                self.elecrv = [''] * int(c.GetValue())
                self.elecpv = [''] * int(c.GetValue())
                self.elecchannelA = [''] * int(c.GetValue())
                self.elecchannelB = [''] * int(c.GetValue())
                self.elecflagholder = [''] * int(c.GetValue())

            if c.name == 'optroutine':
                self.routineselectopt.SetItems(options)
                self.start = [''] * int(c.GetValue())
                self.stop = [''] * int(c.GetValue())
                self.step = [''] * int(c.GetValue())
                self.sweeppow = [''] * int(c.GetValue())
                self.sweepsped = [''] * int(c.GetValue())
                self.laserout = [''] * int(c.GetValue())
                self.numscans = [''] * int(c.GetValue())
                self.initialran = [''] * int(c.GetValue())
                self.rangedecre = [''] * int(c.GetValue())
                self.opticflagholder = [''] * int(c.GetValue())

            if c.name == 'setwroutine':
                self.routineselectsetw.SetItems(options)
                self.setwvolt = [''] * int(c.GetValue())
                self.setwcurrent = [''] * int(c.GetValue())
                self.setwvmax = [''] * int(c.GetValue())
                self.setwvmin = [''] * int(c.GetValue())
                self.setwimin = [''] * int(c.GetValue())
                self.setwimax = [''] * int(c.GetValue())
                self.setwires = [''] * int(c.GetValue())
                self.setwvres = [''] * int(c.GetValue())
                self.setwiv = [''] * int(c.GetValue())
                self.setwrv = [''] * int(c.GetValue())
                self.setwpv = [''] * int(c.GetValue())
                self.setwchannelA = [''] * int(c.GetValue())
                self.setwchannelB = [''] * int(c.GetValue())
                self.setwwavelengths = [''] * int(c.GetValue())
                self.setwflagholder = [''] * int(c.GetValue())

            if c.name == 'setvroutine':
                self.routineselectsetv.SetItems(options)
                self.setvstart = [''] * int(c.GetValue())
                self.setvstop = [''] * int(c.GetValue())
                self.setvstep = [''] * int(c.GetValue())
                self.setvsweeppow = [''] * int(c.GetValue())
                self.setvsweepsped = [''] * int(c.GetValue())
                self.setvlaserout = [''] * int(c.GetValue())
                self.setvnumscans = [''] * int(c.GetValue())
                self.setvinitialran = [''] * int(c.GetValue())
                self.setvrangedecre = [''] * int(c.GetValue())
                self.setvchannelA = [''] * int(c.GetValue())
                self.setvchannelB = [''] * int(c.GetValue())
                self.setvvoltages = [''] * int(c.GetValue())
                self.setvflagholder = [''] * int(c.GetValue())

        if c.GetValue() == '':
            if c.name == 'elecroutine':
                self.routineselectelec.SetItems(optionsblank)
            if c.name == 'optroutine':
                self.routineselectopt.SetItems(optionsblank)
            if c.name == 'setwroutine':
                self.routineselectsetw.SetItems(optionsblank)
            if c.name == 'setvroutine':
                self.routineselectsetv.SetItems(optionsblank)


    def trueorfalse(self, event):
        """
        For selections that can only be one or the other this function deselects the other option on the selection of one of the parameters
        Parameters
        ----------
        event : event triggered by any one of the parameters that are exclusive

        Returns
        -------

        """
        e = event.GetEventObject()

        if e == self.Asel and self.Asel.GetValue() == True:
            self.Bsel.SetValue(False)

        if e == self.Asel2 and self.Asel2.GetValue() == True:
            self.Bsel2.SetValue(False)

        if e == self.Asel3 and self.Asel3.GetValue() == True:
            self.Bsel3.SetValue(False)

        if e == self.Bsel and self.Bsel.GetValue() == True:
            self.Asel.SetValue(False)

        if e == self.Bsel2 and self.Bsel2.GetValue() == True:
            self.Asel2.SetValue(False)

        if e == self.Bsel3 and self.Bsel3.GetValue() == True:
            self.Asel3.SetValue(False)

        if e == self.voltsel and self.voltsel.GetValue() == True:
            self.currentsel.SetValue(False)

        if e == self.currentsel and self.currentsel.GetValue() == True:
            self.voltsel.SetValue(False)

        if e == self.voltsel2 and self.voltsel2.GetValue() == True:
            self.currentsel2.SetValue(False)

        if e == self.currentsel2 and self.currentsel2.GetValue() == True:
            self.voltsel2.SetValue(False)

        event.Skip()


    def routinesaveelec(self, event):
        """
        When the user hits the electrical panel save button this function saves the data in the panel to a list with a size equal to the number of routines
        Parameters
        ----------
        event : the event triggered by user clicking the save button in the electrical panel

        Returns
        -------

        """
        if self.routineselectelec.GetValue() != '':
            value = int(self.routineselectelec.GetValue()) - 1
            self.elecvolt[value] = self.voltsel.GetValue()
            self.eleccurrent[value] = self.currentsel.GetValue()
            self.elecvmax[value] = self.maxsetvoltage.GetValue()
            self.elecvmin[value] = self.minsetvoltage.GetValue()
            self.elecimin[value] = self.minsetcurrent.GetValue()
            self.elecimax[value] = self.maxsetcurrent.GetValue()
            self.elecires[value] = self.resocurrent.GetValue()
            self.elecvres[value] = self.resovoltage.GetValue()
            self.eleciv[value] = self.typesel.GetValue()
            self.elecrv[value] = self.type2sel.GetValue()
            self.elecpv[value] = self.type3sel.GetValue()
            self.elecchannelA[value] = self.Asel.GetValue()
            self.elecchannelB[value] = self.Bsel.GetValue()
            self.elecflagholder[value] = True
            print('Electrical routines temporarily saved')


    def routinesaveopt(self, event):
        """
        When the user hits the optical panel save button this function saves the data in the panel to a list with a size equal to the number of routines
        Parameters
        ----------
        event : event triggered by user clicking the save button in the optical panel

        Returns
        -------

        """
        if self.routineselectopt.GetValue() != '':
            value = int(self.routineselectopt.GetValue()) - 1
            self.start[value] = self.startWvlTc.GetValue()
            self.stop[value] = self.stopWvlTc.GetValue()
            self.step[value] = self.stepWvlTc.GetValue()
            self.sweeppow[value] = self.sweepPowerTc.GetValue()
            self.sweepsped[value] = self.sweepSpeedCb.GetValue()
            self.laserout[value] = self.laserOutputCb.GetValue()
            self.numscans[value] = self.numSweepCb.GetValue()
            self.initialran[value] = self.sweepinitialrangeTc.GetValue()
            self.rangedecre[value] = self.rangedecTc.GetValue()
            self.opticflagholder[value] = True
            print('Optical routines temporarily saved')


    def routinesavesetw(self, event):
        """
        When the user hits the set wavelength, voltage sweep panel save button this function saves the data in the
        panel to a list with a size equal to the number of routines
        Parameters
        ----------
        event : event triggered by user clicking the save button in the set wavelength, voltage sweep panel

        Returns
        -------

        """

        if self.routineselectsetw.GetValue() != '':
            value = int(self.routineselectsetw.GetValue()) - 1
            self.setwvolt[value] = self.voltsel2.GetValue()
            self.setwcurrent[value] = self.currentsel2.GetValue()
            self.setwvmax[value] = self.maxsetvoltage2.GetValue()
            self.setwvmin[value] = self.minsetvoltage2.GetValue()
            self.setwimin[value] = self.minsetcurrent2.GetValue()
            self.setwimax[value] = self.maxsetcurrent2.GetValue()
            self.setwires[value] = self.resocurrent2.GetValue()
            self.setwvres[value] = self.resovoltage2.GetValue()
            self.setwiv[value] = self.typesel2.GetValue()
            self.setwrv[value] = self.type2sel2.GetValue()
            self.setwpv[value] = self.type3sel2.GetValue()
            self.setwchannelA[value] = self.Asel2.GetValue()
            self.setwchannelB[value] = self.Bsel2.GetValue()
            self.setwwavelengths[value] = self.wavesetTc2.GetValue()
            self.setwflagholder[value] = True
            print('Set wavelength, voltage sweep routines temporarily saved')


    def routinesavesetv(self, event):
        """
        When the user hits the set voltage, wavelength sweep panel save button this function saves the data in the
        panel to a list with a size equal to the number of routines
        Parameters
        ----------
        event : event triggered by user clicking the save button in the set voltage, wavelength sweep panel

        Returns
        -------

        """

        if self.routineselectsetv.GetValue() != '':
            value = int(self.routineselectsetv.GetValue()) - 1
            self.setvstart[value] = self.startWvlTc2.GetValue()
            self.setvstop[value] = self.stopWvlTc2.GetValue()
            self.setvstep[value] = self.stepWvlTc2.GetValue()
            self.setvsweeppow[value] = self.sweepPowerTc2.GetValue()
            self.setvsweepsped[value] = self.sweepSpeedCb2.GetValue()
            self.setvlaserout[value] = self.laserOutputCb2.GetValue()
            self.setvnumscans[value] = self.numSweepCb2.GetValue()
            self.setvinitialran[value] = self.sweepinitialrangeTc2.GetValue()
            self.setvrangedecre[value] = self.rangedecTc2.GetValue()
            self.setvvoltages[value] = self.voltagesetTc2.GetValue()
            self.setvchannelA[value] = self.Asel3.GetValue()
            self.setvchannelB[value] = self.Bsel3.GetValue()
            self.setvflagholder[value] = True
            print('Set voltage, wavelength sweep routines temporarily saved')


    def routinepanel(self, event):
        """
        When the user opens the routine select dropdown this function saves the data in the panel to a list with a size
        equal to the number of routines
        Parameters
        ----------
        event : the event triggered by the user opening the dropdown selection on any of the panels

        Returns
        -------

        """
        e = event.GetEventObject()
        name = e.name


        if name == 'routineselectelec':

            if self.routineselectelec.GetValue() != '':
                value = int(self.routineselectelec.GetValue()) - 1
                self.elecvolt[value] = self.voltsel.GetValue()
                self.eleccurrent[value] = self.currentsel.GetValue()
                self.elecvmax[value] = self.maxsetvoltage.GetValue()
                self.elecvmin[value] = self.minsetvoltage.GetValue()
                self.elecimin[value] = self.minsetcurrent.GetValue()
                self.elecimax[value] = self.maxsetcurrent.GetValue()
                self.elecires[value] = self.resocurrent.GetValue()
                self.elecvres[value] = self.resovoltage.GetValue()
                self.eleciv[value] = self.typesel.GetValue()
                self.elecrv[value] = self.type2sel.GetValue()
                self.elecpv[value] = self.type3sel.GetValue()
                self.elecchannelA[value] = self.Asel.GetValue()
                self.elecchannelB[value] = self.Bsel.GetValue()
                self.elecflagholder[value] = True

        if name == 'routineselectopt':

            if self.routineselectopt.GetValue() != '':
                value = int(self.routineselectopt.GetValue()) - 1
                self.start[value] = self.startWvlTc.GetValue()
                self.stop[value] = self.stopWvlTc.GetValue()
                self.step[value] = self.stepWvlTc.GetValue()
                self.sweeppow[value] = self.sweepPowerTc.GetValue()
                self.sweepsped[value] = self.sweepSpeedCb.GetValue()
                self.laserout[value] = self.laserOutputCb.GetValue()
                self.numscans[value] = self.numSweepCb.GetValue()
                self.initialran[value] = self.sweepinitialrangeTc.GetValue()
                self.rangedecre[value] = self.rangedecTc.GetValue()
                self.opticflagholder[value] = True


        if name == 'routineselectsetw':

            if self.routineselectsetw.GetValue() != '':
                value = int(self.routineselectsetw.GetValue()) - 1
                self.setwvolt[value] = self.voltsel2.GetValue()
                self.setwcurrent[value] = self.currentsel2.GetValue()
                self.setwvmax[value] = self.maxsetvoltage2.GetValue()
                self.setwvmin[value] = self.minsetvoltage2.GetValue()
                self.setwimin[value] = self.minsetcurrent2.GetValue()
                self.setwimax[value] = self.maxsetcurrent2.GetValue()
                self.setwires[value] = self.resocurrent2.GetValue()
                self.setwvres[value] = self.resovoltage2.GetValue()
                self.setwiv[value] = self.typesel2.GetValue()
                self.setwrv[value] = self.type2sel2.GetValue()
                self.setwpv[value] = self.type3sel2.GetValue()
                self.setwchannelA[value] = self.Asel2.GetValue()
                self.setwchannelB[value] = self.Bsel2.GetValue()
                self.setwwavelengths[value] = self.wavesetTc2.GetValue()
                self.setwflagholder[value] = True

        if name == 'routineselectsetv':

            if self.routineselectsetv.GetValue() != '':
                value = int(self.routineselectsetv.GetValue()) - 1
                self.setvstart[value] = self.startWvlTc2.GetValue()
                self.setvstop[value] = self.stopWvlTc2.GetValue()
                self.setvstep[value] = self.stepWvlTc2.GetValue()
                self.setvsweeppow[value] = self.sweepPowerTc2.GetValue()
                self.setvsweepsped[value] = self.sweepSpeedCb2.GetValue()
                self.setvlaserout[value] = self.laserOutputCb2.GetValue()
                self.setvnumscans[value] = self.numSweepCb2.GetValue()
                self.setvinitialran[value] = self.sweepinitialrangeTc2.GetValue()
                self.setvrangedecre[value] = self.rangedecTc2.GetValue()
                self.setvvoltages[value] = self.voltagesetTc2.GetValue()
                self.setvchannelA[value] = self.Asel3.GetValue()
                self.setvchannelB[value] = self.Bsel3.GetValue()
                self.setvflagholder[value] = True

        event.Skip()


    def swaproutine(self, event):
        """
        When the user selects a new routine number in the dropdown menu of the routine panels, this function swaps the
        saved routine values shown
        Parameters
        ----------
        event : the event triggered by the user opening the dropdown selection on any of the panels

        Returns
        -------

        """
        """
        When the user selects a new routine number in the dropdown menu of the routine panels, this function swaps the saved routine values shown
        :param event:
        :type event:
        :return:
        :rtype:
        """

        c = event.GetEventObject()
        name = c.name

        if name == 'routineselectelec':

            if self.routineselectelec.GetValue() != '':
                value = int(self.routineselectelec.GetValue()) - 1
                self.voltsel.SetValue(bool(self.elecvolt[value]))# = self.elecvolt[value]
                self.currentsel.SetValue(bool(self.eleccurrent[value]))
                self.maxsetvoltage.SetValue(self.elecvmax[value])
                self.minsetvoltage.SetValue(self.elecvmin[value])
                self.minsetcurrent.SetValue(self.elecimin[value])
                self.maxsetcurrent.SetValue(self.elecimax[value])
                self.resocurrent.SetValue(self.elecires[value])
                self.resovoltage.SetValue(self.elecvres[value])
                self.typesel.SetValue(bool(self.eleciv[value]))
                self.type2sel.SetValue(bool(self.elecrv[value]))
                self.type3sel.SetValue(bool(self.elecpv[value]))
                self.Asel.SetValue(bool(self.elecchannelA[value]))
                self.Bsel.SetValue(bool(self.elecchannelB[value]))

        if name == 'routineselectopt':

            if self.routineselectopt.GetValue() != '':
                value = int(self.routineselectopt.GetValue()) - 1
                self.startWvlTc.SetValue(self.start[value])
                self.stopWvlTc.SetValue(self.stop[value])
                self.stepWvlTc.SetValue(self.step[value])
                self.sweepPowerTc.SetValue(self.sweeppow[value])
                self.sweepSpeedCb.SetValue(self.sweepsped[value])
                self.laserOutputCb.SetValue(self.laserout[value])
                self.numSweepCb.SetValue(self.numscans[value])
                self.sweepinitialrangeTc.SetValue(self.initialran[value])
                self.rangedecTc.SetValue(self.rangedecre[value])

        if name == 'routineselectsetw':

            if self.routineselectsetw.GetValue() != '':
                value = int(self.routineselectsetw.GetValue()) - 1
                self.voltsel2.SetValue(bool(self.setwvolt[value]))
                self.currentsel2.SetValue(bool(self.setwcurrent[value]))
                self.maxsetvoltage2.SetValue(self.setwvmax[value])
                self.minsetvoltage2.SetValue(self.setwvmin[value])
                self.minsetcurrent2.SetValue(self.setwimin[value])
                self.maxsetcurrent2.SetValue(self.setwimax[value])
                self.resocurrent2.SetValue(self.setwires[value])
                self.resovoltage2.SetValue(self.setwvres[value])
                self.typesel2.SetValue(bool(self.setwiv[value]))
                self.type2sel2.SetValue(bool(self.setwrv[value]))
                self.type3sel2.SetValue(bool(self.setwpv[value]))
                self.Asel2.SetValue(bool(self.setwchannelA[value]))
                self.Bsel2.SetValue(bool(self.setwchannelB[value]))
                self.wavesetTc2.SetValue(self.setwwavelengths[value])

        if name == 'routineselectsetv':

            if self.routineselectsetv.GetValue() != '':
                value = int(self.routineselectsetv.GetValue()) - 1
                self.startWvlTc2.SetValue(self.setvstart[value])
                self.stopWvlTc2.SetValue(self.setvstop[value])
                self.stepWvlTc2.SetValue(self.setvstep[value])
                self.sweepPowerTc2.SetValue(self.setvsweeppow[value])
                self.sweepSpeedCb2.SetValue(self.setvsweepsped[value])
                self.laserOutputCb2.SetValue(self.setvlaserout[value])
                self.numSweepCb2.SetValue(self.setvnumscans[value])
                self.sweepinitialrangeTc2.SetValue(self.setvinitialran[value])
                self.rangedecTc2.SetValue(self.setvrangedecre[value])
                self.Asel3.SetValue(bool(self.setvchannelA[value]))
                self.Bsel3.SetValue(bool(self.setvchannelB[value]))
                self.voltagesetTc2.SetValue(self.setvvoltages[value])


if __name__ == '__main__':
    app = wx.App(redirect=False)
    testParameters()
    app.MainLoop()
    app.Destroy()
    del app