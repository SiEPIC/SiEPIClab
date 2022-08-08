import math
from ctypes import *
from itertools import repeat
import numpy as np


class measurementRoutines:

    def __init__(self, flag, deviceInfo, smu, laser):
        """A class containing different types of measurement routines including iv sweeps, optical spectrum sweeps
        iv sweeps at fixed wavelengths and optical sweeps with bias voltages."""

        self.deviceDict = deviceInfo
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
        # min,max,res,independentVar
        self.SMU.ivsweep(self.deviceDict[0], self.deviceDict[0], self.deviceDict[0], self.deviceDict[0])

    def opticalSweep(self):

        # Convert values from string representation to integers for the driver
        unitNum = self.laser.sweepUnitDict[self.laser.sweepUnit]
        outputNum = self.laser.laserOutputDict[self.laser.sweepLaserOutput]
        numScans = self.laser.sweepNumScansDict[self.laser.sweepNumScans]
        numChan = len(self.laser.pwmSlotIndex)
        numActiveChan = len(self.laser.activeSlotIndex)  # Number of active channels

        # TODO: Fill these in from csv
        numTotalPoints = int(round((self.sweepStopWvl - self.sweepStartWvl) / self.sweepStepWvl + 1))

        # The laser reserves 100 pm of spectrum which takes away from the maximum number of data points per scan
        # Also, we will reserve another 100 data points as an extra buffer.
        # maxPWMPointsTrunc = int(round(self.maxPWMPoints-100e-12/self.sweepStepWvl-1));
        maxPWMPointsTrunc = int(round(self.laser.maxPWMPoints - math.ceil(100e-12 / self.laser.sweepStepWvl))) - 100
        numFullScans = int(numTotalPoints // maxPWMPointsTrunc)
        numRemainingPts = numTotalPoints % maxPWMPointsTrunc

        stitchNumber = numFullScans + 1

        print('Total number of data points: %d' % numTotalPoints)
        print('Stitch number: %d' % stitchNumber)

        # Create a list of the number of points per stitch
        numPointsLst = list()

        for x in repeat(maxPWMPointsTrunc, numFullScans):
            numPointsLst.append(int(x))

        numPointsLst.append(int(round(numRemainingPts)))

        startWvlLst = list()
        stopWvlLst = list()

        # Create a list of the start and stop wavelengths per stitch
        pointsAccum = 0
        for points in numPointsLst:
            # TODO: change these to use values from csv
            startWvlLst.append(self.sweepStartWvl + pointsAccum * self.sweepStepWvl)
            stopWvlLst.append(self.sweepStartWvl + (pointsAccum + points - 1) * self.sweepStepWvl)
            pointsAccum += points

        # Set sweep speed
        # TODO: Use value from csv
        self.laser.setSweepSpeed(self.sweepSpeed)

        wavelengthArrPWM = np.zeros(int(numTotalPoints))
        powerArrPWM = np.zeros((int(numTotalPoints), numActiveChan))

        pointsAccum = 0
        # Loop over all the stitches
        for points, startWvl, stopWvl in zip(numPointsLst, startWvlLst, stopWvlLst):
            print('Sweeping from %g nm to %g nm' % (startWvl * 1e9, stopWvl * 1e9))
            # If the start or end wavelength is not a multiple of 1 pm, the laser will sometimes choose the wrong start
            # or end wavelength for doing the sweep. To fix this, we will set the sweep start wavelength to the
            # nearest multiple of 1 pm below the start wavelength and the nearest multiple above the end wavelength.
            # After the sweep is completed, the desired wavelength range is extracted from the results.
            startWvlAdjusted = startWvl
            stopWvlAdjusted = stopWvl
            if startWvl * 1e12 - int(startWvl * 1e12) > 0:
                startWvlAdjusted = math.floor(startWvl * 1e12) / 1e12
            if stopWvl * 1e12 - int(stopWvl * 1e12) > 0:
                stopWvlAdjusted = math.ceil(stopWvl * 1e12) / 1e12

            # Format the start and dtop wvl to 13 digits of accuracy (otherwise the driver will sweep the wrong range)
            startWvlAdjusted = float('%.13f' % startWvlAdjusted)
            stopWvlAdjusted = float('%.13f' % stopWvlAdjusted)

            c_numPts = c_uint32()
            c_numChanRet = c_uint32()
            # TODO: Update values from csv
            res = self.laser.hp816x_prepareMfLambdaScan(self.laser.hDriver, unitNum, self.sweepPower, outputNum,
                                                        numScans, numChan, startWvlAdjusted, stopWvlAdjusted,
                                                        self.sweepStepWvl, byref(c_numPts), byref(c_numChanRet))

            self.laser.checkError(res)
            numPts = int(c_numPts.value)

            # Set range params
            for ii in self.laser.activeSlotIndex:
                # TODO: update values from csv
                self.laser.setRangeParams(ii, self.sweepInitialRange, self.sweepRangeDecrement)

            # This value is unused since getLambdaScanResult returns the wavelength anyways
            c_wavelengthArr = (c_double * int(numPts))()
            c_wavelengthArrPtr = cast(c_wavelengthArr, POINTER(c_double))

            # Perform the sweep
            res = self.laser.hp816x_executeMfLambdaScan(self.laser.hDriver, c_wavelengthArrPtr)
            self.laser.checkError(res)

            wavelengthArrTemp = np.zeros(int(numPts))
            for zeroIdx, chanIdx in enumerate(self.laser.activeSlotIndex):
                # zeroIdx is the index starting from zero which is used to add the values to the power array
                # chanIdx is the channel index used by the mainframe
                # Get power values and wavelength values from the laser/detector
                wavelengthArrTemp, powerArrTemp = self.laser.getLambdaScanResult(chanIdx, self.laser.sweepUseClipping,
                                                                                 self.laser.sweepClipLimit, numPts)
                # The driver sometimes doesn't return the correct starting wavelength for a sweep
                # We will search the returned wavelength results to see the index at which
                # the desired wavelength starts at, and take values starting from there
                wavelengthStartIdx = self.laser.findClosestValIdx(wavelengthArrTemp, startWvl)
                wavelengthStopIdx = self.laser.findClosestValIdx(wavelengthArrTemp, stopWvl)
                wavelengthArrTemp = wavelengthArrTemp[wavelengthStartIdx:wavelengthStopIdx + 1]
                powerArrTemp = powerArrTemp[wavelengthStartIdx:wavelengthStopIdx + 1]
                powerArrPWM[pointsAccum:pointsAccum + points, zeroIdx] = powerArrTemp
            wavelengthArrPWM[pointsAccum:pointsAccum + points] = wavelengthArrTemp
            pointsAccum += points

        return wavelengthArrPWM, powerArrPWM

    def fixedWavelengthIVSweep(self):
        #TODO: Ensure first parameter is wavelength
        self.laser.setTLSWavelength(self.deviceDict[40], slot=self.laser.panel.getSelectedLaserSlot())
        self.ivSweep()

    def opticalSweepWithBiasVoltages(self):
        #TODO: First param is voltage, second is channel
        self.SMU.setVoltage(self.deviceDict[0], self.deviceDict[0])
        self.opticalSweep()
