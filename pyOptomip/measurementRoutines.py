import math
from ctypes import *
from itertools import repeat
import numpy as np
import wx

#TODO: Plot figures
class measurementRoutines:

    def __init__(self, flag, deviceInfo, i, smu, laser):
        """A class containing different types of measurement routines including iv sweeps, optical spectrum sweeps
        iv sweeps at fixed wavelengths and optical sweeps with bias voltages."""

        self.deviceDict = deviceInfo
        self.i = i
        self.SMU = smu
        self.laser = laser

        if flag == 'ELEC':  # If the test is purely electrical
            self.ivSweep()
        if flag == 'OPT':  # If the test is purely optical
            self.opticalSweep()
        if flag == 'FIXWAVIV':  # iv sweep at a fixed wavelength
            self.fixedWavelengthIVSweep()
        if flag == 'BIASVOPT':  # optical sweep at a fixed voltage
            self.opticalSweepWithBiasVoltages()

    def ivSweep(self):
        if self.deviceDict['Voltsel'][self.i]:
            self.SMU.ivsweep(self.deviceDict['VoltMin'][self.i], self.deviceDict['VoltMax'][self.i],
                             self.deviceDict['VoltRes'][self.i], 'Voltage')
        if self.deviceDict['Currentsel'][self.i]:
            self.SMU.ivsweep(self.deviceDict['CurrentMin'][self.i], self.deviceDict['CurrentMax'][self.i],
                             self.deviceDict['CurrentRes'][self.i], 'Current')

    def opticalSweep(self):


    def fixedWavelengthIVSweep(self):
        self.laser.setTLSWavelength(self.deviceDict['Wavelengths'][self.i], slot=self.laser.panel.getSelectedLaserSlot())
        if self.deviceDict['setwVoltsel'][self.i]:
            self.SMU.ivsweep(self.deviceDict['SetwVoltMin'][self.i], self.deviceDict['SetwVoltMax'][self.i],
                             self.deviceDict['SetwVoltRes'][self.i], 'Voltage')
        if self.deviceDict['setwCurrentsel'][self.i]:
            self.SMU.ivsweep(self.deviceDict['SetwCurrentMin'][self.i], self.deviceDict['SetwCurrentMax'][self.i],
                             self.deviceDict['SetwCurrentRes'][self.i], 'Current')

    def opticalSweepWithBiasVoltages(self):
        voltages = self.deviceDict['Voltages'][self.i]
        for voltage in voltages:
            if self.deviceDict['setvChannelA'][self.i]:
                self.SMU.setVoltage(voltage, 'A')
            if self.deviceDict['setvChannelB'][self.i]:
                self.SMU.setVoltage(voltage, 'B')
            self.opticalSweep()
