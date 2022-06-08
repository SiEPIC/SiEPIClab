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
from ctypes import byref, c_float
from wx.lib.activex import ActiveXCtrl


class QontrolMotorCtrl(ActiveXCtrl):
    def __init__(self, parent, COM_id, serialNum, name='Qontrol Motor'):
        wx.lib.activex.ActiveXCtrl.__init__(self, parent, COM_id, name=name)
        self.ctrl.HWSerialNum = serialNum
        self.ctrl.StartCtrl()
        self.chan = 0

    def getPosition(self):
        pos = c_float()
        res = self.ctrl.GetPosition(self.chan, byref(pos))
        self.checkError(res)
        return float(pos.value) * 1000

    def moveRelative(self, offset, wait=True):
        res = self.ctrl.SetRelMoveDist(self.chan, offset / 1000.0)
        self.checkError(res)
        res = self.ctrl.MoveRelative(self.chan, wait)
        self.checkError(res)

    def moveAbsolute(self, offset, wait=True):
        res = self.ctrl.SetAbsMovePos(self.chan, offset / 1000.0)
        self.checkError(res)
        res = self.ctrl.MoveAbsolute(self.chan, wait)
        self.checkError(res)

    def setVelocityParams(self, minVel, maxVel, accel):
        res = self.ctrl.SetVelParams(minVel, accel, maxVel)
        self.checkError(res)

    def checkError(self, err):
        if err == 0:
            return
        else:
            raise Exception("An error occurred")


class QontrolMotor(object):
    name = 'Qontrol Actuator'
    isMotor = True
    isLaser = False

    def __init__(self, serialNum):
        self.COM_id = 'Qontrol'
        self.motorLst = list()
        self.frame = wx.Frame(None, -1, title='Qontrol Motor Control')
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        for num in serialNum:
            motor = QontrolMotorCtrl(self.frame, self.COM_id, serialNum=num)
            hbox.Add(motor, proportion=1, flag=wx.EXPAND)
            self.motorLst.append(motor)

        self.xMotor = self.motorLst[0]
        self.yMotor = self.motorLst[1]

        self.frame.SetSizer(hbox)
        self.frame.Show()

    def moveRelative(self, dx, dy):
        self.xMotor.moveRelative(dx)
        self.yMotor.moveRelative(dy)

    def moveAbsoluteXY(self, x, y):
        self.xMotor.moveAbsolute(x)
        self.yMotor.moveAbsolute(y)

    def getPosition(self):
        xpos = self.xMotor.getPosition()
        ypos = self.yMotor.getPosition()
        return (xpos, ypos)

    def disconnect(self):
        for motor in self.motorLst:
            motor.Destroy()
        self.frame.Destroy()