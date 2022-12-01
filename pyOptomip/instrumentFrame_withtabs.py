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
from outputlogPanel import outputlogPanel
import sys
from fineAlign import fineAlign
from fineAlignPanel import fineAlignPanel
import traceback
from logWriter import logWriter, logWriterError
from autoMeasurePanel import autoMeasurePanel
from autoMeasure import autoMeasure
import myMatplotlibPanel
from TestParameters_revised import TopPanel
import cv2
import threading
import time
from documentationpanel import docPanel
from CameraPanel import cameraPanel
from instr_status import statusPanel
from SMUFrame import resistancePanel


class instrumentFrame_withtabs(wx.Frame):

    def __init__(self, parent, instList):
        """

        Args:
            parent:
            instList:

        Returns:
            object:
        """
        displaySize = wx.DisplaySize()
        super(instrumentFrame_withtabs, self).__init__(parent, title='Instrument Control',
                                                       size=(displaySize[0] * 5 / 8.0, displaySize[1] * 3 / 4.0))

        self.instList = instList  # List of connected instruments
        try:
            self.InitUI()
        except Exception as e:  # If GUI cannot open, disconnect all instruments
            for inst in self.instList:
                inst.disconnect()
            self.Destroy()
            raise
        self.Centre()
        self.Show()

    def InitUI(self):
        """

        """
        self.Bind(wx.EVT_CLOSE, self.OnExitApp)
        self.p = wx.Panel(self)
        nb = wx.Notebook(self.p)

        self.laserWithDetector = []
        self.laser = []
        self.opticalStage = []
        self.electricalStage = []
        self.SMU = []

        """Classify instruments"""
        for inst in self.instList:
            if inst.isLaser:
                if inst.isDetect:
                    self.laserWithDetector = inst
                else:
                    self.laser = inst

            if inst.isMotor:
                if inst.isElec:
                    self.electricalStage = inst
                else:
                    self.opticalStage = inst

            if inst.isSMU:
                self.SMU = inst

        """Connect to top and side cameras"""
        #self.camera = cameraPanel.Camera
        self.camera = self.Camera()
        self.camera.start()
        #self.side_camera = self.Camera(0)
        #self.side_camera.start()

        """Create the tab windows"""
        tab1 = self.HomeTab(nb, self.laserWithDetector, self.opticalStage, self.electricalStage, self.camera, self.instList, self.SMU)
        if self.SMU:
            tab2 = self.ElectricalTab(nb, self.SMU)
        tab3 = self.OpticalTab(nb, self.laserWithDetector)
        tab4 = self.AutoMeasureTab(nb, self.laserWithDetector, self.opticalStage, self.electricalStage, self.SMU,
                                   self.camera)
        if (self.laserWithDetector and self.opticalStage ) or (self.SMU and self.electricalStage):
            tab5 = self.TestingParametersTab(nb, tab4.autoMeasurePanel)

        """Add the windows to tabs and name them."""
        nb.AddPage(tab1, "Home")
        if self.SMU:
            nb.AddPage(tab2, "Electrical")
        if self.laserWithDetector:
            nb.AddPage(tab3, "Optical")
        if (self.laserWithDetector and self.opticalStage) or (self.SMU and self.electricalStage):
            nb.AddPage(tab4, "Automated Measurements")
            nb.AddPage(tab5, "Testing Parameters")

        """Set notebook in a sizer to create the layout"""
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(nb, 1, wx.ALL | wx.EXPAND)

        """Add output log"""
        self.log = outputlogPanel(self.p)
        sizer.Add(self.log, 1, wx.ALL | wx.EXPAND)
        self.p.SetSizer(sizer)
        sys.stdout = logWriter(self.log)
        sys.stderr = logWriterError(self.log)

    def motorFound(self):
        """

        Returns:

        """
        motorFound = False
        for inst in self.instList:
            motorFound = motorFound | inst.isMotor
        return motorFound

    def laserFound(self):
        """

        Returns:

        """
        laserFound = False
        for inst in self.instList:
            laserFound = laserFound | inst.isLaser
        return laserFound

    def getLasers(self):
        """

        Returns:

        """
        laserList = []
        for inst in self.instList:
            if inst.isLaser:
                laserList.append(inst)
        return laserList

    def getMotors(self):
        """

        Returns:

        """
        motorList = []
        for inst in self.instList:
            if inst.isMotor:
                motorList.append(inst)
        return motorList

    def OnExitApp(self, event):
        """

        Args:
            event:
        """
        self.camera.cap.release()
        cv2.destroyAllWindows()
        for inst in self.instList:
            inst.disconnect()
        self.Destroy()

    class HomeTab(wx.Panel):
        def __init__(self, parent, laserWithDetector, opticalStage, electricalStage, camera, instr, SMU):
            """

            Args:
                parent:
                instList:
            """
            wx.Panel.__init__(self, parent)
            vbox = wx.BoxSizer(wx.VERTICAL)
            self.hbox = wx.BoxSizer(wx.HORIZONTAL)
            homeVbox = wx.BoxSizer(wx.VERTICAL)
            homeVbox2 = wx.BoxSizer(wx.VERTICAL)
            self.camera = camera
            #self.side_camera = side_camera

            if opticalStage:
                opticalStagePanel = opticalStage.panelClass(self, opticalStage)
                homeVbox.Add(opticalStagePanel, proportion=0, border=0, flag=wx.EXPAND)
                if laserWithDetector:
                    self.fineAlign = fineAlign(laserWithDetector, opticalStage)
                    try:
                        self.fineAlignPanel = fineAlignPanel(self, self.fineAlign)
                    except Exception as e:
                        dial = wx.MessageDialog(None,
                                                'Could not initiate instrument control. ' + traceback.format_exc(),
                                                'Error', wx.ICON_ERROR)
                        dial.ShowModal()
                    homeVbox.Add(self.fineAlignPanel, proportion=0, flag=wx.EXPAND)
            if electricalStage:
                electricalStagePanel = electricalStage.panelClass(self, electricalStage)
                homeVbox.Add(electricalStagePanel, proportion=0, border=0, flag=wx.EXPAND)
                if SMU:

                    smuPanel = resistancePanel(self, SMU)
                    smuHbox = wx.BoxSizer(wx.HORIZONTAL)
                    smuHbox.Add(smuPanel, proportion=1, border=0, flag=wx.EXPAND)
                    homeVbox.Add(smuHbox, 1, wx.EXPAND)
            if laserWithDetector:
                detectorPanel = laserWithDetector.panelClass(self, laserWithDetector, False, True)
                detectHbox = wx.BoxSizer(wx.HORIZONTAL)
                detectHbox.Add(detectorPanel,proportion=1, border=0, flag=wx.EXPAND)
                docpanel = docPanel(self)
                detectHbox.Add(docpanel, 1, wx.EXPAND)
                homeVbox.Add(detectHbox, 1, wx.EXPAND)



            camerapanel = cameraPanel(self, camera)
            homeVbox2.Add(camerapanel, 0, wx.EXPAND)

            statuspanel = statusPanel(self, instr)
            homeVbox2.Add(statuspanel, 1, wx.EXPAND)

            #docpanel = docPanel(self)
            #homeVbox2.Add(docpanel, 1, wx.EXPAND)

            self.hbox.AddMany([(homeVbox, 1, wx.EXPAND), (homeVbox2, 1, wx.EXPAND)])

            vbox.Add(self.hbox, 3, wx.EXPAND)
            self.SetSizer(vbox)
            self.Layout()
            self.Show()


    class ElectricalTab(wx.Panel):
        def __init__(self, parent, SMU):
            """

            Args:
                parent:
                instList:
            """
            wx.Panel.__init__(self, parent)
            vbox = wx.BoxSizer(wx.VERTICAL)
            hbox = wx.BoxSizer(wx.HORIZONTAL)

            if SMU:
                smuPanel = SMU.panelClass(self, SMU)
                hbox.Add(smuPanel, proportion=1, border=0, flag=wx.EXPAND)

            vbox.Add(hbox, 3, wx.EXPAND)
            self.SetSizer(vbox)
            self.Layout()
            self.Show()


    class OpticalTab(wx.Panel):
        def __init__(self, parent, laserWithDetector):
            """

            Args:
                parent:
                instList:
            """
            wx.Panel.__init__(self, parent)
            vbox = wx.BoxSizer(wx.VERTICAL)

            if laserWithDetector:
                laserPanel = laserWithDetector.panelClass(self, laserWithDetector, True, False)
                laserVbox = wx.BoxSizer(wx.VERTICAL)
                laserVbox.Add(laserPanel, proportion=0, border=0, flag=wx.EXPAND)
                vbox.Add(laserVbox, 3, wx.EXPAND)

            self.SetSizer(vbox)
            self.Layout()
            self.Show()


    class AutoMeasureTab(wx.Panel):
        def __init__(self, parent, laser, motorOpt, motorElec, SMU, camera):
            """

            Args:
                parent:
                instList:
            """
            wx.Panel.__init__(self, parent)
            vbox = wx.BoxSizer(wx.VERTICAL)
            hbox = wx.BoxSizer(wx.HORIZONTAL)
            if laser and motorOpt or SMU and motorElec:
                self.fineAlign = fineAlign(laser, motorOpt)
                try:
                    self.fineAlignPanel = fineAlignPanel(self, self.fineAlign)
                except Exception as e:
                    dial = wx.MessageDialog(None, 'Could not initiate instrument control. ' + traceback.format_exc(),
                                            'Error', wx.ICON_ERROR)
                    dial.ShowModal()

                self.graph = myMatplotlibPanel.myMatplotlibPanel(self)
                self.autoMeasure = autoMeasure(laser, motorOpt, motorElec, SMU, self.fineAlign, self.graph)

                self.autoMeasurePanel = autoMeasurePanel(self, self.autoMeasure, camera)

                vbox.Add(self.autoMeasurePanel, proportion=0, flag=wx.EXPAND)

                vbox.Add(hbox, 3, wx.EXPAND)
                self.SetSizer(vbox)


    class TestingParametersTab(wx.Panel):
        def __init__(self, parent, automeasurePanel):
            """

            Args:
                parent:
                instList:
            """
            wx.Panel.__init__(self, parent)
            vbox = wx.BoxSizer(wx.VERTICAL)
            hbox = wx.BoxSizer(wx.HORIZONTAL)
            self.testingParameters = TopPanel(self, automeasurePanel)
            vbox.Add(self.testingParameters, proportion=0, flag=wx.EXPAND)
            vbox.Add(hbox, 3, wx.EXPAND)
            self.SetSizer(vbox)

    class Camera(threading.Thread):

        # def connect(self, *args, **kwargs):
        # self.cap = cv2.VideoCapture(0)

        def __init__(self):
            threading.Thread.__init__(self)
            self.camID = 1

        def run(self, *args, **kwargs):
            self.cap = cv2.VideoCapture(self.camID)
            self.show = False
            self.a = 0
            self.b = 0
            self.record = 0
            self.frame_width = int(self.cap.get(3))
            self.frame_height = int(self.cap.get(4))
            self.cap.set(cv2.CAP_PROP_FPS, 10)
            self.recordflag = False
            self.switchcamera = False

            while self.cap.isOpened():
                if self.show:
                    ret, frame = self.cap.read()

                    if self.camID == 1:
                        frame = cv2.flip(frame, 1)

                    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                    h, s, v = cv2.split(hsv)

                    s = s + self.a

                    hsv = cv2.merge([h, s, v])
                    frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
                    self.cap.set(cv2.CAP_PROP_EXPOSURE, self.b)
                    cv2.imshow('Webcam', frame)

                    if self.recordflag:
                        self.result.write(frame)

                    if self.switchcamera:
                        self.cap.release()
                        cv2.destroyAllWindows()
                        if self.camID == 0:
                            self.camID = 1
                        elif self.camID == 1:
                            self.camID = 0
                        self.cap = cv2.VideoCapture(self.camID)
                        self.switchcamera = False

                else:
                    self.cap.release()
                    # Destroy all the windows
                    cv2.destroyAllWindows()
                    while not self.show:
                        time.sleep(1)
                        pass
                    self.cap = cv2.VideoCapture(self.camID)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # After the loop release the cap object
            self.cap.release()
            # Destroy all the windows
            cv2.destroyAllWindows()

        def isOpened(self):
            return self.show

        def saturation(self, value):
            self.a = value

        def exposure(self, value):
            self.b = value

        def startrecord(self, path):

            self.record = self.record + 1

            filename = (path + "\Arraycapture_" + str(self.record) + ".avi")
            print(filename)

            size = (self.frame_width, self.frame_height)

            self.result = cv2.VideoWriter(filename,
                                          cv2.VideoWriter_fourcc(*'MJPG'),
                                          10, size)
            self.recordflag = True
            print("Recording Started")

        def stoprecord(self):

            self.recordflag = False
            print("Recording Stopped")

        def close(self):
            self.show = False

        def open(self):
            self.show = True
