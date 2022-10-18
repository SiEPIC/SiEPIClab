import wx
import cv2
import threading


class cameraPanel(wx.Panel):

    def __init__(self, parent, camera):
        super(cameraPanel, self).__init__(parent)
        self.camera = camera
        self.InitUI()

    def InitUI(self):
        sbcam = wx.StaticBox(self, label='Camera Settings')
        vboxcam = wx.StaticBoxSizer(sbcam, wx.VERTICAL)

        self.hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        self.openBtn = wx.Button(self, label='Open', size=(50, 20))
        self.openBtn.Bind(wx.EVT_BUTTON, self.OpenCamera)

        self.closeBtn = wx.Button(self, label='Close', size=(50, 20))
        self.closeBtn.Bind(wx.EVT_BUTTON, self.CloseCamera)
        self.hbox0.AddMany([(self.openBtn, 1, wx.EXPAND), (self.closeBtn, 1, wx.EXPAND)])

        self.hbox0_5 = wx.BoxSizer(wx.HORIZONTAL)
        self.openSideBtn = wx.Button(self, label='Switch Views', size=(50, 20))
        self.openSideBtn.Bind(wx.EVT_BUTTON, self.OpenSideCamera)

        self.hbox0_5.AddMany([(self.openSideBtn, 1, wx.EXPAND)])

        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        bb = wx.StaticText(self, label='Saturation:')
        self.saturation = wx.Slider(self, value=0, minValue=0, maxValue=254, style=wx.SL_HORIZONTAL)
        self.hbox1.AddMany([(bb, 1, wx.EXPAND), (self.saturation, 1, wx.EXPAND)])
        self.saturation.Bind(wx.EVT_SLIDER, self.saturationchange)

        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        bb2 = wx.StaticText(self, label='Exposure:')
        self.exposure = wx.Slider(self, value=-5, minValue=-10, maxValue=0, style=wx.SL_HORIZONTAL)
        self.hbox2.AddMany([(bb2, 1, wx.EXPAND), (self.exposure, 1, wx.EXPAND)])
        self.exposure.Bind(wx.EVT_SLIDER, self.exposurechange)

        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        bb3 = wx.StaticText(self, label='Recording:')
        self.startBtn = wx.Button(self, label='Start', size=(50, 20))
        self.startBtn.Bind(wx.EVT_BUTTON, self.StartRecording)

        self.stopBtn = wx.Button(self, label='Stop', size=(50, 20))
        self.stopBtn.Bind(wx.EVT_BUTTON, self.StopRecording)

        self.hbox3.AddMany([(bb3, 1, wx.EXPAND), (self.startBtn, 1, wx.EXPAND), (self.stopBtn, 1, wx.EXPAND)])

        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(self, label='Save folder:')
        self.outputFolderTb = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.outputFolderBtn = wx.Button(self, wx.ID_OPEN, size=(50, 20))
        self.outputFolderBtn.Bind(wx.EVT_BUTTON, self.OnButton_SelectOutputFolder)
        self.hbox4.AddMany(
            [(st2, 1, wx.EXPAND), (self.outputFolderTb, 1, wx.EXPAND), (self.outputFolderBtn, 0, wx.EXPAND)])

        vboxcam.AddMany([(self.hbox0, 1, wx.EXPAND), (self.hbox1, 1, wx.EXPAND), (self.hbox2, 1, wx.EXPAND),
                         (self.hbox3, 1, wx.EXPAND), (self.hbox4, 1, wx.EXPAND), (self.hbox0_5, 1, wx.EXPAND)])

        self.SetSizer(vboxcam)


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


    def saturationchange(self, event):
        c = self.saturation.GetValue()
        self.camera.saturation(c)


    def exposurechange(self, event):
        c = self.exposure.GetValue()
        self.camera.exposure(c)


    def StartRecording(self, event):
        print(self.outputFolderTb.GetValue())
        if self.outputFolderTb.GetValue() == "":
            print("Please select save location")
        else:
            self.camera.startrecord(self.outputFolderTb.GetValue())


    def StopRecording(self, event):
        self.camera.stoprecord()


    def OpenCamera(self, event):
        self.camera.open()


    def CloseCamera(self, event):
        self.camera.close()


    def OpenSideCamera(self, event):
        self.camera.switchcamera = True


