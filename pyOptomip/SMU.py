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

"""
Created on Mon Jun 02 10:01:33 2014

@author: Stephen Lin
Last updated: July 15, 2014
"""
# MAIN ISSUES
# The Corvus does not return any errors for many things:
# e.g.: If an axis is not connected but is enabled through the code, everything will still proceed
# however, NONE of any of the axis will move when given the commmand (making it impossible to tell you which axis is not working)
# Corvus will tell you there is an internal error, but it does not give ANY details.


import time
from keithley2600 import Keithley2600
from keithley2600 import Keithley2600Base


class SMUClass():


    name = 'SMU'
    isSMU = True
    isMotor = False
    isLaser = False

    def connect(self, visaName, rm):
        self.k = Keithley2600(visaName)
        self.k.smua.source.output = self.k.smua.OUTPUT_ON  #turns on SMUA

        self.k.apply_voltage(self.k.smua, 0.2)

        #SMUClass.setVoltage(self, 6)
        # SMUClass.setCurrent(1, 0.05, visaName)
        # k.apply_voltage(k.smua, 1)
        v = self.k.smua.measure.v()  # measures and returns the SMUA voltage
        print(v)
        i = self.k.smua.measure.i()
        print(i)

        print('Connected\n')




    def disconnect(self):
        self.k.smua.source.output = self.k.smua.OUTPUT_OFF
        self.k.disconnect()
        print('SMU Disconnected')


    def setVoltage(self, voltage):
        self.k.apply_voltage(self.k.smua, voltage)
        print('Set voltage to ' + str(voltage) + 'V')

    def setCurrent(self, current):
        self.k.apply_current(self.k.smua, current)
        print('Set current to ' + str(current*100) + 'mA')

    def setcurrentlimit(self, currentlimit):
        pass

    def sweep(self, voltage1, voltage2, step, visaName):
        k = Keithley2600(visaName)

        sweeplist = [voltage1]
        amount = (voltage2 - voltage1)/step + 1

        for x in range(amount):
            sweeplist.append(voltage1 + step)
            print(str(sweeplist[x]))
        k.voltage_sweep_single_smu(k.smua, sweeplist)

    #def elecopticsweep(self, voltage1, voltage2, step, visaName):




    # Closed Loop ----------------------------
    def setcloop(self, toggle):
        # 0 = off
        # 1 = on
        try:
            self.ser.write('%d 1 setcloop' % (toggle))
            self.ser.write('%d 2 setcloop' % (toggle))
            self.ser.write('%d 3 setcloop' % (toggle))
            if toggle == 0:
                print('Close Loop Disabled for All Axis.')
            if toggle == 1:
                print('Close Loop Enabled for All Axis.')
        except:
            self.showErr()

    # set scale type
    def setscaletype(self, stype):
        # value of 0 or 1
        # 0 = Analog
        # 1 = digital
        try:
            self.ser.write('%d 1 setscaletype' % (stype))
            self.ser.write('%d 2 setscaletype' % (stype))
            self.ser.write('%d 3 setscaletype' % (stype))
            if stype == 0:
                print('Scale Type set to Analog for All Axis')
            if stype == 1:
                print('Scale Type set to Digital for All Axis')
        except:
            self.showErr()

    def setclperiod(self, direction, distance):
        # + or - for direction
        # distance in microns, value from 0.0000001 to 1.999999

        microndistance = distance / 1000

        try:
            self.ser.write('%s %d 1 setclperiod' % (direction, microndistance))
            self.ser.write('%s %d 2 setclperiod' % (direction, microndistance))
            self.ser.write('%s %d 3 setclperiod' % (direction, microndistance))
            print('Clperiod Set Successfully')
        except:
            self.showErr()

    def setnselpos(self, pos):
        # pos: 0 or 1
        # 0 returns the calculated position
        # 1 returns the measured position

        try:
            self.ser.write('%d 1 setnselpos' % (pos))
            self.ser.write('%d 2 setnselpos' % (pos))
            self.ser.write('%d 3 setnselpos' % (pos))
            print('Complete')
            # NOTE: Try doing this with axis disabled and see if the function still works
            # should still work even if axis disabled.
        except:
            self.showErr()

    # sets the unit for all axis
    # 0 = microstep
    # 1 = micron
    # 2 = millimeters
    # 3 = centimeters
    # 4 = meters
    # 5 = inches
    # 6 = mil (1/1000 inch)
    def setunit(self, unit):
        self.ser.write('%d 0 setunit' % (unit))
        self.ser.write('%d 1 setunit' % (unit))
        self.ser.write('%d 2 setunit' % (unit))
        self.ser.write('%d 3 setunit' % (unit))
        print('Units set successfully.')

    # Checks the currently set units
    # 0 = microstep
    # 1 = micron
    # 2 = millimeters
    # 3 = centimeters
    # 4 = meters
    # 5 = inches
    # 6 = mil (1/1000 inch)
    def getunit(self, axis):
        self.ser.write('%d getunit' % (axis))
        value = self.ser.read()
        print(('Axis %d is set to unitvalue: %s' % (axis, value)))

    # =======Movement functions============
    def moveX(self, distance):
        if self.NumberOfAxis == 1:
            try:
                self.ser.write(str(distance) + ' r')
                # print ('Move Complete')
            except:
                print('An Error has occured')
                self.showErr()

        if self.NumberOfAxis == 2:
            try:
                self.ser.write(str(distance) + ' 0 r')
                # print ('Move Complete')
            except:
                print('An Error has occured')
                self.showErr()

        if self.NumberOfAxis == 3:
            try:
                self.ser.write(str(distance) + ' 0 0 r')
                # print ('Move Complete')
            except:
                print('An Error has occured')
                self.showErr()

    def moveY(self, distance):
        if self.NumberOfAxis == 1:
            print('Error: Axis 2 Not Enabled.')

        if self.NumberOfAxis == 2:
            try:
                self.ser.write('0 ' + str(distance) + ' r')
                # print ('Move Complete')
            except:
                print('An Error has occured')
                self.showErr()

        if self.NumberOfAxis == 3:
            try:
                self.ser.write('0 ' + str(distance) + ' 0 r')
                # print ('Move Complete')
            except:
                print('An Error has occured')
                self.showErr()

    def moveZ(self, distance):
        if self.NumberOfAxis == 1:
            print('Error: Axis 3 Not Enabled.')

        if self.NumberOfAxis == 2:
            print('Error: Axis 3 Not Enabled.')

        if self.NumberOfAxis == 3:
            try:
                self.ser.write('0 0 ' + str(distance) + ' r')
                # print ('Move Complete')
            except:
                print('An Error has occured')
                self.showErr()

    # Moves all the axis together
    # can be used regardless of how many axis are enabled
    def moveRelative(self, x, y=0, z=0):
        if self.NumberOfAxis == 1:
            try:
                self.ser.write('%.6f r' % (x))
                # print ('Move Complete')
            except:
                print('An Error has occured')
                self.showErr()

        if self.NumberOfAxis == 2:
            try:
                self.ser.write('%.6f %.6f r' % (x, y))
                # print ('Move Complete')
            except:
                print('An Error has occured')
                self.showErr()

        if self.NumberOfAxis == 3:
            try:
                self.ser.write('%.6f %.6f %.6f r' % (x, y, z))
                # print ('Move Complete')
            except:
                print('An Error has occured')
                self.showErr()
        self.waitMoveComplete()

    def moveAbsoluteXY(self, x, y):
        xCurrentPos = self.getPosition()[0];
        yCurrentPos = self.getPosition()[1];
        self.moveRelative(x - xCurrentPos, y - yCurrentPos)

    def waitMoveComplete(self):
        while int(self.ser.ask('st')) & 1:
            time.sleep(0.001)

    # Absolute MOve
    # Has a possible range of +/- 16383mm
    # units are the ones defined to the axis (should be microns)

    # From manual: The move profile is calculated in respect to the velocity/acceleration
    # setup and the given hard or software limits. The axes are linear interpolated,
    # this causes the controller to start and stop all active axes simultaneously
    #    def moveAbsolute(self,x,y=0,z=0):
    #        if self.NumberOfAxis == 1:
    #            try:
    #                self.ser.write('%d m'%(x))
    #                print ('Move Complete')
    #            except:
    #                print('An Error has occured')
    #                self.showErr()
    #
    #        if self.NumberOfAxis == 2:
    #            try:
    #                self.ser.write('%d %d m'%(x,y))
    #                print ('Move Complete')
    #            except:
    #                print('An Error has occured')
    #                self.showErr()
    #
    #        if self.NumberOfAxis == 3:
    #            try:
    #                self.ser.write('%d %d %d m'%(x,y,z))
    #                print ('Move Complete')
    #            except:
    #                print('An Error has occured')
    #                self.showErr()

    def getPosition(self):
        try:
            self.ser.write('pos')
            motorPosStr = self.ser.read()
            res = list(map(float, motorPosStr.strip().split()))
        except Exception as e:
            print(e)
            print(motorPosStr)
            print('An Error has occured')
            self.showErr()
        return res

    def clear(self):  # Should clear any lingering messages in the device
        try:
            self.ser.write('clear')  # Clears the parameter stack, refer to page 287 in manual for more detail
        except:
            self.showErr()

    def reset(self):  # Resets the whole device, equivalent of disconnecting the power according to the manual
        # a beep should be heard after the device is reset
        try:
            self.ser.write('reset')
        except:
            self.showErr()

    def showErr(self):
        self.ser.write(
            'ge')  # Returns error and clears the error stack, Errors are given as codes which are listen in them manual
        error = str('Error Code: ' + self.ser.read() + ' (Refer to Manual Page 165)')
        raise Exception(error)
