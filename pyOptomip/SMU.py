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

    def __init__(self):
        self.Aflag = False
        self.Bflag = False

    def connect(self, visaName, rm):
        self.k = Keithley2600(visaName)
        #self.k.smua.source.output = self.k.smua.OUTPUT_ON  #turns on SMUA
        #self.setCurrent(0)

        self.inst = rm.open_resource(visaName)
        print(self.inst.query("*IDN?\n"))
        #self.inst.write("beeper.beep(0.1,2400)")
        #self.inst.write("delay(0.250)")
        #self.inst.write("beeper.beep(0.1,2400)")
        #self.inst.write("read_error_queue()")

        self.inst.write("smua.reset()") #Reset channel A
        self.inst.write("dataqueue.clear()")
        self.inst.write("errorqueue.clear()")

        #v = self.inst.query("errorqueue.clear()")
        #errorCode, message, severity, errorNode = v
        #print(v)
        print('Connected\n')


    def disconnect(self):
        #self.k.smua.source.output = self.k.smua.OUTPUT_OFF
        #self.k.disconnect()

        self.inst.write("smua.source.output = smua.OUTPUT_OFF") #Turn off output
        #self.inst.write("disconnect()") #disconnect from smu
        print('SMU Disconnected')


    def setVoltage(self, voltage, channel):#, outputA, outputB):
        """ Sets the source of the SMU to a specified voltage
            Arguments:
                voltage: a float representing the voltage to set the SMU to
            Returns:
                A print statement indicating that the voltage has been set
            """
        if channel == 'A':
            self.inst.write("smua.source.func = smua.OUTPUT_DCVOLTS")
            setvoltstring = "smua.source.levelv = " + str(voltage)
            self.inst.write(setvoltstring)
            print('Set channel A voltage to ' + str(int(voltage)) + 'V')

        if channel == 'B':
            self.inst.write("smub.source.func = smub.OUTPUT_DCVOLTS")
            setvoltstring = "smub.source.levelv = " + str(voltage)
            self.inst.write(setvoltstring)
            print('Set channel B voltage to ' + str(int(voltage)) + 'V')

        if channel == 'All':
            self.inst.write("smua.source.func = smua.OUTPUT_DCVOLTS")
            setvoltstring = "smua.source.levelv = " + str(voltage)
            self.inst.write(setvoltstring)
            print('Set channel A voltage to ' + str(int(voltage)) + 'V')

            self.inst.write("smub.source.func = smub.OUTPUT_DCVOLTS")
            setvoltstring = "smub.source.levelv = " + str(voltage)
            self.inst.write(setvoltstring)
            print('Set channel B voltage to ' + str(int(voltage)) + 'V')



        #if outputA is False and outputB is False:
         #   print("Please select an output channel")

        #if outputA is True:
         #   self.inst.write("smua.source.func = smua.OUTPUT_DCVOLTS")
          #  setvoltstring = "smua.source.levelv = " + str(voltage)
           # self.inst.write(setvoltstring)
            #print('Set channel A voltage to ' + str(int(voltage)) + 'V')

        #if outputB is True:
         #   self.inst.write("smub.source.func = smub.OUTPUT_DCVOLTS")
          #  setvoltstring = "smub.source.levelv = " + str(voltage)
           # self.inst.write(setvoltstring)
            #print('Set channel B voltage to ' + str(int(voltage)) + 'V')


    def setCurrent(self, current, channel):#outputA, outputB):
        """ Sets the source of the SMU to a specified current
                    Arguments:
                        current: a float representing the current to set the SMU to
                        channel: specifies which channel to set current in
                    Returns:
                        A print statement indicating that the current has been set
                    """
        if channel == 'A':
            self.inst.write("smua.source.func = smua.OUTPUT_DCAMPS")
            setcurrentstring = "smua.source.leveli = " + str(current)
            self.inst.write(setcurrentstring)
            print('Set channel A current to ' + str(int(current * 1e6) / 1000) + 'mA')

        if channel == 'B':
            self.inst.write("smub.source.func = smub.OUTPUT_DCAMPS")
            setcurrentstring = "smub.source.leveli = " + str(current)
            self.inst.write(setcurrentstring)
            print('Set channel B current to ' + str(int(current * 1e6) / 1000) + 'mA')

        if channel == 'All':
            self.inst.write("smua.source.func = smua.OUTPUT_DCAMPS")
            setcurrentstring = "smua.source.leveli = " + str(current)
            self.inst.write(setcurrentstring)
            print('Set channel A current to ' + str(int(current * 1e6) / 1000) + 'mA')

            self.inst.write("smub.source.func = smub.OUTPUT_DCAMPS")
            setcurrentstring = "smub.source.leveli = " + str(current)
            self.inst.write(setcurrentstring)
            print('Set channel B current to ' + str(int(current * 1e6) / 1000) + 'mA')


    def setcurrentlimit(self, currentlimit, channel):#outputA, outputB):

        if channel == 'A':
            currentlimitstring = "smua.source.limiti = " + str(float(currentlimit / 1000))
            self.inst.write(currentlimitstring)
            print("Set channel A current limit to " + str(currentlimit) + "mA")

        if channel == 'B':
            currentlimitstring = "smub.source.limiti = " + str(float(currentlimit / 1000))
            self.inst.write(currentlimitstring)
            print("Set channel B current limit to " + str(currentlimit) + "mA")

        if channel == 'All':
            currentlimitstring = "smua.source.limiti = " + str(float(currentlimit / 1000))
            self.inst.write(currentlimitstring)
            print("Set channel A current limit to " + str(currentlimit) + "mA")

            currentlimitstring = "smub.source.limiti = " + str(float(currentlimit / 1000))
            self.inst.write(currentlimitstring)
            print("Set channel B current limit to " + str(currentlimit) + "mA")


    def setvoltagelimit(self, voltagelimit, channel):# outputA, outputB):

        if channel == 'A':
            voltagelimitstring = "smua.source.limitv = " + str(voltagelimit)
            self.inst.write(voltagelimitstring)
            print("Set channel A voltage limit to " + str(voltagelimit) + " V")

        if channel == 'B':
            voltagelimitstring = "smub.source.limitv = " + str(voltagelimit)
            self.inst.write(voltagelimitstring)
            print("Set channel B voltage limit to " + str(voltagelimit) + " V")

        if channel == 'All':
            voltagelimitstring = "smua.source.limitv = " + str(voltagelimit)
            self.inst.write(voltagelimitstring)
            print("Set channel A voltage limit to " + str(voltagelimit) + " V")

            voltagelimitstring = "smub.source.limitv = " + str(voltagelimit)
            self.inst.write(voltagelimitstring)
            print("Set channel B voltage limit to " + str(voltagelimit) + " V")


    def setpowerlimit(self, powerlimit, channel):# outputA, outputB):


        if channel == 'A':
            powerlimitstring = "smua.source.limitp = " + str(float(powerlimit / 1000))
            self.inst.write(powerlimitstring)
            print("Set channel A power limit to " + str(powerlimit) + " mW")

        if channel == 'B':
            powerlimitstring = "smub.source.limitp = " + str(float(powerlimit / 1000))
            self.inst.write(powerlimitstring)
            print("Set channel B power limit to " + str(powerlimit) + " mW")

        if channel == 'All':
            powerlimitstring = "smua.source.limitp = " + str(float(powerlimit / 1000))
            self.inst.write(powerlimitstring)
            print("Set channel A power limit to " + str(powerlimit) + " mW")

            powerlimitstring = "smub.source.limitp = " + str(float(powerlimit / 1000))
            self.inst.write(powerlimitstring)
            print("Set channel B power limit to " + str(powerlimit) + " mW")


    def getvoltageA(self):
        v = self.inst.query("print(smua.measure.v())")
        return v


    def getcurrentA(self):
        i = self.inst.query("print(smua.measure.i())")
        return i


    def getvoltageB(self):
        v = self.inst.query("print(smub.measure.v())")
        return v


    def getcurrentB(self):
        i = self.inst.query("print(smub.measure.r())")
        return i


    def getresistanceA(self):
        r = self.inst.query("print(smua.measure.r())")
        return r


    def getresistanceB(self):
        r = self.inst.query("print(smub.measure.r())")
        return r


    def ivsweep(self, min:float, max:float, resolution:float, independantvar):

        self.voltageresultA = []
        self.currentresultA = []
        self.voltageresultB = []
        self.currentresultB = []
        self.resistanceresultA = []
        self.resistanceresultB = []
        self.powerresultA = []
        self.powerresultB = []

        print(self.Aflag)
        print(self.Bflag)

        if independantvar == 'Voltage':

            sweeplist = [min]
            x = min

            while x < max:
                sweeplist.append(x + resolution / 1000)
                x = x + resolution / 1000


            if self.Aflag == True:
                self.inst.write("smua.source.func = smua.OUTPUT_DCVOLTS")

                for v in sweeplist:
                    setvoltstring = "smua.source.levelv = " + str(v)
                    self.inst.write(setvoltstring)
                    # self.k.apply_voltage(self.k.smua, v)
                    # i = self.k.smua.measure.i()
                    i = self.inst.query("print(smua.measure.i())")
                    i = float(i) * 1000
                    r = self.inst.query("print(smua.measure.r())")
                    r = float(r)
                    p = self.inst.query("print(smua.measure.p())")
                    p = float(p) * 1000
                    print(p)
                    self.voltageresultA.append(v)
                    self.currentresultA.append(i)
                    self.resistanceresultA.append(r)
                    self.powerresultA.append(p)
                    # rt.append_row([v, i])
                    time.sleep(1)

            if self.Aflag == True:
                setvoltstring = "smua.source.levelv = " + str(0)
                self.inst.write(setvoltstring)

            if self.Bflag == True:
                self.inst.write("smub.source.func = smub.OUTPUT_DCVOLTS")

                for v in sweeplist:
                    setvoltstring = "smub.source.levelv = " + str(v)
                    self.inst.write(setvoltstring)
                    # self.k.apply_voltage(self.k.smua, v)
                    # i = self.k.smua.measure.i()
                    i = self.inst.query("print(smub.measure.i())")
                    i = float(i) * 1000
                    r = self.inst.query("print(smub.measure.r())")
                    r = float(r)
                    p = self.inst.query("print(smub.measure.p())")
                    p = float(p) * 1000
                    self.voltageresultB.append(v)
                    self.currentresultB.append(i)
                    self.resistanceresultB.append(r)
                    self.powerresultB.append(p)
                    time.sleep(1)

            if self.Bflag == True:
                setvoltstring = "smub.source.levelv = " + str(0)
                self.inst.write(setvoltstring)

        if independantvar == 'Current':

            sweeplist = [min / 1000]
            x = min / 1000

            while x < max / 1000:
                sweeplist.append(x + resolution / 1000)
                x = x + resolution / 1000


            if self.Aflag == True:
                self.inst.write("smua.source.func = smua.OUTPUT_DCAMPS")

                for i in sweeplist:
                    setcurrentstring = "smua.source.leveli = " + str(i)
                    self.inst.write(setcurrentstring)

                    v = self.inst.query("print(smua.measure.v())")
                    v = float(v)
                    r = self.inst.query("print(smua.measure.r())")
                    r = float(r)
                    p = self.inst.query("print(smua.measure.p())")
                    p = float(p) * 1000
                    print(p)
                    self.voltageresultA.append(v)
                    self.currentresultA.append(i*1000)
                    self.resistanceresultA.append(r)
                    self.powerresultA.append(p)
                    # rt.append_row([v, i])
                    time.sleep(1)

            if self.Aflag == True:
                setcurrentstring = "smua.source.leveli = " + str(0)
                self.inst.write(setcurrentstring)

            if self.Bflag == True:
                self.inst.write("smub.source.func = smub.OUTPUT_DCAMPS")

                for i in sweeplist:
                    setcurrentstring = "smub.source.leveli = " + str(i)
                    self.inst.write(setcurrentstring)

                    v = self.inst.query("print(smub.measure.v())")
                    v = float(v)
                    r = self.inst.query("print(smub.measure.r())")
                    r = float(r)
                    p = self.inst.query("print(smub.measure.p())")
                    p = float(p) * 1000
                    print(p)
                    self.voltageresultA.append(v)
                    self.currentresultA.append(i)
                    self.resistanceresultA.append(r)
                    self.powerresultA.append(p)
                    # rt.append_row([v, i])
                    time.sleep(1)

            if self.Bflag == True:
                setcurrentstring = "smub.source.leveli = " + str(0)
                self.inst.write(setcurrentstring)

        if self.Aflag == True:
            print(self.voltageresultA)
            print(self.currentresultA)

        if self.Bflag == True:
            print(self.voltageresultB)
            print(self.currentresultB)

        print('Sweep Completed!')


    def turnchannelon(self, channel):#A, B):

        if channel == 'A':
            self.inst.write("smua.source.output = smua.OUTPUT_ON")
            self.onflagA = 'ON'
            print("Channel A ON")

        if channel == 'B':
            self.inst.write("smub.source.output = smub.OUTPUT_ON")
            self.onflagB = 'ON'
            print("Channel B ON")

        if channel == 'All':
            self.inst.write("smua.source.output = smua.OUTPUT_ON")
            self.onflagA = 'ON'
            print("Channel A ON")
            self.inst.write("smub.source.output = smub.OUTPUT_ON")
            self.onflagB = 'ON'
            print("Channel B ON")


    def turnchanneloff(self, channel): #A, B):

        if channel == 'A':
            self.inst.write("smua.source.output = smua.OUTPUT_OFF")
            print("Channel A OFF")

        if channel == 'B':
            self.inst.write("smub.source.output = smub.OUTPUT_OFF")
            print("Channel B OFF")

        if channel == 'All':
            self.inst.write("smua.source.output = smua.OUTPUT_OFF")
            print("Channel A OFF")
            self.inst.write("smub.source.output = smub.OUTPUT_OFF")
            print("Channel B OFF")


    def setoutputflagon(self, channel):#A, B):

        if channel == 'A':
            self.Aflag = True
            print("Channel A set for use with sweep")
        if channel == 'B':
            self.Bflag = True
            print("Channel B set for use with sweep")
        if channel == 'All':
            self.Aflag =True
            self.Bflag = True
            print("Channel A set for use with sweep")
            print("Channel B set for use with sweep")


    def setoutputflagoff(self, channel):  # A, B):

        if channel == 'A':
            self.Aflag = False
            print("Channel A disabled for use with sweep")
        if channel == 'B':
            self.Bflag = False
            print("Channel B disabled for use with sweep")
        if channel == 'All':
            self.Aflag = False
            self.Bflag = False
            print("Channel A disabled for use with sweep")
            print("Channel B disabled for use with sweep")




