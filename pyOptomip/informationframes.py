import wx


class infoFrame(wx.Frame):

    def __init__(self, parent, infochecked,):
        """A frame which opens upon clicking the filter button within the auto-measure tab.
        Used to filter which devices are selected within a checklist of electro-optic devices"""
        displaySize = wx.DisplaySize()
        super(infoFrame, self).__init__(parent, title='Information')#,
                                         # size=(displaySize[0] * 3 / 8.0, displaySize[1] * 2 / 4.0))

        try:
            self.infoPanel = infoPanel
            self.infochecked = infochecked
            self.InitUI()
        except Exception as e:
            raise
        self.Centre()
        self.Show()

    def InitUI(self):
        """Layout of the frame"""
        self.Bind(wx.EVT_CLOSE, self.OnExitApp)

        if self.infochecked == 0:
            sbOuter = wx.StaticBox(self, label='Set Voltage Wavelength sweep: Voltage input')
        elif self.infochecked == 1:
            sbOuter = wx.StaticBox(self, label='Scale Adjustment')
        elif self.infochecked == 2:
            sbOuter = wx.StaticBox(self, label='Information')
        elif self.infochecked == 3:
            sbOuter = wx.StaticBox(self, label='Information')
        elif self.infochecked == 4:
            sbOuter = wx.StaticBox(self, label='Information')
        elif self.infochecked == 5:
            sbOuter = wx.StaticBox(self, label='Information')



        vboxOuter = wx.StaticBoxSizer(sbOuter, wx.VERTICAL)

        panel = self.infoPanel(self, self.infochecked)

        vboxOuter.Add(panel, 0, wx.EXPAND)

        self.SetSizer(vboxOuter)

    def OnExitApp(self, event):
        self.Destroy()


class infoPanel(wx.Panel):
    def __init__(self, parent, infochecked):
        """Panel which is used to obtain the necessary parameters to calculate the transformation from
        gds coordinates to motor coordinates. Three devices must be selected and the respective motor
        coordinates saved.

        Args:
            parent: wx Panel
            autoMeasure: The automeasure object used for the automeasure panel"""

        super(infoPanel, self).__init__(parent)
        self.infochecked = infochecked

        self.InitUI()

    def InitUI(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        if self.infochecked == 0:
            entry1 = wx.StaticText(self, label='For set voltage wavelength sweep please enter list of desired voltages seperated by commas')
            entry2 = wx.StaticText(self, label='Ex. 1, 2, 3')
            entry3 = wx.StaticText(self, label='')
            entry4 = wx.StaticText(self, label='')
            entry5 = wx.StaticText(self, label='')
        elif self.infochecked == 1:
            entry1 = wx.StaticText(self, label='The scale adjustment tool is used to adjust the x and y scales of the')
            entry2 = wx.StaticText(self, label='chip stage to account for the slight misalignment of the')
            entry3 = wx.StaticText(self, label='motor axises To use, create electrcial matrix, move chip stage ')
            entry4 = wx.StaticText(self, label='by 2000 in the x direction, move to a device, adjust the x scale')
            entry5 = wx.StaticText(self, label='until the probe aligns perfectly over the device, repeat for y axis')
        elif self.infochecked == 2:
            entry1 = wx.StaticText(self, label='Help')
            entry2 = wx.StaticText(self, label='Help')
            entry3 = wx.StaticText(self, label='Help')
            entry4 = wx.StaticText(self, label='')
            entry5 = wx.StaticText(self, label='')
        elif self.infochecked == 3:
            entry1 = wx.StaticText(self, label='Help')
            entry2 = wx.StaticText(self, label='Help')
            entry3 = wx.StaticText(self, label='Help')
            entry4 = wx.StaticText(self, label='')
            entry5 = wx.StaticText(self, label='')
        elif self.infochecked == 4:
            entry1 = wx.StaticText(self, label='Help')
            entry2 = wx.StaticText(self, label='Help')
            entry3 = wx.StaticText(self, label='Help')
            entry4 = wx.StaticText(self, label='')
            entry5 = wx.StaticText(self, label='')
        elif self.infochecked == 5:
            entry1 = wx.StaticText(self, label='Help')
            entry2 = wx.StaticText(self, label='Help')
            entry3 = wx.StaticText(self, label='Help')
            entry4 = wx.StaticText(self, label='')
            entry5 = wx.StaticText(self, label='')

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(entry1, 1, wx.EXPAND)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(entry2, 1, wx.EXPAND)

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3.Add(entry3, 1, wx.EXPAND)

        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        hbox4.Add(entry4, 1, wx.EXPAND)

        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        hbox5.Add(entry5, 1, wx.EXPAND)

        vbox.AddMany([(hbox1, 0, wx.EXPAND), (hbox2, 0, wx.EXPAND), (hbox3, 0, wx.EXPAND), (hbox4, 0, wx.EXPAND), (hbox5, 0, wx.EXPAND)])

        self.SetSizer(vbox)

