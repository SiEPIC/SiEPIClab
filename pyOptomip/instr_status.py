import wx
import pyvisa

class statusPanel(wx.Panel):

    def __init__(self, parent, instr):
        super(statusPanel, self).__init__(parent)
        self.instr = instr
        self.InitUI()


    def InitUI(self):
        sbcam = wx.StaticBox(self, label='Instrument Status')
        vboxstatus = wx.StaticBoxSizer(sbcam, wx.VERTICAL)
        hboxstatus = wx.BoxSizer(wx.HORIZONTAL)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        Condev = wx.StaticText(self, label='Connected Devices:')
        hbox.AddMany([(Condev, 1, wx.EXPAND)])

        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.devices = wx.StaticText(self, label='')
        self.hbox1.AddMany([(self.devices, 1, wx.EXPAND)])


        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.refreshBtn = wx.Button(self, label='Refresh', size=(50, 20))
        self.refreshBtn.Bind(wx.EVT_BUTTON, self.refresh_btn)

        hbox2.AddMany([(self.refreshBtn, 1, wx.EXPAND)])


        vboxstatus.AddMany([(hbox, 1, wx.EXPAND), (self.hbox1, 1, wx.EXPAND), (hbox2, 1, wx.EXPAND)])

        self.SetSizer(vboxstatus)

    def refresh_btn(self, event):
        rm = pyvisa.ResourceManager()
        i = rm.list_resources()
        string = ''
        self.devices.SetLabel(string)
        inst = self.instr

        if len(inst) == 0:
            string = 'No instruments connected'

        for a in range(len(inst)):

            devname = inst[a].name
            if devname == 'Dummy CorvusEco' or devname == 'Dummy Laser':
                pass
            else:
                print(inst[a].query('*IDN?'))

            string = string + '\n' + str(devname)

        self.devices.SetLabel(string)







