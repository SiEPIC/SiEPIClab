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
import csv

import wx
from numpy import *
import re
import os
import numpy as np
from scipy.io import savemat
import time
import matplotlib.pyplot as plt
from ElectroOpticDevice import ElectroOpticDevice
from measurementRoutines import measurementRoutines


class autoMeasure(object):

    def __init__(self, laser, motorOpt, motorElec, smu, fineAlign, graph):
        """
        Creates an autoMeasure object which is used to coordinate motors and perform automated
        measurements.
        Args:
            laser: laser object
            motorOpt: motor object controlling the chip stage
            motorElec: motor object controlling the wedge probe stage
            smu: smu object controls SMU
            fineAlign: fineAlign object
        """
        global beginMeasure
        self.laser = laser
        self.motorOpt = motorOpt
        self.motorElec = motorElec
        self.smu = smu
        self.fineAlign = fineAlign
        self.saveFolder = os.getcwd()
        self.graphPanel = graph
        self.devices = []
        self.saveoptposition1 = []
        self.saveoptposition2 = []
        self.saveoptposition3 = []
        self.xscalevar = 0
        self.yscalevar = 0

        self.wavelengthSweeps = {'RoutineName': [], 'Start': [], 'Stop': [], 'Stepsize': [], 'Sweeppower': [], 'Sweepspeed': [],
                                 'Laseroutput': [], 'Numscans': [], 'InitialRange': [], 'RangeDec': []}
        self.voltageSweeps = {'RoutineName': [], 'VoltMin': [], 'VoltMax': [], 'VoltRes': [], 'IV': [], 'RV': [], 'PV': [],
                              'ChannelA': [], 'ChannelB': []}
        self.currentSweeps = {'RoutineName': [], 'CurrentMin': [], 'CurrentMax': [], 'CurrentRes': [], 'IV': [], 'RV': [],
                              'PV': [], 'ChannelA': [], 'ChannelB': []}
        self.setWavelengthVoltageSweeps = {'RoutineName': [], 'VoltMin': [], 'VoltMax': [], 'VoltRes': [], 'IV': [], 'RV': [],
                                           'PV': [], 'ChannelA': [], 'ChannelB': [], 'Wavelength': []}
        self.setWavelengthCurrentSweeps = {'RoutineName': [], 'CurrentMin': [], 'CurrentMax': [], 'CurrentRes': [], 'IV': [],
                                           'RV': [], 'PV': [], 'ChannelA': [], 'ChannelB': [],
                                           'Wavelength': []}
        self.setVoltageWavelengthSweeps = {'RoutineName': [], 'Start': [], 'Stop': [], 'Stepsize': [], 'Sweeppower': [],
                                           'Sweepspeed': [], 'Laseroutput': [], 'Numscans': [],
                                           'InitialRange': [], 'RangeDec': [], 'ChannelA': [], 'ChannelB': [],
                                           'Voltage': []}


    def readCoordFile(self, fileName):
        """
        Reads a coordinate file generated using the automated coordinate extraction in k-layout.
        Stores all data as a list of ElectroOpticDevice objects, self.devices.
        Args:
            fileName: Path to desired text file, a string
        """
        self.devices = []
        with open(fileName, 'r') as f:
            data = f.readlines()

        # Remove the first line since it is the header and remove newline char  
        dataStrip = [line.strip() for line in data[1:]]
        dataStrip2 = []
        for x in dataStrip:
            j = x.replace(" ", "")
            dataStrip2.append(j)
        # x,y,polarization,wavelength,type,deviceid,params
        reg = re.compile(r'(.-?[0-9]*),(.-?[0-9]*),(T(E|M)),([0-9]+),(.+?),(.+)')
        # x, y, deviceid, padname, params
        regElec = re.compile(r'(.-?[0-9]*),(.-?[0-9]*),(.+),(.+),(.*)')

        self.devSet = []

        #for ii, line in enumerate(dataStrip2):
            #if reg.match(line):
               # matchRes = reg.findall(line)[0]

                #devName = matchRes[6]
               # self.devSet.append(devName)

        # Parse the data in each line and put it into a list of devices
        for ii, line in enumerate(dataStrip2):
            if line == "" or line == "%X-coord,Y-coord,deviceID,padName,params":
                pass
            else:
                if reg.match(line):
                    matchRes = reg.findall(line)[0]
                    devName = matchRes[6]

                    self.devSet.append(devName)
                    device = ElectroOpticDevice(devName, matchRes[4], matchRes[2], [float(matchRes[0]),
                                                float(matchRes[1])], matchRes[5])
                    self.devices.append(device)
                else:
                    if regElec.match(line):
                        matchRes = regElec.findall(line)[0]
                        devName = matchRes[2]
                        for device in self.devices:
                            if device.getDeviceID() == devName:
                                print("adding elec coords to device")
                                device.addElectricalCoordinates((matchRes[3], float(matchRes[0]), float(matchRes[1])))
                    else:
                        print('Warning: The entry\n%s\nis not formatted correctly.' % line)

    def findCoordinateTransform(self, motorCoords, gdsCoords):
        ## OLD METHOD: USED FOR TESTING
        """ Finds the affine transform matrix which maps the GDS coordinates to motor coordinates."""

        if len(motorCoords) != len(gdsCoords):
            raise CoordinateTransformException('You must have the same number of motor coordinates and GDS coordinates')

        if len(motorCoords) < 3:
            raise CoordinateTransformException('You must have at least 3 coordinate pairs.')

        numPairs = len(motorCoords)

        X = mat(zeros((2 * numPairs, 2 * numPairs)))
        Xp = mat(zeros((2 * numPairs, 1)))

        for ii, motorCoord, gdsCoord in zip(range(numPairs), motorCoords, gdsCoords):
            X[2 * ii, 0:3] = mat([gdsCoord[0], gdsCoord[1], 1])
            X[2 * ii + 1, 3:6] = mat([gdsCoord[0], gdsCoord[1], 1])
            Xp[2 * ii:2 * ii + 2] = mat([[motorCoord[0]], [motorCoord[1]]])

        # Do least squares fitting
        a = linalg.lstsq(X, Xp)

        A = vstack((a[0][0:3].T, a[0][3:6].T, mat([0, 0, 1])))

        self.transformMatrix = A

        return A

    def gdsToMotor(self, gdsCoords):
        ## OLD METHOD: USED FOR TESTING
        """ Uses the calculated affine transform to map a GDS coordinate to a motor coordinate."""
        gdsCoordVec = mat([[gdsCoords[0]], [gdsCoords[1]], [1]])
        motorCoordVec = self.transformMatrix * gdsCoordVec
        motorCoords = (float(motorCoordVec[0]), float(motorCoordVec[1]))
        return motorCoords

    def coordinate_transform_matrix(self, motorCoords, gdsCoords):
        ## FOR TESTING PURPOSES
        """ Finds the affine transform matrix which maps the GDS coordinates to motor coordinates."""
        motorMatrix = np.array([[motorCoords[0][0], motorCoords[1][0], motorCoords[2][0]],
                                [motorCoords[0][1], motorCoords[1][1], motorCoords[2][1]],
                                [motorCoords[0][2], motorCoords[1][2], motorCoords[2][2]]])

        gdsMatrix = np.array([[gdsCoords[0][0], gdsCoords[1][0], gdsCoords[2][0]],
                              [gdsCoords[0][1], gdsCoords[1][1], gdsCoords[2][1]],
                              [1, 1, 1]])

        transpose = gdsMatrix.T

        row1 = np.linalg.solve(transpose, motorMatrix[0])
        row2 = np.linalg.solve(transpose, motorMatrix[1])
        row3 = np.linalg.solve(transpose, motorMatrix[2])

        self.T = vstack((row1, row2, row3))

        return self.T

    def perform_transform(self, gdsCoords):
        ## FOR TESTING PURPOSES
        """ Uses the calculated affine transform to map a GDS coordinate to a motor coordinate."""
        gdsVector = np.array([[gdsCoords[0]], [gdsCoords[1]], [1]])

        newMotorCoords = self.T @ gdsVector

        return newMotorCoords

    def findCoordinateTransformOpt(self, motorCoords, gdsCoords):
        """ Finds the best fit affine transform which maps the GDS coordinates to motor coordinates
        for the motors controlling the chip stage.

        Args:
            motorCoords: A list of motor coordinates from the three devices used for alignment
            gdsCoords: A list of gds coordinates from the three devices used for alignment

        Returns:
            M: a matrix used to map gds coordinates to motor coordinates.
        """
        if all(item == 0 for item in motorCoords) and all(item == 0 for item in gdsCoords):

            if motorCoords and gdsCoords:
                motorMatrix = np.array([[motorCoords[0][0], motorCoords[1][0], motorCoords[2][0]],
                                        [motorCoords[0][1], motorCoords[1][1], motorCoords[2][1]],
                                        [motorCoords[0][2], motorCoords[1][2], motorCoords[2][2]]])

                gdsMatrix = np.array([[gdsCoords[0][0], gdsCoords[1][0], gdsCoords[2][0]],
                                      [gdsCoords[0][1], gdsCoords[1][1], gdsCoords[2][1]],
                                      [1, 1, 1]])

                transpose = gdsMatrix.T
                row1 = np.linalg.solve(transpose, motorMatrix[0])
                row2 = np.linalg.solve(transpose, motorMatrix[1])
                row3 = np.linalg.solve(transpose, motorMatrix[2])

                self.TMopt = vstack((row1, row2, row3))

                return self.TMopt

    def findCoordinateTransformElec(self, motorCoords, gdsCoords):
        """ Finds the best fit affine transform which maps the GDS coordinates to motor coordinates
        for the motors controlling the wedge probe stage.

        Args:
            motorCoords: A list of motor coordinates from the three devices used for alignment
            gdsCoords: A list of gds coordinates from the three devices used for alignment

        Returns:
            M: a matrix used to map gds coordinates to motor coordinates.
        """

        if all(item == 0 for item in motorCoords) and all(item == 0 for item in gdsCoords):
            motorMatrix = np.array([[motorCoords[0][0], motorCoords[1][0], motorCoords[2][0]],
                                    [motorCoords[0][1], motorCoords[1][1], motorCoords[2][1]],
                                    [motorCoords[0][2], motorCoords[1][2], motorCoords[2][2]]])

            gdsMatrix = np.array([[gdsCoords[0][0], gdsCoords[1][0], gdsCoords[2][0]],
                                  [gdsCoords[0][1], gdsCoords[1][1], gdsCoords[2][1]],
                                  [1, 1, 1]])

            transpose = gdsMatrix.T

            row1 = np.linalg.solve(transpose, motorMatrix[0])
            row2 = np.linalg.solve(transpose, motorMatrix[1])
            row3 = np.linalg.solve(transpose, motorMatrix[2])

            self.TMelec = vstack((row1, row2, row3))
            return self.TMelec

    def gdsToMotorCoordsOpt(self, gdsCoords):
        """ Uses the calculated affine transform to map a GDS coordinate to a motor coordinate.

        Args:
            gdsCoords: The gds coordinates of a device

        Returns:
            motorCoords: the motor coordinates for the chip stage that correspond to given gds
            coordinates.
        """
        gdsVector = np.array([[gdsCoords[0]], [gdsCoords[1]], [1]])

        newMotorCoords = self.TMopt @ gdsVector

        return newMotorCoords

    def gdsToMotorCoordsElec(self, gdsCoords):
        """ Uses the calculated affine transform to map a GDS coordinate to a motor coordinate.

        Args:
            gdsCoords: The gds coordinates of a device

        Returns:
            object: the motor coordinates for the wedge probe stage that correspond to given gds
            coordinates.
        """
        gdsVector = np.array([[gdsCoords[0]], [gdsCoords[1]], [1]])

        newMotorCoords = self.TMelec @ gdsVector

        return newMotorCoords

    def addWavelengthSweep(self, name, start, stop, stepsize, sweeppower, sweepspeed, laseroutput, numscans,
                           initialrange, rangedec):
        """Associates a wavelength sweep routine with this device"""
        self.wavelengthSweeps['Start'].append(start)
        self.wavelengthSweeps['Stop'].append(stop)
        self.wavelengthSweeps['Stepsize'].append(stepsize)
        self.wavelengthSweeps['Sweeppower'].append(sweeppower)
        self.wavelengthSweeps['Sweepspeed'].append(sweepspeed)
        self.wavelengthSweeps['Laseroutput'].append(laseroutput)
        self.wavelengthSweeps['Numscans'].append(numscans)
        self.wavelengthSweeps['InitialRange'].append(initialrange)
        self.wavelengthSweeps['RangeDec'].append(rangedec)
        self.wavelengthSweeps['RoutineName'].append(name)
        self.hasRoutines = True

    def addVoltageSweep(self, name, voltmin, voltmax, voltres, iv, rv, pv, a, b):
        """Associates a voltage sweep routine with this device"""
        self.voltageSweeps['VoltMin'].append(voltmin)
        self.voltageSweeps['VoltMax'].append(voltmax)
        self.voltageSweeps['VoltRes'].append(voltres)
        self.voltageSweeps['IV'].append(iv)
        self.voltageSweeps['RV'].append(rv)
        self.voltageSweeps['PV'].append(pv)
        self.voltageSweeps['ChannelA'].append(a)
        self.voltageSweeps['ChannelB'].append(b)
        self.voltageSweeps['RoutineName'].append(name)
        self.hasRoutines = True

    def addCurrentSweep(self, name, currentmin, currentmax, currentres, iv, rv, pv, a, b):
        """Associates a current sweep routine with this device"""
        self.currentSweeps['CurrentMin'].append(currentmin)
        self.currentSweeps['CurrentMax'].append(currentmax)
        self.currentSweeps['CurrentRes'].append(currentres)
        self.currentSweeps['IV'].append(iv)
        self.currentSweeps['RV'].append(rv)
        self.currentSweeps['PV'].append(pv)
        self.currentSweeps['ChannelA'].append(a)
        self.currentSweeps['ChannelB'].append(b)
        self.currentSweeps['RoutineName'].append(name)
        self.hasRoutines = True

    def addSetWavelengthVoltageSweep(self, name, voltmin, voltmax, voltres, iv, rv, pv, a, b, wavelengths):
        """"""
        self.setWavelengthVoltageSweeps['VoltMin'].append(voltmin)
        self.setWavelengthVoltageSweeps['VoltMax'].append(voltmax)
        self.setWavelengthVoltageSweeps['VoltRes'].append(voltres)
        self.setWavelengthVoltageSweeps['IV'].append(iv)
        self.setWavelengthVoltageSweeps['RV'].append(rv)
        self.setWavelengthVoltageSweeps['PV'].append(pv)
        self.setWavelengthVoltageSweeps['ChannelA'].append(a)
        self.setWavelengthVoltageSweeps['ChannelB'].append(b)
        self.setWavelengthVoltageSweeps['Wavelength'].append(wavelengths)
        self.setWavelengthVoltageSweeps['RoutineName'].append(name)
        self.hasRoutines = True

    def addSetWavelengthCurrentSweep(self, name, currentmin, currentmax, currentres, iv, rv, pv, a, b, wavelengths):
        """"""
        self.setWavelengthCurrentSweeps['CurrentMin'].append(currentmin)
        self.setWavelengthCurrentSweeps['CurrentMax'].append(currentmax)
        self.setWavelengthCurrentSweeps['CurrentRes'].append(currentres)
        self.setWavelengthCurrentSweeps['IV'].append(iv)
        self.setWavelengthCurrentSweeps['RV'].append(rv)
        self.setWavelengthCurrentSweeps['PV'].append(pv)
        self.setWavelengthCurrentSweeps['ChannelA'].append(a)
        self.setWavelengthCurrentSweeps['ChannelB'].append(b)
        self.setWavelengthCurrentSweeps['Wavelength'].append(wavelengths)
        self.setWavelengthCurrentSweeps['RoutineName'].append(name)
        self.hasRoutines = True

    def addSetVoltageWavelengthSweep(self, name, start, stop, stepsize, sweeppower, sweepspeed, laseroutput,
                                     numscans, initialrange, rangedec, a, b, voltages):
        """"""

        self.setVoltageWavelengthSweeps['Start'].append(start)
        self.setVoltageWavelengthSweeps['Stop'].append(stop)
        self.setVoltageWavelengthSweeps['Stepsize'].append(stepsize)
        self.setVoltageWavelengthSweeps['Sweeppower'].append(sweeppower)
        self.setVoltageWavelengthSweeps['Sweepspeed'].append(sweepspeed)
        self.setVoltageWavelengthSweeps['Laseroutput'].append(laseroutput)
        self.setVoltageWavelengthSweeps['Numscans'].append(numscans)
        self.setVoltageWavelengthSweeps['InitialRange'].append(initialrange)
        self.setVoltageWavelengthSweeps['RangeDec'].append(rangedec)
        self.setVoltageWavelengthSweeps['ChannelA'].append(a)
        self.setVoltageWavelengthSweeps['ChannelB'].append(initialrange)
        self.setVoltageWavelengthSweeps['Voltage'].append(voltages)
        self.setVoltageWavelengthSweeps['RoutineName'].append(name)
        self.hasRoutines = True


    def beginMeasure(self, devices, checkList, activeDetectors, camera, abortFunction=None, updateFunction=None,
                     updateGraph=True):
        """ Runs an automated measurement. For each device, wedge probe is moved out of the way, chip stage is moved
        so laser in aligned, wedge probe is moved to position. Various tests are performed depending on the contents
        of the testing parameters file.

        The sweep results, and metadata associated with the sweep are stored in a data file which is saved to the folder specified
        in self.saveFolder. An optional abort function can be specified which is called to determine if the measurement process should
        be stopped. Also, an update function is called which can be used to update UI elements about the measurement progress.

        Args:
            devices: list of device ids for devices to be tested
            testingParameters: testing parameters dictionary created from testing parameters tab or csv upload
            checkList: checklist object from autoMeasurePanel
            abortFunction: optional function used to determine when to stop measurement
            updateFunction: optional function can be used to update UI elements
            updateGraph: Whether to update the graph in the autoMeasurePanel with each measurement."""

        self.checkList = checkList
        self.activeDetectors = activeDetectors

        print("***********************************************")

        checkedDevices = []
        for device in self.devices:
            if device.getDeviceID() in devices:
                checkedDevices.append(device)

        devices = checkedDevices

        measurement = measurementRoutines(self.smu, self.laser, self.activeDetectors)

        chipTimeStart = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())

        # For each checked device

        for i, device in enumerate(devices):

            motorCoordOpt = self.motorOpt.getPosition()
            self.devFolder = os.path.join(self.saveFolder, device.getDeviceID())
            if not os.path.exists(self.devFolder):
                os.makedirs(self.devFolder)

            camera.startrecord(path=self.devFolder)

            # Move to device
            self.moveToDevice(device.getDeviceID())
            time.sleep(0.5)

            # Check which type of measurement is to be completed
            if device.getVoltageSweepRoutines() and self.motorElec and self.smu:
                for routine in device.getVoltageSweepRoutines():
                    timeStart = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())
                    print("Performing Voltage Sweep: {}".format(routine))
                    ii = self.voltageSweeps['RoutineName'].index(routine)
                    voltmin = self.voltageSweeps['VoltMin'][ii]
                    voltmax = self.voltageSweeps['VoltMax'][ii]
                    voltres = self.voltageSweeps['VoltRes'][ii]
                    A = self.voltageSweeps['ChannelA'][ii]
                    B = self.voltageSweeps['ChannelB'][ii]
                    IV = self.voltageSweeps['IV'][ii]
                    RV = self.voltageSweeps['RV'][ii]
                    PV = self.voltageSweeps['PV'][ii]
                    VoltA, CurA, ResA, PowA, VoltB, CurB, ResB, PowB = measurement.voltageSweep(voltmin, voltmax, voltres, A, B)
                    timeStop = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())
                    if IV:
                        self.graphPanel.axes.set_xlabel('Voltage (V)')
                        self.graphPanel.axes.set_ylabel('Current (mA)')
                        self.graphPanel.canvas.sweepResultDict = {}
                        if A:
                            self.graphPanel.canvas.sweepResultDict['voltage'] = VoltA
                            self.graphPanel.canvas.sweepResultDict['current'] = CurA

                            # save all associated files
                            self.saveFiles(device, 'Voltage (V)', 'Current (mA)', ii, VoltA, CurA,
                                            'Voltage sweep', motorCoordOpt, timeStart, timeStop, chipTimeStart,
                                           self.devFolder, routine + '_IV')
                            self.drawGraph(VoltA, CurA, self.graphPanel, 'Voltage (V)', 'Current (mA)')
                        if B:
                            self.graphPanel.canvas.sweepResultDict['voltage'] = VoltB
                            self.graphPanel.canvas.sweepResultDict['current'] = CurB


                            # save all associated files
                            self.saveFiles(device, 'Voltage (V)', 'Current (mA)', ii, VoltB, CurB,
                                            'Voltage sweep', motorCoordOpt, timeStart, timeStop, chipTimeStart,
                                           self.devFolder, routine + '_IV')
                            self.drawGraph(VoltB, CurB, self.graphPanel, 'Voltage (V)', 'Current (mA)')

                    if RV:
                        self.graphPanel.canvas.sweepResultDict = {}
                        if A:
                            self.graphPanel.canvas.sweepResultDict['voltage'] = VoltA
                            self.graphPanel.canvas.sweepResultDict['resistance'] = ResA
                            self.drawGraph(VoltA, ResA, self.graphPanel, 'Voltage (V)', 'Resistance (Ohms)')

                            # save all associated files
                            self.saveFiles(device, 'Voltage (V)', 'Resistance (Ohms)', ii, VoltA, ResA,
                                            'Voltage sweep', motorCoordOpt, timeStart, timeStop, chipTimeStart,
                                           self.devFolder, routine + '_RV')

                        if B:
                            self.graphPanel.canvas.sweepResultDict['voltage'] = VoltB
                            self.graphPanel.canvas.sweepResultDict['resistance'] = ResB


                            # save all associated files
                            self.saveFiles(device, 'Voltage (V)', 'Resistance (Ohms)', ii, VoltB, ResB,
                                            'Voltage sweep', motorCoordOpt, timeStart, timeStop, chipTimeStart,
                                           self.devFolder, routine + '_RV')
                            self.drawGraph(VoltB, ResB, self.graphPanel, 'Voltage (V)', 'Resistance (Ohms)')
                    if PV:
                        self.graphPanel.canvas.sweepResultDict = {}
                        if A:
                            self.graphPanel.canvas.sweepResultDict['voltage'] = VoltA
                            self.graphPanel.canvas.sweepResultDict['power'] = PowA


                            # save all associated files
                            self.saveFiles(device, 'Voltage (V)', 'Power (W)', ii, VoltA, PowA,
                                            'Voltage sweep', motorCoordOpt, timeStart, timeStop, chipTimeStart,
                                           self.devFolder, routine + '_PV')
                            self.drawGraph(VoltA, PowA, self.graphPanel, 'Voltage (V)', 'Power (W)')

                        if B:
                            self.graphPanel.canvas.sweepResultDict['voltage'] = VoltB
                            self.graphPanel.canvas.sweepResultDict['power'] = PowB


                            # save all associated files
                            self.saveFiles(device, 'Voltage (V)', 'Power (W)', ii, VoltB, PowB,
                                             'Voltage sweep', motorCoordOpt, timeStart, timeStop, chipTimeStart,
                                           self.devFolder, routine + '_PV')
                            self.drawGraph(VoltB, PowB, self.graphPanel, 'Voltage (V)', 'Power (W)')

            if device.getCurrentSweepRoutines() and self.motorElec and self.smu:
                for routine in device.getCurrentSweepRoutines():
                    ii = self.currentSweeps['RoutineName'].index(routine)
                    timeStart = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())
                    routineName = self.currentSweeps['RoutineName'][ii]
                    print("Performing Current Sweep: {}".format(routineName))
                    imin = self.currentSweeps['CurrentMin'][ii]
                    imax = self.currentSweeps['CurrentMax'][ii]
                    ires = self.currentSweeps['CurrentRes'][ii]
                    A = self.currentSweeps['ChannelA'][ii]
                    B = self.currentSweeps['ChannelB'][ii]
                    IV = self.currentSweeps['IV'][ii]
                    RV = self.currentSweeps['RV'][ii]
                    PV = self.currentSweeps['PV'][ii]
                    VoltA, CurA, ResA, PowA, VoltB, CurB, ResB, PowB = measurement.currentSweep(imin, imax, ires, A, B)
                    timeStop = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())
                    if IV:
                        self.graphPanel.canvas.sweepResultDict = {}
                        if A:
                            self.graphPanel.canvas.sweepResultDict['voltage'] = VoltA
                            self.graphPanel.canvas.sweepResultDict['current'] = CurA


                            # save all associated files
                            self.saveFiles(device,'Current (mA)','Voltage (V)', ii, CurA, VoltA,
                                            'Current sweep', motorCoordOpt, timeStart, timeStop, chipTimeStart,
                                           self.devFolder, routine + '_VI')
                            self.drawGraph(CurA, VoltA, self.graphPanel, 'Current (mA)', 'Voltage (V)')
                        if B:
                            self.graphPanel.canvas.sweepResultDict['voltage'] = VoltB
                            self.graphPanel.canvas.sweepResultDict['current'] = CurB


                            # save all associated files
                            self.saveFiles(device, 'Current (mA)', 'Voltage (V)', ii, CurB, VoltB,
                                           'Current sweep', motorCoordOpt, timeStart, timeStop, chipTimeStart,
                                           self.devFolder, routine + '_VI')
                            self.drawGraph(CurB, VoltB, self.graphPanel, 'Current (mA)', 'Voltage (V)')

                    if RV:
                        self.graphPanel.canvas.sweepResultDict = {}
                        if A:
                            self.graphPanel.canvas.sweepResultDict['current'] = CurA
                            self.graphPanel.canvas.sweepResultDict['resistance'] = ResA


                            # save all associated files
                            self.saveFiles(device, 'Current (mA)', 'Resistance (Ohms)', ii, CurA, ResA,
                                            'Current sweep', motorCoordOpt, timeStart, timeStop, chipTimeStart,
                                           self.devFolder, routine + '_RI')
                            self.drawGraph(CurA, ResA, self.graphPanel, 'Current (mA)', 'Resistance (Ohms)')

                        if B:
                            self.graphPanel.canvas.sweepResultDict['current'] = CurB
                            self.graphPanel.canvas.sweepResultDict['resistance'] = ResB


                            # save all associated files
                            self.saveFiles(device, 'Current (mA)', 'Resistance (Ohms)', ii, CurB, ResB,
                                            'Current sweep', motorCoordOpt, timeStart, timeStop, chipTimeStart,
                                           self.devFolder, routine + '_RI')
                            self.drawGraph(CurB, ResB, self.graphPanel, 'Current (mA)', 'Resistance (Ohms)')
                    if PV:
                        self.graphPanel.canvas.sweepResultDict = {}
                        if A:
                            self.graphPanel.canvas.sweepResultDict['current'] = CurA
                            self.graphPanel.canvas.sweepResultDict['power'] = PowA


                            # save all associated files
                            self.saveFiles(device, 'Current (mA)', 'Power (W)', ii, CurA, PowA,
                                            'Current sweep', motorCoordOpt, timeStart, timeStop, chipTimeStart,
                                           self.devFolder, routine + '_PI')
                            self.drawGraph(CurA, PowA, self.graphPanel, 'Current (mA)', 'Power (W)')

                        if B:
                            self.graphPanel.canvas.sweepResultDict['current'] = CurB
                            self.graphPanel.canvas.sweepResultDict['power'] = PowB


                            # save all associated files
                            self.saveFiles(device, 'Current (mA)', 'Power (W)', ii, CurB, PowB,
                                            'Current sweep', motorCoordOpt, timeStart, timeStop, chipTimeStart,
                                           self.devFolder, routine + '_PI')
                            self.drawGraph(CurB, PowB, self.graphPanel, 'Current (mA)', 'Power (W)')

            if device.getWavelengthSweepRoutines() and self.laser:
                for routine in device.getWavelengthSweepRoutines():
                    ii = self.wavelengthSweeps['RoutineName'].index(routine)
                    timeStart = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())
                    routineName = self.wavelengthSweeps['RoutineName'][ii]
                    print("Performing Optical Test {}".format(routineName))
                    start = self.wavelengthSweeps['Start'][ii]
                    stop = self.wavelengthSweeps['Stop'][ii]
                    stepsize = self.wavelengthSweeps['Stepsize'][ii]
                    sweepspeed = self.wavelengthSweeps['Sweepspeed'][ii]
                    sweeppower = self.wavelengthSweeps['Sweeppower'][ii]
                    laseroutput = self.wavelengthSweeps['Laseroutput'][ii]
                    numscans = self.wavelengthSweeps['Numscans'][ii]
                    initrange = self.wavelengthSweeps['InitialRange'][ii]
                    rangedec = self.wavelengthSweeps['RangeDec'][ii]
                    wav, pow = measurement.opticalSweep(start, stop, stepsize, sweepspeed, sweeppower,
                                                        laseroutput, numscans, initrange, rangedec)
                    timeStop = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())

                    self.graphPanel.canvas.sweepResultDict = {}
                    self.graphPanel.canvas.sweepResultDict['wavelength'] = wav
                    self.graphPanel.canvas.sweepResultDict['power'] = pow
                    if len(self.activeDetectors) > 1:
                        self.detstringlist = ['Detector Slot ' + str(self.activeDetectors[0] + 1)]
                        for det in self.activeDetectors:
                            if det == self.activeDetectors[0]:
                                pass
                            else:
                                self.detstringlist.append('Detector Slot ' + str(det + 1))


                    # save all associated files
                    self.saveFiles(device, 'Wavelength (nm)', 'Power (dBm)', ii, wav * 1e9, pow,
                                    'Wavelength sweep', motorCoordOpt, timeStart, timeStop, chipTimeStart,
                                   self.devFolder, routine, leg = 1)

                    self.drawGraph(wav * 1e9, pow, self.graphPanel, 'Wavelength (nm)', 'Power (dBm)', legend=0)

            if device.getSetWavelengthVoltageSweepRoutines() and self.laser and self.motorElec and self.smu:
                for routine in device.getSetWavelengthVoltageSweepRoutines():
                    ii = self.setWavelengthVoltageSweeps['RoutineName'].index(routine)
                    timeStart = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())
                    print("Performing Voltage Sweep with set wavelength")
                    voltmin = self.setWavelengthVoltageSweeps['VoltMin'][ii]
                    voltmax = self.setWavelengthVoltageSweeps['VoltMax'][ii]
                    voltres = self.setWavelengthVoltageSweeps['VoltRes'][ii]
                    A = self.setWavelengthVoltageSweeps['ChannelA'][ii]
                    B = self.setWavelengthVoltageSweeps['ChannelB'][ii]
                    IV = self.setWavelengthVoltageSweeps['IV'][ii]
                    RV = self.setWavelengthVoltageSweeps['RV'][ii]
                    PV = self.setWavelengthVoltageSweeps['PV'][ii]
                    wavelengths = self.setWavelengthVoltageSweeps['Wavelength'][ii].split(',')

                    VoltA = [[]for _ in range(len(wavelengths))]
                    CurA = [[]for _ in range(len(wavelengths))]
                    VoltB = [[]for _ in range(len(wavelengths))]
                    CurB = [[]for _ in range(len(wavelengths))]
                    ResA = [[]for _ in range(len(wavelengths))]
                    PowA = [[]for _ in range(len(wavelengths))]
                    ResB = [[]for _ in range(len(wavelengths))]
                    PowB = [[]for _ in range(len(wavelengths))]

                    for l, wavelength in enumerate(wavelengths):
                        VoltA[l], CurA[l], ResA[l], PowA[l], VoltB[l], CurB[l], ResB[l], PowB[l] = \
                            measurement.fixedWavelengthVoltageSweep(voltmin, voltmax, voltres, A, B, wavelength)
                        timeStop = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())

                    if IV:
                        self.graphPanel.canvas.sweepResultDict = {}
                        if A:
                            for wav in range(len(wavelengths)):
                                self.graphPanel.canvas.sweepResultDict['voltage'] = VoltA[wav]
                                self.graphPanel.canvas.sweepResultDict['current'] = CurA[wav]
                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Current (mA)', ii, VoltA[wav], CurA[wav],
                                               'Voltage Sweep w Set Wavelength',
                                               motorCoordOpt, timeStart, timeStop, chipTimeStart, self.devFolder,
                                               routine + str(wavelengths[wav]) + '_VI_A')
                                self.drawGraph(VoltA[wav], CurA[wav], self.graphPanel, 'Voltage (V)', 'Current (mA)', legend=0)

                            vol3 = [[]]
                            cur3 = [[]]
                            for i in range(len(VoltA[0]) - 1):
                                vol3.append([])
                                cur3.append([])
                            for p in range(len(VoltA[ii])):
                                for v in range(len(wavelengths)):
                                    vol3[p].append(VoltA[v][p] )
                                    cur3[p].append(CurA[v][p])

                            self.wavstringlist = [str(wav) + ' nm' for wav in wavelengths]

                            self.graphPanel.canvas.sweepResultDict['voltage'] = vol3
                            self.graphPanel.canvas.sweepResultDict['current'] = cur3

                            # save all associated files
                            self.saveFiles(device, 'Voltage (V)', 'Current (mA)', ii,vol3, cur3, 'Voltage Sweep w Set Wavelength',
                                               motorCoordOpt, timeStart, timeStop, chipTimeStart, self.devFolder,
                                               routine + 'combined' + '_VI_A', leg = 3)
                            self.drawGraph(vol3, cur3, self.graphPanel, 'Voltage (V)', 'Current (mA)', legend=3)

                        if B:
                            for wav in range(len(wavelengths)):
                                self.graphPanel.canvas.sweepResultDict['voltage'] = VoltA[wav]
                                self.graphPanel.canvas.sweepResultDict['current'] = CurA[wav]

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Current (mA)', ii, VoltA[wav], CurA[wav],
                                               'Voltage Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                               chipTimeStart, self.devFolder, routine + str(wavelengths[wav]) + '_VI_B')
                                self.drawGraph(VoltA[wav], CurA[wav], self.graphPanel, 'Voltage (V)', 'Current (mA)',
                                               legend=0)

                            vol3 = [[]]
                            cur3 = [[]]
                            for i in range(len(VoltB[0]) - 1):
                                vol3.append([])
                                cur3.append([])
                            for p in range(len(VoltB[ii])):
                                for v in range(len(wavelengths)):
                                    vol3[p].append(VoltB[v][p])
                                    cur3[p].append(CurB[v][p])

                            self.wavstringlist = [str(wav) + ' nm' for wav in wavelengths]

                            self.graphPanel.canvas.sweepResultDict['voltage'] =vol3
                            self.graphPanel.canvas.sweepResultDict['current'] = cur3

                            # save all associated files
                            self.saveFiles(device, 'Voltage (V)', 'Current (mA)', ii, vol3, cur3,
                                                    'Voltage Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                                    chipTimeStart, self.devFolder, routine + 'combined' + '_VI_B', leg = 3)
                            self.drawGraph(vol3, cur3, self.graphPanel, 'Voltage (V)', 'Current (mA)',
                                                    legend=3)

                    if RV:
                        self.graphPanel.canvas.sweepResultDict = {}
                        if A:
                            for wav in range(len(wavelengths)):
                                self.graphPanel.canvas.sweepResultDict['voltage'] = VoltA[wav]
                                self.graphPanel.canvas.sweepResultDict['resistance'] = ResA[wav]

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Resistance (Ohms)', ii, VoltA[wav], ResA[wav],
                                               'Voltage Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                               chipTimeStart, self.devFolder, routine + str(wavelengths[wav]) + '_VR_A')
                                self.drawGraph(VoltA[wav], ResA[wav], self.graphPanel, 'Voltage (V)', 'Resistance (Ohms)',
                                               legend=0)

                            vol3 = [[]]
                            res3 = [[]]
                            for i in range(len(VoltA[0]) - 1):
                                vol3.append([])
                                res3.append([])
                            for p in range(len(VoltA[ii])):
                                for v in range(len(wavelengths)):
                                    vol3[p].append(VoltA[v][p])
                                    res3[p].append(ResA[v][p])

                            self.wavstringlist = [str(wav) + ' nm' for wav in wavelengths]
                            for wav in wavelengths:
                                if wav == wavelengths[0]:
                                    pass
                                else:
                                    self.wavstringlist.append(str(wav) + ' nm')

                            self.graphPanel.canvas.sweepResultDict['voltage'] = vol3
                            self.graphPanel.canvas.sweepResultDict['resistance'] = res3

                            # save all associated files
                            self.saveFiles(device, 'Voltage (V)', 'Resistance (Ohms)', ii, vol3, res3,
                                                   'Voltage Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                                   chipTimeStart, self.devFolder, routine + 'combined' + '_RV', leg = 3)
                            self.drawGraph(vol3, res3, self.graphPanel, 'Voltage (V)', 'Resistance (Ohms)',
                                                   legend=3)

                        if B:
                            for wav in range(len(wavelengths)):
                                self.graphPanel.canvas.sweepResultDict['voltage'] = VoltB[wav]
                                self.graphPanel.canvas.sweepResultDict['resistance'] = ResB[wav]

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Resistance (Ohms)', ii, VoltB[wav], ResB[wav],
                                               'Voltage Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                               chipTimeStart, self.devFolder, routine + str(wavelengths[wav]) + '_VR_B')
                                self.drawGraph(VoltB[wav], ResB[wav], self.graphPanel, 'Voltage (V)', 'Resistance (Ohms)',
                                               legend=0)

                            vol3 = [[]]
                            res3 = [[]]
                            for i in range(len(VoltB[0]) - 1):
                                vol3.append([])
                                res3.append([])
                            for p in range(len(VoltB[ii])):
                                for v in range(len(wavelengths)):
                                    vol3[p].append(VoltB[v][p])
                                    res3[p].append(ResB[v][p])

                            self.wavstringlist = [str(wav) + ' nm' for wav in wavelengths]

                            self.graphPanel.canvas.sweepResultDict['voltage'] = vol3
                            self.graphPanel.canvas.sweepResultDict['resistance'] = res3

                            # save all associated files
                            self.saveFiles(device, 'Voltage (V)', 'Resistance (Ohms)', ii, vol3, res3,
                                                   'Voltage Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                                   chipTimeStart, self.devFolder, routine + 'combined' + '_RV', leg = 3)
                            self.drawGraph(vol3, res3, self.graphPanel, 'Voltage (V)', 'Resistance (Ohms)',
                                                   legend=3)
                    if PV:
                        self.graphPanel.canvas.sweepResultDict = {}
                        if A:
                            for wav in range(len(wavelengths)):
                                self.graphPanel.canvas.sweepResultDict['voltage'] = VoltA[wav]
                                self.graphPanel.canvas.sweepResultDict['power'] = PowA[wav]

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Power (W)', ii, VoltA[wav], PowA[wav],
                                               'Voltage Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                               chipTimeStart, self.devFolder, routine + str(wavelengths[wav]) + '_VP_A')
                                self.drawGraph(VoltA[wav], PowA[wav], self.graphPanel, 'Voltage (V)', 'Power (W)',
                                               legend=0)
                            vol3 = [[]]
                            pow3 = [[]]
                            for i in range(len(VoltA[0]) - 1):
                                vol3.append([])
                                pow3.append([])
                            for p in range(len(VoltA[ii])):
                                for v in range(len(wavelengths)):
                                    vol3[p].append(VoltA[v][p])
                                    pow3[p].append(PowA[v][p])

                            self.wavstringlist = [str(wav) + ' nm' for wav in wavelengths]

                            self.graphPanel.canvas.sweepResultDict['voltage'] = vol3
                            self.graphPanel.canvas.sweepResultDict['power'] = pow3

                            # save all associated files
                            self.saveFiles(device, 'Voltage (V)', 'Power (W)', ii, vol3, pow3,
                                                'Voltage Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                                chipTimeStart, self.devFolder, routine + 'combined' + '_PV', leg = 3)
                            self.drawGraph(vol3, pow3, self.graphPanel, 'Voltage (V)', 'Power (W)',
                                                   legend=3)

                        if B:
                            for wav in range(len(wavelengths)):
                                self.graphPanel.canvas.sweepResultDict['voltage'] = VoltB[wav]
                                self.graphPanel.canvas.sweepResultDict['power'] = PowB[wav]

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Power (W)', ii, VoltB[wav], PowB[wav],
                                               'Voltage Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                               chipTimeStart, self.devFolder, routine + str(wavelengths[wav]) + '_VP_B')
                                self.drawGraph(VoltB[wav], PowB[wav], self.graphPanel, 'Voltage (V)', 'Power (W)',
                                               legend=0)
                            vol3 = [[]]
                            pow3 = [[]]
                            for i in range(len(VoltB[0]) - 1):
                                vol3.append([])
                                pow3.append([])
                            for p in range(len(VoltB[ii])):
                                for v in range(len(wavelengths)):
                                    vol3[p].append(VoltB[v][p])
                                    pow3[p].append(PowB[v][p])

                            self.wavstringlist = [str(wav) + ' nm' for wav in wavelengths]

                            self.graphPanel.canvas.sweepResultDict['voltage'] = vol3
                            self.graphPanel.canvas.sweepResultDict['power'] = pow3

                            # save all associated files
                            self.saveFiles(device, 'Voltage (V)', 'Power (W)', ii, vol3, pow3,
                                                   'Voltage Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                                   chipTimeStart, self.devFolder, routine + 'combined' + '_PV', leg = 3)
                            self.drawGraph(vol3, pow3, self.graphPanel, 'Voltage (V)', 'Power (W)',
                                                   legend=3)

            if device.getSetWavelengthCurrentSweepRoutines() and self.laser and self.motorElec and self.smu:
                currentSweeps = device.getSetWavelengthCurrentSweepRoutines()
                for routine in currentSweeps:
                    ii = self.setWavelengthCurrentSweeps['RoutineName'].index(routine)
                    timeStart = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())
                    print("Performing Current Sweep with set wavelength")
                    imin = self.setWavelengthCurrentSweeps['CurrentMin'][ii]
                    imax = self.setWavelengthCurrentSweeps['CurrentMax'][ii]
                    ires = self.setWavelengthCurrentSweeps['CurrentRes'][ii]
                    A = self.setWavelengthCurrentSweeps['ChannelA'][ii]
                    B = self.setWavelengthCurrentSweeps['ChannelB'][ii]
                    IV = self.setWavelengthCurrentSweeps['IV'][ii]
                    RV = self.setWavelengthCurrentSweeps['RV'][ii]
                    PV = self.setWavelengthCurrentSweeps['PV'][ii]
                    wavelengths = self.setWavelengthCurrentSweeps['Wavelength'][ii].split(',')

                    VoltA = [[]for _ in range(len(wavelengths))]
                    CurA = [[]for _ in range(len(wavelengths))]
                    VoltB = [[]for _ in range(len(wavelengths))]
                    CurB = [[]for _ in range(len(wavelengths))]
                    ResA = [[]for _ in range(len(wavelengths))]
                    PowA = [[]for _ in range(len(wavelengths))]
                    ResB = [[]for _ in range(len(wavelengths))]
                    PowB = [[]for _ in range(len(wavelengths))]

                    for l, wavelength in enumerate(wavelengths):
                        VoltA[l], CurA[l], ResA[l], PowA[l], VoltB[l], CurB[l], ResB[l], PowB[l] = \
                            measurement.fixedWavelengthCurrentSweep(imin, imax, ires, A, B, wavelength)
                        timeStop = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())
                    if IV:
                        self.graphPanel.canvas.sweepResultDict = {}
                        if A:
                            for wav in range(len(wavelengths)):
                                self.graphPanel.canvas.sweepResultDict['voltage'] = VoltA[wav]
                                self.graphPanel.canvas.sweepResultDict['current'] = CurA[wav]

                                # save all associated files
                                self.saveFiles(device, 'Current (mA)', 'Voltage (V)', ii, CurA[wav], VoltA[wav],
                                               'Current Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                               chipTimeStart, self.devFolder, routine + str(wavelengths[wav]) + '_IV_A')
                                self.drawGraph(CurA[wav], VoltA[wav], self.graphPanel, 'Current (mA)', 'Voltage (V)', legend=0)

                            vol3 = [[]]
                            cur3 = [[]]
                            for b in range(len(VoltA[0]) - 1):
                                vol3.append([])
                                cur3.append([])
                            for p in range(len(VoltA[l])):
                                for v in range(len(wavelengths)):
                                    vol3[p].append(VoltA[v][p])
                                    cur3[p].append(CurA[v][p])

                            self.wavstringlist = [str(wav) + ' nm' for wav in wavelengths]

                            self.graphPanel.canvas.sweepResultDict['voltage'] = vol3
                            self.graphPanel.canvas.sweepResultDict['current'] = cur3

                            # save all associated files
                            self.saveFiles(device,  'Current (mA)','Voltage (V)', ii,  cur3, vol3,
                                            'Current Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                            chipTimeStart, self.devFolder, routine+'combined' + '_IV_A', leg = 3)
                            self.drawGraph(cur3,vol3, self.graphPanel,  'Current (mA)', 'Voltage (V)',legend = 3)

                        if B:
                            for wav in range(len(wavelengths)):
                                self.graphPanel.canvas.sweepResultDict['voltage'] = VoltB[wav]
                                self.graphPanel.canvas.sweepResultDict['current'] = CurB[wav]

                                # save all associated files
                                self.saveFiles(device, 'Current (mA)', 'Voltage (V)', ii, CurB[wav], VoltB[wav],
                                               'Current Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                               chipTimeStart, self.devFolder, routine + str(wavelengths[wav]) + '_IV_B')
                                self.drawGraph(CurB[wav], VoltB[wav], self.graphPanel, 'Current (mA)', 'Voltage (V)',
                                               legend=0)

                            vol3 = [[]]
                            cur3 = [[]]
                            for b in range(len(VoltB[0]) - 1):
                                vol3.append([])
                                cur3.append([])
                            for p in range(len(VoltB[l])):
                                for v in range(len(wavelengths)):
                                    vol3[p].append(VoltB[v][p])
                                    cur3[p].append(CurB[v][p])

                            self.wavstringlist = [str(wav) + ' nm' for wav in wavelengths]

                            self.graphPanel.canvas.sweepResultDict['voltage'] = vol3
                            self.graphPanel.canvas.sweepResultDict['current'] = cur3

                            # save all associated files
                            self.saveFiles(device,  'Current (mA)','Voltage (V)', ii,  cur3,vol3,
                                        'Current Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                        chipTimeStart, self.devFolder, routine + 'combined' + '_IV_B', leg = 3)
                            self.drawGraph(cur3, vol3,self.graphPanel,  'Current (mA)','Voltage (V)',
                                        legend=3)

                    if RV:
                        self.graphPanel.canvas.sweepResultDict = {}
                        if A:
                            for wav in range(len(wavelengths)):
                                self.graphPanel.canvas.sweepResultDict['resistance'] = ResA[wav]
                                self.graphPanel.canvas.sweepResultDict['current'] = CurA[wav]

                                # save all associated files
                                self.saveFiles(device, 'Current (mA)', 'Resistance (Ohms)', ii, CurA[wav], ResA[wav],
                                               'Current Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                               chipTimeStart, self.devFolder, routine + str(wavelengths[wav]) + '_IR_A')
                                self.drawGraph(CurA[wav], ResA[wav], self.graphPanel, 'Current (mA)', 'Resistance (Ohms)',
                                               legend=0)
                            res3 = [[]]
                            cur3 = [[]]
                            for b in range(len(VoltA[0]) - 1):
                                res3.append([])
                                cur3.append([])
                            for p in range(len(VoltA[l])):
                                for v in range(len(wavelengths)):
                                    res3[p].append(ResA[v][p] )
                                    cur3[p].append(CurA[v][p])

                            self.wavstringlist = [str(wav) + ' nm' for wav in wavelengths]

                            self.graphPanel.canvas.sweepResultDict['resistance'] = res3
                            self.graphPanel.canvas.sweepResultDict['current'] = cur3

                            # save all associated files
                            self.saveFiles(device,  'Current (mA)','Resistance (Ohms)', ii,  cur3,res3,
                                            'Current Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                            chipTimeStart, self.devFolder, routine+ 'combined' + '_IR_A', leg = 3)
                            self.drawGraph(cur3,res3, self.graphPanel,  'Current (mA)', 'Resistance (Ohms)',legend = 3)

                        if B:
                            for wav in range(len(wavelengths)):
                                self.graphPanel.canvas.sweepResultDict['resistance'] = ResB[wav]
                                self.graphPanel.canvas.sweepResultDict['current'] =  CurB[wav]

                                # save all associated files
                                self.saveFiles(device, 'Current (mA)', 'Resistance (Ohms)', ii, CurB[wav], ResB[wav],
                                               'Current Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                               chipTimeStart, self.devFolder, routine + str(wavelengths[wav]) + '_IR_B')
                                self.drawGraph(CurB[wav], ResB[wav], self.graphPanel, 'Current (mA)', 'Resistance (Ohms)',
                                               legend=0)

                            res3 = [[]]
                            cur3 = [[]]
                            for b in range(len(VoltB[0]) - 1):
                                res3.append([])
                                cur3.append([])
                            for p in range(len(VoltB[l])):
                                for v in range(len(wavelengths)):
                                    res3[p].append(VoltB[v][p])
                                    cur3[p].append(CurB[v][p])

                            self.wavstringlist = [str(wav) + ' nm' for wav in wavelengths]

                            self.graphPanel.canvas.sweepResultDict['resistance'] = res3
                            self.graphPanel.canvas.sweepResultDict['current'] = cur3

                            # save all associated files
                            self.saveFiles(device,  'Current (mA)','Resistance (Ohms)', ii,  cur3, res3,
                                            'Current Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                            chipTimeStart, self.devFolder, routine + 'combined' + '_IR_B', leg = 3)
                            self.drawGraph( cur3, res3,self.graphPanel,  'Current (mA)','Resistance (Ohms)',
                                            legend=3)

                    if PV:
                        self.graphPanel.canvas.sweepResultDict = {}
                        if A:
                            for wav in range(len(wavelengths)):
                                self.graphPanel.canvas.sweepResultDict['power'] = PowA[wav]
                                self.graphPanel.canvas.sweepResultDict['current'] = CurA[wav]
                                # save all associated files
                                self.saveFiles(device, 'Current (mA)', 'Power (W)', ii, CurA[wav], PowA[wav],
                                               'Current Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                               chipTimeStart, self.devFolder, routine + str(wavelengths[wav]) + '_IP_A')
                                self.drawGraph(CurA[wav], PowA[wav], self.graphPanel, 'Current (mA)', 'Power (W)', legend=0)

                            pow3 = [[]]
                            cur3 = [[]]
                            for b in range(len(VoltA[0]) - 1):
                                pow3.append([])
                                cur3.append([])
                            for p in range(len(VoltA[l])):
                                for v in range(len(wavelengths)):
                                    pow3[p].append(PowA[v][p] )
                                    cur3[p].append(CurA[v][p])

                            self.wavstringlist = [str(wav) + ' nm' for wav in wavelengths]

                            self.graphPanel.canvas.sweepResultDict['power'] = pow3
                            self.graphPanel.canvas.sweepResultDict['current'] = cur3

                            # save all associated files
                            self.saveFiles(device,  'Current (mA)','Power (W)', ii,  cur3, pow3,
                                             'Current Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                             chipTimeStart, self.devFolder, routine+ 'combined' + '_IP_A', leg = 3)
                            self.drawGraph(cur3,pow3, self.graphPanel,  'Current (mA)', 'Power (W)',legend = 3)

                        if B:
                            for wav in range(len(wavelengths)):
                                self.graphPanel.canvas.sweepResultDict['power'] = PowB[wav]
                                self.graphPanel.canvas.sweepResultDict['current'] = CurB[wav]

                                # save all associated files
                                self.saveFiles(device, 'Current (mA)', 'Power (W)', ii, CurB[wav], PowB[wav],
                                               'Current Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                               chipTimeStart, self.devFolder, routine + 'combined' + '_IP_B')
                                self.drawGraph(CurB[wav], PowB[wav], self.graphPanel, 'Current (mA)', 'Power (W)',
                                               legend=0)
                            pow3 = [[]]
                            cur3 = [[]]
                            for b in range(len(VoltB[0]) - 1):
                                pow3.append([])
                                cur3.append([])
                            for p in range(len(VoltB[l])):
                                for v in range(len(wavelengths)):
                                    pow3[p].append(VoltB[v][p])
                                    cur3[p].append(CurB[v][p])

                            self.wavstringlist = [str(wav) + ' nm' for wav in wavelengths]

                            self.graphPanel.canvas.sweepResultDict['power'] = pow3
                            self.graphPanel.canvas.sweepResultDict['current'] = cur3

                            # save all associated files
                            self.saveFiles(device,  'Current (mA)','Power (W)', ii,  cur3, pow3,
                                        'Current Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                        chipTimeStart, self.devFolder, routine + 'combined' + '_IP_B', leg = 3)
                            self.drawGraph( cur3, pow3,self.graphPanel,  'Current (mA)','Power (W)',
                                        legend=3)

            if device.getSetVoltageWavelengthSweepRoutines() and self.laser and self.motorElec and self.smu:
                for routine in device.getSetVoltageWavelengthSweepRoutines():
                    ii = self.setVoltageWavelengthSweeps['RoutineName'].index(routine)
                    timeStart = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())
                    print("Performing Optical Test with Bias Voltage")
                    start = self.setVoltageWavelengthSweeps['Start'][ii]
                    stop = self.setVoltageWavelengthSweeps['Stop'][ii]
                    stepsize = self.setVoltageWavelengthSweeps['Stepsize'][ii]
                    sweepspeed = self.setVoltageWavelengthSweeps['Sweepspeed'][ii]
                    sweeppower = self.setVoltageWavelengthSweeps['Sweeppower'][ii]
                    laseroutput = self.setVoltageWavelengthSweeps['Laseroutput'][ii]
                    numscans = self.setVoltageWavelengthSweeps['Numscans'][ii]
                    initrange = self.setVoltageWavelengthSweeps['InitialRange'][ii]
                    rangedec = self.setVoltageWavelengthSweeps['RangeDec'][ii]
                    A = self.setVoltageWavelengthSweeps['ChannelA'][ii]
                    B = self.setVoltageWavelengthSweeps['ChannelB'][ii]
                    voltages = self.setVoltageWavelengthSweeps['Voltage'][ii].split(',')

                    if len(self.activeDetectors) > 1:
                        self.detstringlist = ['Detector Slot ' + str(self.activeDetectors[0] + 1)]
                        for det in self.activeDetectors:
                            if det == self.activeDetectors[0]:
                                pass
                            else:
                                self.detstringlist.append('Detector Slot ' + str(det + 1))

                    wav = [[]for _ in range(len(voltages))]
                    pow = [[]for _ in range(len(voltages))]

                    for l, voltage in enumerate(voltages):
                        wav[l], pow[l] = measurement.opticalSweepWithBiasVoltage(start, stop, stepsize, sweepspeed,
                                                                            sweeppower, laseroutput, numscans,
                                                                            initrange, rangedec, voltage, A, B)


                        timeStop = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())

                        self.graphPanel.canvas.sweepResultDict = {}
                        self.graphPanel.canvas.sweepResultDict['wavelength'] = wav[l]
                        self.graphPanel.canvas.sweepResultDict['power'] = pow[l]

                        # save all associated files
                        self.saveFiles(device, 'Wavelength (nm)', 'Power (dBm)', ii, wav[l] * 1e9, pow[l],
                                        'Wavelength sweep w Bias Voltage', motorCoordOpt, timeStart, timeStop,
                                        chipTimeStart, self.devFolder, routine+str(voltage))

                        self.drawGraph(wav[l] * 1e9, pow[l], self.graphPanel, 'Wavelength (nm)', 'Power (dBm)')


                    for det in range(len(self.activeDetectors)):
                        wav3 = [[]]
                        pow3 = [[]]
                        for b in range(len(wav[0])-1):
                            wav3.append([])
                            pow3.append([])
                        for p in range(len(wav[0])):
                            for v in range(len(voltages)):
                                wav3[p].append(wav[v][p] * 1e9)
                                pow3[p].append(pow[v][p][det])

                        self.graphPanel.canvas.sweepResultDict = {}
                        self.graphPanel.canvas.sweepResultDict['wavelength'] = wav3[det]
                        self.graphPanel.canvas.sweepResultDict['power'] = pow3[det]

                        self.voltstringlist = [str(voltages[0]) + ' V']
                        for volt in voltages:
                            if volt == voltages[0]:
                                pass
                            else:
                                self.voltstringlist.append(str(volt) + ' V')

                        # save all associated files
                        self.saveFiles(device, 'Wavelength (nm)', 'Power (dBm)', ii, wav3, pow3,
                                        'Wavelength sweep w Bias Voltage', motorCoordOpt, timeStart, timeStop,
                                        chipTimeStart, self.devFolder, routine + '_combinedVoltages' + '_Detector' + str(det), 2)
                        self.drawGraph(wav3, pow3, self.graphPanel, 'Wavelength (nm)', 'Power (dBm)', legend=2)
            camera.stoprecord()

            if abortFunction is not None and abortFunction():
                print('Aborted')
                return
            if updateFunction is not None:
                updateFunction(i)

            print("Automeasure Completed, Results Saved to " + str(self.saveFolder))

    def setScale(self, x, y):
        self.xscalevar = x
        self.yscalevar = y

    def moveToDevice(self, deviceName):
        """
        Move laser and or probe to selected device
        """
        # If laser and probe are connected
        print('Moving to device')
        if self.laser and self.motorElec:
            # lift wedge probe
            self.motorElec.moveRelativeZ(1000)
            time.sleep(2)
            # move wedge probe out of the way
            elecPosition = self.motorElec.getPosition()
            if elecPosition[0] < self.motorElec.minXPosition:
                relativex = self.motorElec.minXPosition - elecPosition[0]
                self.motorElec.moveRelativeX(-relativex)
                time.sleep(2)
            selectedDevice = deviceName
            # find device object
            for device in self.devices:
                if device.getDeviceID() == selectedDevice:
                    gdsCoordOpt = (device.getOpticalCoordinates()[0], device.getOpticalCoordinates()[1])
                    motorCoordOpt = self.gdsToMotorCoordsOpt(gdsCoordOpt)
                    # Move chip stage
                    self.motorOpt.moveAbsoluteXYZ(motorCoordOpt[0], motorCoordOpt[1], motorCoordOpt[2])
                    # Fine align to device
                    res, completed = self.fineAlign.doFineAlign()
                    # If fine align fails change text colour of device to red in the checklist
                    if completed is False:
                        for ii in range(self.checkList.GetItemCount()):
                            if self.checkList.GetItemText(ii) == device.getDeviceID():
                                self.checkList.SetItemTextColour(ii, wx.Colour(255, 0, 0))
                    else:
                        # Set text to green if FineAlign Completes
                        for ii in range(self.checkList.GetItemCount()):
                            if self.checkList.GetItemText(ii) == device.getDeviceID():
                                self.checkList.SetItemTextColour(ii, wx.Colour(0, 255, 0))
                    # Find relative probe position
                    gdsCoordElec = (float(device.getElectricalCoordinates()[0][0]), float(device.getElectricalCoordinates()[0][1]))
                    motorCoordElec = self.gdsToMotorCoordsElec(gdsCoordElec)
                    optPosition = self.motorOpt.getPosition()
                    elecPosition = self.motorElec.getPosition()
                    absolutex = motorCoordElec[0] + optPosition[0]*self.xscalevar
                    absolutey = motorCoordElec[1] + optPosition[1]*self.yscalevar
                    absolutez = motorCoordElec[2]
                    relativex = absolutex[0] - elecPosition[0]
                    relativey = absolutey[0] - elecPosition[1]
                    relativez = absolutez[0] - elecPosition[2] + 20
                    # Move probe to device
                    self.motorElec.moveRelativeX(-relativex)
                    time.sleep(2)
                    self.motorElec.moveRelativeY(-relativey)
                    time.sleep(2)
                    self.motorElec.moveRelativeZ(-relativez)
                    # Fine align to device again
                    res, completed = self.fineAlign.doFineAlign()
                    # If fine align fails change text colour of device to red in the checklist
                    if completed is False:
                        for ii in range(self.checkList.GetItemCount()):
                            if self.checkList.GetItemText(ii) == device.getDeviceID():
                                self.checkList.SetItemTextColour(ii, wx.Colour(255, 0, 0))
                    else:
                        # Set text to green if FineAlign Completes
                        for ii in range(self.checkList.GetItemCount()):
                            if self.checkList.GetItemText(ii) == device.getDeviceID():
                                self.checkList.SetItemTextColour(ii, wx.Colour(0, 255, 0))

        # if laser is connected but probe isn't
        elif self.laser and not self.motorElec:
            # Calculate optical transform matrix
            selectedDevice = deviceName
            # find device object
            for device in self.devices:
                if device.getDeviceID() == selectedDevice:
                    gdsCoordOpt = (device.getOpticalCoordinates()[0], device.getOpticalCoordinates()[1])
                    motorCoordOpt = self.gdsToMotorCoordsOpt(gdsCoordOpt)
                    # Move chip stage
                    self.motorOpt.moveAbsoluteXYZ(motorCoordOpt[0], motorCoordOpt[1], motorCoordOpt[2])

                    # Fine align to device
                    res, completed = self.fineAlign.doFineAlign()
                    # If fine align fails change text colour of device to red in the checklist
                    if completed is False:
                        for ii in range(self.checkList.GetItemCount()):
                            if self.checkList.GetItemText(ii) == device.getDeviceID():
                                self.checkList.SetItemTextColour(ii, wx.Colour(255, 0, 0))
                    else:
                        # Set text to green if FineAlign Completes
                        for ii in range(self.checkList.GetItemCount()):
                            if self.checkList.GetItemText(ii) == device.getDeviceID():
                                self.checkList.SetItemTextColour(ii, wx.Colour(0, 255, 0))

        # if probe is connected but laser isn't
        elif not self.laser and self.motorElec:
            selectedDevice = deviceName
            for device in self.devices:
                if device.getDeviceID() == selectedDevice:
                    gdsCoord = (
                    float(device.getElectricalCoordinates()[0][0]), float(device.getElectricalCoordinates()[0][1]))
                    motorCoord = self.gdsToMotorCoordsElec(gdsCoord)
                    self.motorElec.moveRelativeZ(1000)
                    time.sleep(2)
                    if [self.motorOpt] and [self.motorElec]:
                        optPosition = self.motorOpt.getPosition()
                        elecPosition = self.motorElec.getPosition()
                        adjustment = self.motorOpt.getPositionforRelativeMovement()
                        absolutex = motorCoord[0] + optPosition[0]*self.xscalevar
                        absolutey = motorCoord[1] + optPosition[1]*self.yscalevar
                        absolutez = motorCoord[2]
                        relativex = absolutex[0] - elecPosition[0]
                        relativey = absolutey[0] - elecPosition[1]
                        relativez = absolutez[0] - elecPosition[2] + 20
                        self.motorElec.moveRelativeX(-relativex)
                        time.sleep(2)
                        self.motorElec.moveRelativeY(-relativey)
                        time.sleep(2)
                        self.motorElec.moveRelativeZ(-relativez)

        self.graphPanel.canvas.draw()

    def drawGraph(self, x, y, graphPanel, xlabel, ylabel, legend=0):
        graphPanel.axes.cla()
        graphPanel.axes.plot(x, y)
        if legend == 1:
            graphPanel.axes.legend(self.detstringlist)
        if legend == 2:
            graphPanel.axes.legend(self.voltstringlist)
        if legend == 3:
            graphPanel.axes.legend(self.wavstringlist)
        graphPanel.axes.ticklabel_format(useOffset=False)
        self.graphPanel.axes.set_xlabel(xlabel)
        self.graphPanel.axes.set_ylabel(ylabel)
        graphPanel.canvas.draw()


    def save_pdf(self, deviceObject, x, y, xarr, yarr, saveFolder, routineName, legend):
        # Create pdf file
        path = saveFolder
        d1 = deviceObject.getDeviceID().replace(":", "")
        pdfFileName = os.path.join(path, saveFolder + "\\" + routineName + ".pdf")
        plt.figure()
        plt.plot(xarr, yarr)
        plt.xlabel(x)
        plt.ylabel(y)
        if legend == 1:
            plt.legend(self.detstringlist)
        if legend == 2:
            plt.legend(self.voltstringlist)
        if legend == 3:
            plt.legend(self.wavstringlist)
        plt.savefig(pdfFileName)
        plt.close()

    def save_mat(self, deviceObject, devNum, motorCoordOpt, xArray, yArray, x, y, saveFolder, routineName):
        path = saveFolder
        d1 = deviceObject.getDeviceID().replace(":", "")
        matFileName = os.path.join(path, saveFolder + "\\" + routineName + ".mat")

        # Save sweep data and metadata to the mat file
        matDict = dict()
        matDict['scandata'] = dict()
        matDict['metadata'] = dict()
        matDict['scandata'][x] = xArray
        matDict['scandata'][y] = yArray
        matDict['metadata']['device'] = deviceObject.getDeviceID()
        matDict['metadata']['gds_x_coord'] = deviceObject.getOpticalCoordinates()[0]
        matDict['metadata']['gds_y_coord'] = deviceObject.getOpticalCoordinates()[1]
        matDict['metadata']['motor_x_coord'] = motorCoordOpt[0]
        matDict['metadata']['motor_y_coord'] = motorCoordOpt[1]
        matDict['metadata']['motor_z_coord'] = motorCoordOpt[2]
        matDict['metadata']['measured_device_number'] = devNum
        timeSeconds = time.time()
        matDict['metadata']['time_seconds'] = timeSeconds
        matDict['metadata']['time_str'] = time.ctime(timeSeconds)
        savemat(matFileName, matDict)

    def save_csv(self, deviceObject, testType, xArray, yArray, start, stop, chipStart, motorCoords, devNum, saveFolder, routineName, xlabel, ylabel):

        path = saveFolder
        d1 = deviceObject.getDeviceID().replace(":", "")
        csvFileName = os.path.join(path, saveFolder + "\\" + routineName + ".csv")
        f = open(csvFileName, 'w', newline='')
        writer = csv.writer(f)
        textType = ["#Test:" + testType]
        writer.writerow(textType)
        user = ["#User:"]
        writer.writerow(user)
        start = ["#Start:" + start]
        writer.writerow(start)
        stop = ["#Stop:" + stop]
        writer.writerow(stop)
        devID = ["#Device ID:" + deviceObject.getDeviceID()]
        writer.writerow(devID)
        gds = ["#Device coordinates (gds):" + '(' + str(deviceObject.getOpticalCoordinates()[0]) + ', ' + str(deviceObject.getOpticalCoordinates()[1]) + ')']
        writer.writerow(gds)
        motor = ["#Device coordinates (motor):" + '(' + str(motorCoords[0]) + ', ' + str(motorCoords[1]) + ', ' + str(motorCoords[2]) + ')']
        writer.writerow(motor)
        chipStart = ["#Chip test start:" + str(chipStart)]
        writer.writerow(chipStart)
        settings = ["#Settings:"]
        writer.writerow(settings)
        laser = ["#Laser:" + self.laser.getName()]
        writer.writerow(laser)
        detector = ["#Detector:" + self.laser.getDetector()]
        writer.writerow(detector)
        if testType == 'Wavelength sweep':
            wavsweep = self.wavelengthSweeps
            speed = ["#Sweep speed:" + wavsweep['Sweepspeed'][devNum]]
            writer.writerow(speed)
            numData = ["#Number of datasets: 1"]
            writer.writerow(numData)
            laserPow = ["#Laser power:" + wavsweep['Sweeppower'][devNum]]
            writer.writerow(laserPow)
            stepSize = ["#Wavelength step-size:" + wavsweep['Stepsize'][devNum]]
            writer.writerow(stepSize)
            startWav = ["#Start wavelength:" + wavsweep['Start'][devNum]]
            writer.writerow(startWav)
            stopWav = ["#Stop wavelength:" + wavsweep['Stop'][devNum]]
            writer.writerow(stopWav)
            stitCount = ["#Stitch count: 0"]
            writer.writerow(stitCount)
            initRange = ["#Init Range:" + wavsweep['InitialRange'][devNum]]
            writer.writerow(initRange)
            newSweep = ["#New sweep plot behaviour: replace"]
            writer.writerow(newSweep)
            laseOff = ["#Turn off laser when done: no"]
            writer.writerow(laseOff)
            metric = ["#Metric Tag"]
            writer.writerow(metric)
            wavSweep = [xlabel]
            wavSweep.extend(xArray)
            writer.writerow(wavSweep)
            for x in range(len(self.activeDetectors)):
                det1 = ["channel_{}".format(self.activeDetectors[x] + 1)]
                for point in range(len(yArray)):
                    det1.append(yArray[point][x])
                writer.writerow(det1)
        if testType == 'Wavelength sweep w Bias Voltage':
            wavsweep = self.setVoltageWavelengthSweeps
            BiasV = ["#Bias Voltage:" + wavsweep['Voltage'][devNum]]
            writer.writerow(BiasV)
            speed = ["#Sweep speed:" + wavsweep['Sweepspeed'][devNum]]
            writer.writerow(speed)
            numData = ["#Number of datasets: 1"]
            writer.writerow(numData)
            laserPow = ["#Laser power:" + wavsweep['Sweeppower'][devNum]]
            writer.writerow(laserPow)
            stepSize = ["#Wavelength step-size:" + wavsweep['Stepsize'][devNum]]
            writer.writerow(stepSize)
            startWav = ["#Start wavelength:" + wavsweep['Start'][devNum]]
            writer.writerow(startWav)
            stopWav = ["#Stop wavelength:" + wavsweep['Stop'][devNum]]
            writer.writerow(stopWav)
            stitCount = ["#Stitch count: 0"]
            writer.writerow(stitCount)
            initRange = ["#Init Range:" + wavsweep['InitialRange'][devNum]]
            writer.writerow(initRange)
            newSweep = ["#New sweep plot behaviour: replace"]
            writer.writerow(newSweep)
            laseOff = ["#Turn off laser when done: no"]
            writer.writerow(laseOff)
            metric = ["#Metric Tag"]
            writer.writerow(metric)
            wavSweep = [xlabel]
            wavSweep.extend(xArray)
            writer.writerow(wavSweep)
            for x in range(len(self.activeDetectors)):
                det1 = ["channel_{}".format(self.activeDetectors[x] + 1)]
                for point in range(len(yArray)):
                    det1.append(yArray[point][x])
                writer.writerow(det1)
        if testType == 'Voltage sweep':
            iv = self.voltageSweeps
            stepSize = ["Resolution:" + iv['VoltRes'][devNum]]
            writer.writerow(stepSize)
            startWav = ["#Start Voltage:" + iv['VoltMin'][devNum]]
            writer.writerow(startWav)
            stopWav = ["#Stop Voltage:" + iv['VoltMax'][devNum]]
            writer.writerow(stopWav)
            wavSweep = [xlabel]
            wavSweep.extend(xArray)
            writer.writerow(wavSweep)
            det1 = [ylabel]
            for point in range(len(yArray)):
                det1.append(yArray[point])
            writer.writerow(det1)
        if testType == 'Current sweep':
            iv = self.currentSweeps
            stepSize = ["Resolution:" + iv['CurrentRes'][devNum]]
            writer.writerow(stepSize)
            startWav = ["#Start Current:" + iv['CurrentMin'][devNum]]
            writer.writerow(startWav)
            stopWav = ["#Stop Current:" + iv['CurrentMax'][devNum]]
            writer.writerow(stopWav)
            stitCount = ["#Stitch count: 0"]
            writer.writerow(stitCount)
            wavSweep = [xlabel]
            wavSweep.extend(xArray)
            writer.writerow(wavSweep)
            det1 = [ylabel]
            for point in range(len(yArray)):
                det1.append(yArray[point])
            writer.writerow(det1)
        if testType == 'Voltage Sweep w Set Wavelength':
            iv = self.setWavelengthVoltageSweeps
            wav = ["Wavelength:" + iv['Wavelength'][devNum]]
            writer.writerow(wav)
            stepSize = ["Resolution:" + iv['VoltRes'][devNum]]
            writer.writerow(stepSize)
            startWav = ["#Start Voltage:" + iv['VoltMin'][devNum]]
            writer.writerow(startWav)
            stopWav = ["#Stop Voltage:" + iv['VoltMax'][devNum]]
            writer.writerow(stopWav)
            wavSweep = [xlabel]
            wavSweep.extend(xArray)
            writer.writerow(wavSweep)
            det1 = [ylabel]
            for point in range(len(yArray)):
                det1.append(yArray[point])
            writer.writerow(det1)
        if testType == 'Current Sweep w Set Wavelength':
            iv = self.setWavelengthCurrentSweeps
            wav = ["Wavelength:" + iv['Wavelength'][devNum]]
            writer.writerow(wav)
            stepSize = ["Resolution:" + iv['CurrentRes'][devNum]]
            writer.writerow(stepSize)
            startWav = ["#Start Current:" + iv['CurrentMin'][devNum]]
            writer.writerow(startWav)
            stopWav = ["#Stop Current:" + iv['CurrentMax'][devNum]]
            writer.writerow(stopWav)
            stitCount = ["#Stitch count: 0"]
            writer.writerow(stitCount)
            wavSweep = [xlabel]
            wavSweep.extend(xArray)
            writer.writerow(wavSweep)
            det1 = [ylabel]
            for point in range(len(yArray)):
                det1.append(yArray[point])
            writer.writerow(det1)
        f.close()

    def saveFiles(self, deviceObject, x, y, devNum, xArray, yArray, testType, motorCoord, start, stop, chipStart, saveFolder, routineName, leg = 0):
        self.save_pdf(deviceObject, x, y, xArray, yArray, saveFolder, routineName, legend = leg)
        self.save_mat(deviceObject, devNum, motorCoord, xArray, yArray, x, y, saveFolder, routineName)
        self.save_csv(deviceObject, testType, xArray, yArray, start, stop, chipStart, motorCoord, devNum, saveFolder, routineName, x, y)


class CoordinateTransformException(Exception):
    pass
