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

        self.instrumentList = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        self.instrumentList.InsertColumn(0, 'Instruments', width=200)
        #self.instrumentList.Bind(wx.EVT_LIST_ITEM_CHECKED, self.routinechecklistchecked)
        #self.instrumentList.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.routinechecklistunchecked)
        self.connectList = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        self.connectList.InsertColumn(0, 'Status', width=150)
        #self.connectList.Bind(wx.EVT_LIST_ITEM_CHECKED, self.subroutinechecked)
        #self.connectList.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.subroutineunchecked)

        hboxstatus.AddMany([(self.instrumentList, 1, wx.EXPAND), (self.connectList, 1, wx.EXPAND)])

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.refreshBtn = wx.Button(self, label='Refresh', size=(50, 20))
        self.refreshBtn.Bind(wx.EVT_BUTTON, self.refresh_btn)

        hbox.AddMany([(self.refreshBtn, 1, wx.EXPAND|wx.BOTTOM)])

        vboxstatus.AddMany([(hboxstatus, 0, wx.EXPAND), (hbox, 1, wx.EXPAND|wx.BOTTOM)])

        self.SetSizer(vboxstatus)

    def refresh_btn(self, event):
        print(self.instr)
        rm = pyvisa.ResourceManager()
        i = rm.list_resources()
        print(i)

        self.instrumentList.DeleteAllItems()
        self.connectList.DeleteAllItems()

        for ii, inst in enumerate(self.instr):
            self.instrumentList.InsertItem(ii, str(inst.name + ':' + inst.visaName))

        for ii, instrument in enumerate(self.instr):
            self.visaName = instrument.visaName
            self.inst = rm.open_resource(self.visaName)
            print(self.inst.query("*IDN?\n"))
            response = self.inst.query("*IDN?\n")
            print(response)
            if response == _____: #test in lab
                self.connectList.InsertItem(ii, 'Connected')
            else:
                self.connectList.InsertItem(ii, 'Error')

        #for a in range(len(inst)):

          #  devname = inst[a].name
          #  if devname == 'Dummy CorvusEco' or devname == 'Dummy Laser':
           #     pass
           # elif devname == 'SMU':
            #    inst[a].testconnection(rm)
                #print(inst[a].query('*IDN?'))

           # string = string + '\n' + str(devname)

       # self.devices.SetLabel(string)







