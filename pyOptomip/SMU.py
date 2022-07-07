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
import numpy as np
from keithley2600 import Keithley2600

from keithley2600 import Keithley2600Base
from keithley2600 import ResultTable


class SMUClass():


    name = 'SMU'
    isSMU = True
    isMotor = False
    isLaser = False
    isQontrol = False

    def connect(self, visaName, rm):
        self.k = Keithley2600(visaName)
        self.k.smua.source.output = self.k.smua.OUTPUT_ON  #turns on SMUA
        self.setCurrent(0)

        print('Connected\n')




    def disconnect(self):
        self.k.smua.source.output = self.k.smua.OUTPUT_OFF
        self.k.disconnect()
        print('SMU Disconnected')


    def setVoltage(self, voltage):
        """ Sets the source of the SMU to a specified voltage
            Arguments:
                voltage: a float representing the voltage to set the SMU to
            Returns:
                A print statement indicating that the voltage has been set
            """
        self.k.apply_voltage(self.k.smua, voltage)
        print('Set voltage to ' + str(int(voltage*1e9)/1e9) + 'V')

    def setCurrent(self, current):
        """ Sets the source of the SMU to a specified current
                    Arguments:
                        current: a float representing the current to set the SMU to
                    Returns:
                        A print statement indicating that the current has been set
                    """
        self.k.apply_current(self.k.smua, current)
        print('Set current to ' + str(int(current*1e6)/1000) + 'mA')

    def setcurrentlimit(self, currentlimit):
        pass

    def setvoltagelimit(self, voltagelimit):
        pass

    def getvoltage(self):
        v = self.k.smua.measure.v()
        return v

    def getcurrent(self):
        i = self.k.smua.measure.i()
        return i

    def ivsweep(self, voltagemin: float, voltagemax: float, resolution: float):

        sweeplist = [voltagemin]
        stepsize = (voltagemax - voltagemin)
        stepsize = stepsize/(resolution - 1)
        voltagex = voltagemin

        for x in range(int(resolution - 1)):
            sweeplist.append(voltagex + stepsize)
            voltagex = voltagex + stepsize

        print(sweeplist)

        pars = {'recorded': time.asctime(), 'sweep_type': 'iv'}
        # create ResultTable with two columns
        rt = ResultTable(['Voltage', 'Current'], ['V', 'A'], params=pars)
        fig = rt.plot(live=True)

        for v in sweeplist:
            self.k.apply_voltage(self.k.smua, v)
            i = self.k.smua.measure.i()
            rt.append_row([v, i])
            time.sleep(1)

        return rt

        #result = self.k.voltage_sweep_single_smu(self.k.smua, sweeplist, 0.001, -1, True)

        #return result



    #def elecopticsweep(self, voltage1, voltage2, step, visaName):



