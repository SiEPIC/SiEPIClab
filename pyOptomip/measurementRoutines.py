import math
from ctypes import *
from itertools import repeat
import numpy as np
import wx

class measurementRoutines:

    def __init__(self, flag, smu, laser, activeDetectors):
        """A class containing different types of measurement routines including iv sweeps, optical spectrum sweeps
        iv sweeps at fixed wavelengths and optical sweeps with bias voltages."""

        self.SMU = smu
        self.laser = laser
        self.activeDetectors = activeDetectors
        self.laserOutputMap = dict([('High power', 'highpower'), ('Low SSE', 'lowsse')])
        self.laserNumSweepMap = dict([('1', 1), ('2', 2), ('3', 3)])
        self.wav = []
        self.pow = []

        if flag == 'ELEC':  # If the test is purely electrical
            self.ivSweep()
        if flag == 'OPT':  # If the test is purely optical
            self.wav, self.pow = self.opticalSweep()
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

    def copySweepSettings(self):
        """ Copies the current sweep settings in the dictionary to the laser object."""
        self.laser.sweepStartWvl = float(self.deviceDict['Start'][self.i]) / 1e9
        self.laser.sweepStopWvl = float(self.deviceDict['Stop'][self.i]) / 1e9
        self.laser.sweepStepWvl = float(self.deviceDict['Stepsize'][self.i]) / 1e9
        self.laser.sweepSpeed = self.deviceDict['Sweepspeed'][self.i]
        self.laser.sweepUnit = 'dBm'
        self.laser.sweepPower = float(self.deviceDict['Sweeppower'][self.i])
        self.laser.sweepLaserOutput = self.laserOutputMap[self.deviceDict['Laseroutput'][self.i]]
        self.laser.sweepNumScans = self.laserNumSweepMap[self.deviceDict['Numscans'][self.i]]
        self.laser.sweepInitialRange = self.deviceDict['InitialRange'][self.i]
        self.laser.sweepRangeDecrement = self.deviceDict['RangeDec'][self.i]
        activeDetectors = self.activeDetectors
        if len(activeDetectors) == 0:
            raise Exception('Cannot perform sweep. No active detectors selected.')
        self.laser.activeSlotIndex = activeDetectors

    def opticalSweep(self):
        try:
            self.copySweepSettings()
            self.lastSweepWavelength, self.lastSweepPower = self.laser.sweep()

            return self.lastSweepWavelength, self.lastSweepPower
        except Exception as e:
            print(e)
        self.laser.setAutorangeAll()

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
