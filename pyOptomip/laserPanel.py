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
import myMatplotlibPanel


class tlsPanel(wx.Panel):
    """ Panel which contains controls used for controlling the laser"""

    sweepSpeedMap = dict(
        [('80 nm/s', '80nm'), ('40 nm/s', '40nm'), ('20 nm/s', '20nm'), ('10 nm/s', '10nm'), ('5 nm/s', '5nm'),
         ('0.5 nm/s', '0.5nm'), ('auto', 'auto')])
    laserOutputMap = dict([('High power', 'highpower'), ('Low SSE', 'lowsse')])
    laserNumSweepMap = dict([('1', 1), ('2', 2), ('3', 3)])

    def __init__(self, parent, laser, graphPanel):
        super(tlsPanel, self).__init__(parent)
        self.devName = 'Laser'
        self.laser = laser
        self.graphPanel = graphPanel
        self.InitUI()

    def InitUI(self):

        vboxOuter = wx.BoxSizer(wx.VERTICAL)

        sbCW = wx.StaticBox(self, label='CW Settings')
        vboxCW = wx.StaticBoxSizer(sbCW, wx.VERTICAL)

        hbox12 = wx.BoxSizer(wx.HORIZONTAL)
        st10 = wx.StaticText(self, label='Laser slot:')

        laserSelectChoices = ['auto']
        laserSelectChoices.extend(list(map(str, self.laser.findTLSSlots())))

        self.laserSelectCb = wx.ComboBox(self, choices=laserSelectChoices, style=wx.CB_READONLY,
                                         value=laserSelectChoices[0])
        hbox12.AddMany([(st10, 1, wx.EXPAND), (self.laserSelectCb, 1, wx.EXPAND)])
        ###
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)

        st1 = wx.StaticText(self, label='Laser status:')

        self.laserOnBtn = wx.Button(self, label='ON', size=(50, 20))
        self.laserOnBtn.Bind(wx.EVT_BUTTON, self.OnButton_LaserOn)

        self.laserOffBtn = wx.Button(self, label='OFF', size=(50, 20))
        self.laserOffBtn.Bind(wx.EVT_BUTTON, self.OnButton_LaserOff)

        hbox1.AddMany([(st1, 2, wx.EXPAND), (self.laserOffBtn, 1, wx.EXPAND), (self.laserOnBtn, 1, wx.EXPAND)])
        ###
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        st10 = wx.StaticText(self, label='Laser output')

        cwLaserOutputSettings = ['High power', 'Low SSE']
        self.cwLaserOutputCb = wx.ComboBox(self, choices=cwLaserOutputSettings, style=wx.CB_READONLY,
                                           value='High power')

        self.btn_setCwOutput = wx.Button(self, label='Set', size=(50, 20))
        self.btn_setCwOutput.Bind(wx.EVT_BUTTON, self.OnButton_cwOutputSet)
        hbox2.AddMany(
            [(st10, 3, wx.EXPAND), (self.cwLaserOutputCb, 2, wx.EXPAND), (self.btn_setCwOutput, 1, wx.EXPAND)])
        ###
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)

        st2 = wx.StaticText(self, label='Power (dBm)')

        self.laserPowerTc = wx.TextCtrl(self)
        self.laserPowerTc.SetValue('0')

        self.btn2 = wx.Button(self, label='Set', size=(50, 20))
        self.btn2.Bind(wx.EVT_BUTTON, self.OnButton_PowerSet)

        hbox3.AddMany([(st2, 3, wx.EXPAND), (self.laserPowerTc, 2, wx.EXPAND), (self.btn2, 1, wx.EXPAND)])
        ###
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)

        st_wavelength = wx.StaticText(self, label='Wavelength (nm)')

        self.tc_wavelength = wx.TextCtrl(self)
        self.tc_wavelength.SetValue('0')

        self.btn_wavelength = wx.Button(self, label='Set', size=(50, 20))
        self.btn_wavelength.Bind(wx.EVT_BUTTON, self.OnButton_WavelengthSet)

        hbox4.AddMany(
            [(st_wavelength, 3, wx.EXPAND), (self.tc_wavelength, 2, wx.EXPAND), (self.btn_wavelength, 1, wx.EXPAND)])

        vboxCW.AddMany([(hbox12, 0, wx.EXPAND), (hbox1, 0, wx.EXPAND), (hbox2, 0, wx.EXPAND), (hbox3, 0, wx.EXPAND),
                        (hbox4, 0, wx.EXPAND)]);
        ###
        sbSweep = wx.StaticBox(self, label='Sweep Settings');
        vboxSweep = wx.StaticBoxSizer(sbSweep, wx.VERTICAL)

        hbox5 = wx.BoxSizer(wx.HORIZONTAL)

        st4 = wx.StaticText(self, label='Start (nm)')

        self.startWvlTc = wx.TextCtrl(self)
        self.startWvlTc.SetValue('0')

        hbox5.AddMany([(st4, 1, wx.EXPAND), (self.startWvlTc, 1, wx.EXPAND)])
        ###
        hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        st5 = wx.StaticText(self, label='Stop (nm)')

        self.stopWvlTc = wx.TextCtrl(self)
        self.stopWvlTc.SetValue('0')

        hbox6.AddMany([(st5, 1, wx.EXPAND), (self.stopWvlTc, 1, wx.EXPAND)])
        ###
        hbox7 = wx.BoxSizer(wx.HORIZONTAL)

        st6 = wx.StaticText(self, label='Step (nm)')

        self.stepWvlTc = wx.TextCtrl(self)
        self.stepWvlTc.SetValue('0')

        hbox7.AddMany([(st6, 1, wx.EXPAND), (self.stepWvlTc, 1, wx.EXPAND)])
        ###
        hbox8 = wx.BoxSizer(wx.HORIZONTAL)

        sweepPowerSt = wx.StaticText(self, label='Sweep power (dBm)')

        self.sweepPowerTc = wx.TextCtrl(self)
        self.sweepPowerTc.SetValue('0')

        hbox8.AddMany([(sweepPowerSt, 1, wx.EXPAND), (self.sweepPowerTc, 1, wx.EXPAND)])
        ###
        hbox9 = wx.BoxSizer(wx.HORIZONTAL)

        st7 = wx.StaticText(self, label='Sweep speed')

        sweepSpeedOptions = ['80 nm/s', '40 nm/s', '20 nm/s', '10 nm/s', '5 nm/s', '0.5 nm/s', 'auto']
        self.sweepSpeedCb = wx.ComboBox(self, choices=sweepSpeedOptions, style=wx.CB_READONLY, value='auto')
        hbox9.AddMany([(st7, 1, wx.EXPAND), (self.sweepSpeedCb, 1, wx.EXPAND)])
        ###
        hbox10 = wx.BoxSizer(wx.HORIZONTAL)

        st8 = wx.StaticText(self, label='Laser output')

        laserOutputOptions = ['High power', 'Low SSE']
        self.laserOutputCb = wx.ComboBox(self, choices=laserOutputOptions, style=wx.CB_READONLY, value='High power')
        hbox10.AddMany([(st8, 1, wx.EXPAND), (self.laserOutputCb, 1, wx.EXPAND)])

        ##
        hbox11 = wx.BoxSizer(wx.HORIZONTAL)

        st9 = wx.StaticText(self, label='Number of scans')

        numSweepOptions = ['1', '2', '3']
        self.numSweepCb = wx.ComboBox(self, choices=numSweepOptions, style=wx.CB_READONLY, value='1')
        hbox11.AddMany([(st9, 1, wx.EXPAND), (self.numSweepCb, 1, wx.EXPAND)])

        self.sweepBtn = wx.Button(self, label='Sweep', size=(50, 20))
        self.sweepBtn.Bind(wx.EVT_BUTTON, self.OnButton_Sweep)

        vboxSweep.AddMany([(hbox5, 0, wx.EXPAND), (hbox6, 0, wx.EXPAND), (hbox7, 0, wx.EXPAND), (hbox8, 0, wx.EXPAND), \
                           (hbox9, 0, wx.EXPAND), (hbox10, 0, wx.EXPAND), (hbox11, 0, wx.EXPAND),
                           (self.sweepBtn, 0, wx.ALIGN_CENTER)]);

        vboxOuter.AddMany([(vboxCW, 0, wx.EXPAND), (vboxSweep, 0, wx.EXPAND)])
        # fgs.AddGrowableCol(0, 1)
        # hbox.Add(fgs, proportion=1, flag=wx.ALL, border=15)
        self.SetSizer(vboxOuter)

    def getSelectedLaserSlot(self):
        return self.laserSelectCb.GetValue()

    def OnButton_LaserOn(self, event):
        self.laser.setTLSState('on', slot=self.getSelectedLaserSlot())

    def OnButton_LaserOff(self, event):
        self.laser.setTLSState('off', slot=self.getSelectedLaserSlot())

    def OnButton_PowerSet(self, event):
        self.laser.setTLSPower(float(self.laserPowerTc.GetValue()), slot=self.getSelectedLaserSlot())

    def OnButton_WavelengthSet(self, event):
        self.laser.setTLSWavelength(float(self.tc_wavelength.GetValue()) / 1e9, slot=self.getSelectedLaserSlot())

    def OnButton_cwOutputSet(self, event):
        self.laser.setTLSOutput(self.laserOutputMap[self.cwLaserOutputCb.GetValue()], slot=self.getSelectedLaserSlot())

    def copySweepSettings(self):
        """ Copies the current sweep settings in the interface to the laser object."""
        self.laser.sweepStartWvl = float(self.startWvlTc.GetValue()) / 1e9;
        self.laser.sweepStopWvl = float(self.stopWvlTc.GetValue()) / 1e9;
        self.laser.sweepStepWvl = float(self.stepWvlTc.GetValue()) / 1e9;
        self.laser.sweepSpeed = self.sweepSpeedMap[self.sweepSpeedCb.GetValue()];
        self.laser.sweepUnit = 'dBm';
        self.laser.sweepPower = float(self.sweepPowerTc.GetValue());
        self.laser.sweepLaserOutput = self.laserOutputMap[self.laserOutputCb.GetValue()]
        self.laser.sweepNumScans = self.laserNumSweepMap[self.numSweepCb.GetValue()]
        self.laser.sweepInitialRange = float(self.detectorPanel.initialRangeTc.GetValue());
        self.laser.sweepRangeDecrement = float(self.detectorPanel.sweepRangeDecTc.GetValue());
        activeDetectors = self.detectorPanel.getActiveDetectors()
        if len(activeDetectors) == 0:
            raise Exception('Cannot perform sweep. No active detectors selected.');
        self.laser.activeSlotIndex = activeDetectors

    def drawGraph(self, wavelength, power):
        self.graphPanel.axes.cla()
        self.graphPanel.axes.plot(wavelength, power)
        self.graphPanel.axes.ticklabel_format(useOffset=False)
        self.graphPanel.canvas.draw()

    def haltDetTimer(self):
        timer = self.detectorPanel.timer
        if timer.IsRunning():
            timer.Stop()

    def startDetTimer(self):
        timer = self.detectorPanel.timer
        if not timer.IsRunning():
            timer.Start()

    def OnButton_Sweep(self, event):
        self.haltDetTimer()
        try:
            self.copySweepSettings()
            self.lastSweepWavelength, self.lastSweepPower = self.laser.sweep();
            self.graphPanel.canvas.sweepResultDict = {}
            self.graphPanel.canvas.sweepResultDict['wavelength'] = self.lastSweepWavelength
            self.graphPanel.canvas.sweepResultDict['power'] = self.lastSweepPower

            self.drawGraph(self.lastSweepWavelength * 1e9, self.lastSweepPower)
        except Exception as e:
            print(e)
        self.laser.setAutorangeAll()
        self.startDetTimer()


class laserTopPanel(wx.Panel):
    # Panel which contains the panels used for controling the laser and detectors. It also
    # contains the graph.
    def __init__(self, parent, laser, detectflag, showGraph):
        super(laserTopPanel, self).__init__(parent)

        self.detectflag = detectflag
        self.showGraph = showGraph
        self.laser = laser;
        self.laser.ctrlPanel = self  # So the laser knows what panel is controlling it
        self.InitUI()

    def InitUI(self):
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        if self.showGraph:
            self.graph = myMatplotlibPanel.myMatplotlibPanel(self)
            hbox.Add(self.graph, flag=wx.EXPAND, border=0, proportion=1)
        else:
            self.graph = myMatplotlibPanel.myMatplotlibPanel(self)

        # self.laserPanel = laserPanel(self, self.laser, self.graph, self.detectflag)

        if self.detectflag:
            # self.laserPanel = tlsPanel(self, self.laser, self.graph)
            self.detectorPanelLst = list()

            # for ii in xrange(self.laser.getNumPWMChannels()):
            self.detectorPanel = detectorPanel(self, self.laser.getNumPWMChannels(), self.laser, self.detectflag)
            # self.laserPanel.detectorPanel = self.detectorPanel
            hbox.Add(self.detectorPanel, flag=wx.LEFT | wx.TOP | wx.EXPAND, border=0, proportion=0)
        else:
            self.laserPanel = laserPanel(self, self.laser, self.graph, self.detectflag)
            hbox.Add(self.laserPanel, flag=wx.LEFT | wx.TOP | wx.EXPAND, border=0, proportion=0)

        self.SetSizer(hbox)


class laserPanel(wx.Panel):
    """ Panel which contains the panel used to control the tunable laser and the panel to
	control the detectors. """

    def __init__(self, parent, laser, graph, detectflag):
        super(laserPanel, self).__init__(parent)
        self.detectflag = detectflag
        self.graphPanel = graph
        self.laser = laser
        self.InitUI()

    def InitUI(self):
        sb = wx.StaticBox(self, label='Laser')
        vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)

        if self.detectflag:
            self.laserPanel = tlsPanel(self, self.laser, self.graphPanel)
            self.detectorPanelLst = list()

            # for ii in xrange(self.laser.getNumPWMChannels()):
            self.detectorPanel = detectorPanel(self, self.laser.getNumPWMChannels(), self.laser, self.detectflag)
            self.laserPanel.detectorPanel = self.detectorPanel

            vbox.Add(self.detectorPanel, border=0, proportion=0, flag=wx.EXPAND)
        else:
            self.laserPanel = tlsPanel(self, self.laser, self.graphPanel)
            self.detectorPanelLst = list()

            # for ii in xrange(self.laser.getNumPWMChannels()):
            self.detectorPanel = detectorPanel(self, self.laser.getNumPWMChannels(), self.laser, self.detectflag)
            self.laserPanel.detectorPanel = self.detectorPanel
            vbox.Add(self.laserPanel, flag=wx.LEFT | wx.TOP | wx.EXPAND, border=0, proportion=0)

            # self.detectorPanelLst = list()

            # for ii in xrange(self.laser.getNumPWMChannels()):
            # self.detectorPanel = detectorPanel(self, self.laser.getNumPWMChannels(), self.laser)
            # self.laserPanel.detectorPanel = self.detectorPanel

            # vbox.Add(self.detectorPanel, border=0, proportion=0, flag=wx.EXPAND)

        # sl = wx.StaticLine(self.panel);
        self.SetSizer(vbox)

    def OnClose(self, event):
        self.laserPanel.Destroy()
        self.detectorPanel.Destroy()
        self.Destroy()


class detectorPanel(wx.Panel):
    """ Panel containing the individual panels for each detector. """

    def __init__(self, parent, numDet, laser, detectflag):
        super(detectorPanel, self).__init__(parent)
        self.numDet = numDet
        self.laser = laser
        self.detectflag = detectflag
        self.InitUI()

    def InitUI(self):

        # font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        # font.SetPointSize(12)

        if self.detectflag:

            sbDet = wx.StaticBox(self, label='Detector Settings')

            vbox = wx.StaticBoxSizer(sbDet, wx.VERTICAL)
            hbox = wx.BoxSizer(wx.HORIZONTAL)

            self.initialRangeSt = wx.StaticText(self, label='Initial range (dBm)')
            # self.initialRangeSt.SetFont(font)
            hbox.Add(self.initialRangeSt, proportion=1, flag=wx.ALIGN_LEFT)

            self.initialRangeTc = wx.TextCtrl(self, size=(40, 20))
            self.initialRangeTc.SetValue('-20')
            hbox.Add(self.initialRangeTc, proportion=0, flag=wx.EXPAND | wx.RIGHT, border=15)

            self.sweepRangeDecSt = wx.StaticText(self, label='Range dec. (dBm)')
            # self.sweepRangeDecSt.SetFont(font)
            hbox.Add(self.sweepRangeDecSt, proportion=1, flag=wx.ALIGN_LEFT)

            self.sweepRangeDecTc = wx.TextCtrl(self, size=(40, 20))
            self.sweepRangeDecTc.SetValue('20')
            hbox.Add(self.sweepRangeDecTc, proportion=0, flag=wx.EXPAND)

            vbox.Add(hbox, proportion=0, flag=wx.EXPAND, border=0)

            sl = wx.StaticLine(self)
            vbox.Add(sl, proportion=0, flag=wx.EXPAND)

            self.detectorPanelLst = list()
            for ii, slotInfo in zip(self.laser.pwmSlotIndex, self.laser.pwmSlotMap):
                name = 'Slot %d Det %d' % (slotInfo[0], slotInfo[1] + 1)
                det = individualDetPanel(self, name=name, slot=slotInfo[0], chan=slotInfo[1])
                self.detectorPanelLst.append(det)
                vbox.Add(det, proportion=1, flag=wx.LEFT, border=15)
                sl = wx.StaticLine(self)
                vbox.Add(sl, proportion=0, flag=wx.EXPAND)
            self.SetSizer(vbox)

            self.laser.setAutorangeAll()
            self.timer = wx.Timer(self, wx.ID_ANY)
            self.Bind(wx.EVT_TIMER, self.UpdateAutoMeasurement, self.timer)
            self.timer.Start(1000)

        else:

            self.detectorPanelLst = list()
            for ii, slotInfo in zip(self.laser.pwmSlotIndex, self.laser.pwmSlotMap):
                name = 'Slot %d Det %d' % (slotInfo[0], slotInfo[1] + 1)
                det = individualDetPanel(self, name=name, slot=slotInfo[0], chan=slotInfo[1])
                self.detectorPanelLst.append(det)

            self.laser.setAutorangeAll()
            self.timer = wx.Timer(self, wx.ID_ANY)
            self.Bind(wx.EVT_TIMER, self.UpdateAutoMeasurement, self.timer)
            self.timer.Start(1000)

    def getActiveDetectors(self):
        activeDetectorLst = list();
        for ii, panel in enumerate(self.detectorPanelLst):
            if panel.enableSweepCb.GetValue() == True:
                activeDetectorLst.append(ii)
        return activeDetectorLst

    def UpdateAutoMeasurement(self, event):
        for ii, panel in enumerate(self.detectorPanelLst):
            if panel.autoMeasurementEnabled:
                panel.PowerSt.SetLabel(str(self.laser.readPWM(panel.slot, panel.chan)))

    def OnClose(self, event):
        self.timer.Stop();


class individualDetPanel(wx.Panel):
    """ Panel used to control the settings for one detector. """

    def __init__(self, parent, name='', slot=1, chan=1):
        super(individualDetPanel, self).__init__(parent)
        self.name = name
        self.slot = slot
        self.chan = chan
        self.autoMeasurementEnabled = 0;
        self.InitUI()

    def InitUI(self):

        # font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        # font.SetPointSize(12)

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        fgs = wx.FlexGridSizer(4, 2, 8, 25)

        self.detNameSt = wx.StaticText(self, label=self.name)
        # self.detNameSt.SetFont(font)

        self.autoMeasurementCb = wx.CheckBox(self, label='Auto measurement')
        # self.autoMeasurementCb.SetFont(font)
        self.autoMeasurementCb.Bind(wx.EVT_CHECKBOX, self.OnCheckAutoMeasurement);

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        st1 = wx.StaticText(self, label='Power (dBm):')
        # st1.SetFont(font)
        hbox2.Add(st1, proportion=0)

        self.PowerSt = wx.StaticText(self, label='-100')
        # self.PowerSt.SetFont(font)
        hbox2.Add(self.PowerSt, proportion=0)

        self.enableSweepCb = wx.CheckBox(self, label='Include in sweep')
        self.enableSweepCb.SetValue(False)
        # self.enableSweepCb.SetFont(font)

        fgs.AddMany([(self.detNameSt), (self.enableSweepCb), \
                     (self.autoMeasurementCb), (hbox2, 1, wx.EXPAND)])

        # fgs.AddGrowableCol(0, 1)
        hbox.Add(fgs, proportion=1, flag=wx.ALL, border=0)
        self.SetSizer(hbox)

    def OnCheckAutoMeasurement(self, event):
        if self.autoMeasurementCb.GetValue():
            self.autoMeasurementEnabled = 1;
        else:
            self.autoMeasurementEnabled = 0;
