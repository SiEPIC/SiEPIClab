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
import myMatplotlibPanel
import myMatplotlibPanel_pyplot


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
        reg = re.compile(r'(.-?[0-9]*),(.-?[0-9]*),(T(E|M)),([0-9]+),(.+?),(.+),(.*)')
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
                                device.addElectricalCoordinates(matchRes[3], float(matchRes[0]), float(matchRes[1]))
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
        for wavelength in wavelengths:
            self.setWavelengthVoltageSweeps['VoltMin'].append(voltmin)
            self.setWavelengthVoltageSweeps['VoltMax'].append(voltmax)
            self.setWavelengthVoltageSweeps['VoltRes'].append(voltres)
            self.setWavelengthVoltageSweeps['IV'].append(iv)
            self.setWavelengthVoltageSweeps['RV'].append(rv)
            self.setWavelengthVoltageSweeps['PV'].append(pv)
            self.setWavelengthVoltageSweeps['ChannelA'].append(a)
            self.setWavelengthVoltageSweeps['ChannelB'].append(b)
            self.setWavelengthVoltageSweeps['Wavelength'].append(wavelength)
            self.setWavelengthVoltageSweeps['RoutineName'].append(name)
            self.hasRoutines = True

    def addSetWavelengthCurrentSweep(self, name, currentmin, currentmax, currentres, iv, rv, pv, a, b, wavelengths):
        """"""
        for wavelength in wavelengths:
            self.setWavelengthCurrentSweeps['CurrentMin'].append(currentmin)
            self.setWavelengthCurrentSweeps['CurrentMax'].append(currentmax)
            self.setWavelengthCurrentSweeps['CurrentRes'].append(currentres)
            self.setWavelengthCurrentSweeps['IV'].append(iv)
            self.setWavelengthCurrentSweeps['RV'].append(rv)
            self.setWavelengthCurrentSweeps['PV'].append(pv)
            self.setWavelengthCurrentSweeps['ChannelA'].append(a)
            self.setWavelengthCurrentSweeps['ChannelB'].append(b)
            self.setWavelengthCurrentSweeps['Wavelength'].append(wavelength)
            self.setWavelengthCurrentSweeps['RoutineName'].append(name)
            self.hasRoutines = True

    def addSetVoltageWavelengthSweep(self, name, start, stop, stepsize, sweeppower, sweepspeed, laseroutput,
                                     numscans, initialrange, rangedec, a, b, voltages):
        """"""
        for voltage in voltages:
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
            self.setVoltageWavelengthSweeps['Voltage'].append(voltage)
            self.setVoltageWavelengthSweeps['RoutineName'].append(name)
            self.hasRoutines = True

    def beginMeasure(self, devices, checkList, activeDetectors, graph, camera, abortFunction=None, updateFunction=None,
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
        self.graph = graph

        checkedDevices = []
        for device in self.devices:
            if device.getDeviceID() in devices:
                checkedDevices.append(device)

        devices = checkedDevices

        measurement = measurementRoutines(self.smu, self.laser, self.activeDetectors)

        chipTimeStart = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())

        # For each checked device
        for i, device in enumerate(devices):

            camera.startrecord(path=self.saveFolder)

            # Find motor coordinates for desired device
            gdsCoordOpt = (device.getOpticalCoordinates()[0], device.getOpticalCoordinates()[1])
            motorCoordOpt = self.gdsToMotorCoordsOpt(gdsCoordOpt)
            elec = False
            if device.getElectricalCoordinates():
                gdsCoordElec = (device.getElectricalCoordinates()[0], device.getElectricalCoordinates()[1])
                motorCoordElec = self.gdsToMotorCoordsElec(gdsCoordElec)
                elec = True

            if self.motorElec:
                # move wedge probe out of the way
                self.motorElec.moveRelativeXYZElec(0, -2000, 2000)

            # move chip stage
            x = motorCoordOpt[0] - self.motorOpt.getPosition()[0]
            y = motorCoordOpt[1] - self.motorOpt.getPosition()[1]
            z = motorCoordOpt[2] - self.motorOpt.getPosition()[2]
            self.motorOpt.moveAbsoluteXYZ(motorCoordOpt[0], motorCoordOpt[1], motorCoordOpt[2])

            if device.getElectricalCoordinates():
                if elec:
                    # Move wedge probe and compensate for movement of chip stage
                    self.motorElec.moveAbsoluteXYZElec(motorCoordElec[2] - x, motorCoordElec[0] - y,
                                                       motorCoordElec[1] - z)

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

                # Check which type of measurement is to be completed

                if device.getVoltageSweeps():
                    for routine in device.getVoltageSweeps():
                        timeStart = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())
                        print("Performing Voltage Sweep {}".format(routine))
                        ii = self.voltageSweeps['RoutineName'].index(routine)
                        voltmin = self.voltageSweeps['VoltMin'][ii]
                        voltmax = self.voltageSweeps['VoltMax'][ii]
                        voltres = self.voltageSweeps['VoltRes'][ii]
                        A = self.voltageSweeps['ChannelA'][ii]
                        B = self.voltageSweeps['ChannelB'][ii]
                        IV = self.voltageSweeps['IV'][ii]
                        RV = self.voltageSweeps['RV'][ii]
                        PV = self.voltageSweeps['PV'][ii]
                        VoltA, CurA, ResA, PowA, VoltB, CurB, ResB, PowB = \
                            measurement.voltageSweep(voltmin, voltmax, voltres, A, B)
                        timeStop = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())
                        if IV:
                            self.graph.axes.set_xlabel('Voltage (V)')
                            self.graph.axes.set_ylabel('Current (A)')
                            self.graph.canvas.sweepResultDict = {}
                            if A:
                                self.graph.canvas.sweepResultDict['voltage'] = VoltA
                                self.graph.canvas.sweepResultDict['current'] = CurA
                                self.drawGraph(VoltA * 1e9, CurA, self.graph, 'Voltage (V)', 'Current (A)')

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Current (A)', ii, VoltA, CurA,
                                               'Voltage sweep', motorCoordOpt, timeStart, timeStop, chipTimeStart)
                            if B:
                                self.graph.canvas.sweepResultDict['voltage'] = VoltB
                                self.graph.canvas.sweepResultDict['current'] = CurB
                                self.drawGraph(VoltB * 1e9, CurB, self.graph, 'Voltage (V)', 'Current (A)')

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Current (A)', ii, VoltB, CurB,
                                               'Voltage sweep', motorCoordOpt, timeStart, timeStop, chipTimeStart)

                        if RV:
                            self.graph.canvas.sweepResultDict = {}
                            if A:
                                self.graph.canvas.sweepResultDict['voltage'] = VoltA
                                self.graph.canvas.sweepResultDict['resistance'] = ResA
                                self.drawGraph(VoltA * 1e9, ResA, self.graph, 'Voltage (V)', 'Resistance (Ohms)')

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Resistance (Ohms)', ii, VoltA, ResA,
                                               'Voltage sweep', motorCoordOpt, timeStart, timeStop, chipTimeStart)

                            if B:
                                self.graph.canvas.sweepResultDict['voltage'] = VoltB
                                self.graph.canvas.sweepResultDict['resistance'] = ResB
                                self.drawGraph(VoltB * 1e9, ResB, self.graph, 'Voltage (V)', 'Resistance (Ohms)')

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Resistance (Ohms)', ii, VoltB, ResB,
                                               'Voltage sweep', motorCoordOpt, timeStart, timeStop, chipTimeStart)
                        if PV:
                            self.graph.canvas.sweepResultDict = {}
                            if A:
                                self.graph.canvas.sweepResultDict['voltage'] = VoltA
                                self.graph.canvas.sweepResultDict['power'] = PowA
                                self.drawGraph(VoltA * 1e9, PowA, self.graph, 'Voltage (V)', 'Power (W)')

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Power (W)', ii, VoltA, PowA,
                                               'Voltage sweep', motorCoordOpt, timeStart, timeStop, chipTimeStart)

                            if B:
                                self.graph.canvas.sweepResultDict['voltage'] = VoltB
                                self.graph.canvas.sweepResultDict['power'] = PowB
                                self.drawGraph(VoltB * 1e9, PowB, self.graph, 'Voltage (V)', 'Power (W)')

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Power (W)', ii, VoltB, PowB,
                                               'Voltage sweep', motorCoordOpt, timeStart, timeStop, chipTimeStart)

                if device.getCurrentSweeps():
                    for routine in device.getCurrentSweeps():
                        ii = self.currentSweeps['RoutineName'].index(routine)
                        timeStart = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())
                        routineName = self.currentSweeps['Routine Name'][ii]
                        print("Performing Current Sweep {}".format(routineName))
                        imin = self.currentSweeps['CurrentMin'][ii]
                        imax = self.currentSweeps['CurrentMax'][ii]
                        ires = self.currentSweeps['CurrentRes'][ii]
                        A = self.currentSweeps['ChannelA'][ii]
                        B = self.currentSweeps['ChannelB'][ii]
                        IV = self.currentSweeps['IV'][ii]
                        RV = self.currentSweeps['RV'][ii]
                        PV = self.currentSweeps['PV'][ii]
                        VoltA, CurA, ResA, PowA, VoltB, CurB, ResB, PowB = \
                            measurement.currentSweep(imin, imax, ires, A, B)
                        timeStop = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())
                        if IV:
                            self.graph.canvas.sweepResultDict = {}
                            if A:
                                self.graph.canvas.sweepResultDict['voltage'] = VoltA
                                self.graph.canvas.sweepResultDict['current'] = CurA
                                self.drawGraph(VoltA * 1e9, CurA, self.graph, 'Voltage (V)', 'Current (A)')

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Current (A)', ii, VoltA, CurA,
                                               'Current sweep', motorCoordOpt, timeStart, timeStop, chipTimeStart)
                            if B:
                                self.graph.canvas.sweepResultDict['voltage'] = VoltB
                                self.graph.canvas.sweepResultDict['current'] = CurB
                                self.drawGraph(VoltB * 1e9, CurB, self.graph, 'Voltage (V)', 'Current (A)')

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Current (A)', ii, VoltB, CurB,
                                               'Current sweep', motorCoordOpt, timeStart, timeStop, chipTimeStart)

                        if RV:
                            self.graph.canvas.sweepResultDict = {}
                            if A:
                                self.graph.canvas.sweepResultDict['voltage'] = VoltA
                                self.graph.canvas.sweepResultDict['resistance'] = ResA
                                self.drawGraph(VoltA * 1e9, ResA, self.graph, 'Voltage (V)', 'Resistance (Ohms)')

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Resistance (Ohms)', ii, VoltA, ResA,
                                               'Current sweep', motorCoordOpt, timeStart, timeStop, chipTimeStart)

                            if B:
                                self.graph.canvas.sweepResultDict['voltage'] = VoltB
                                self.graph.canvas.sweepResultDict['resistance'] = ResB
                                self.drawGraph(VoltB * 1e9, ResB, self.graph, 'Voltage (V)', 'Resistance (Ohms)')

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Resistance (Ohms)', ii, VoltB, ResB,
                                               'Current sweep', motorCoordOpt, timeStart, timeStop, chipTimeStart)
                        if PV:
                            self.graph.canvas.sweepResultDict = {}
                            if A:
                                self.graph.canvas.sweepResultDict['voltage'] = VoltA
                                self.graph.canvas.sweepResultDict['power'] = PowA
                                self.drawGraph(VoltA * 1e9, PowA, self.graph, 'Voltage (V)', 'Power (W)')

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Power (W)', ii, VoltA, PowA,
                                               'Current sweep', motorCoordOpt, timeStart, timeStop, chipTimeStart)

                            if B:
                                self.graph.canvas.sweepResultDict['voltage'] = VoltB
                                self.graph.canvas.sweepResultDict['power'] = PowB
                                self.drawGraph(VoltB * 1e9, PowB, self.graph, 'Voltage (V)', 'Power (W)')

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Power (W)', ii, VoltB, PowB,
                                               'Current sweep', motorCoordOpt, timeStart, timeStop, chipTimeStart)

                if device.getWavelengthSweeps():
                    for routine in device.getWavelengthSweeps():
                        ii = self.wavelengthSweeps['RoutineName'].index(routine)
                        timeStart = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())
                        routineName = self.wavelengthSweeps['Routine Name'][ii]
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

                        self.graph.canvas.sweepResultDict = {}
                        self.graph.canvas.sweepResultDict['wavelength'] = wav
                        self.graph.canvas.sweepResultDict['power'] = pow
                        self.drawGraph(wav * 1e9, pow, self.graph, 'Wavelength (nm)', 'Power (dBm)')

                        # save all associated files
                        self.saveFiles(device, 'Wavelength (nm)', 'Power (dBm)', ii, wav, pow,
                                       'Wavelength sweep', motorCoordOpt, timeStart, timeStop, chipTimeStart)

                if device.getSetWavelengthVoltageSweeps():
                    for routine in device.getSetWavelengthVoltageSweeps():
                        ii = self.setWavelengthVoltageSweeps['RoutineName'].index(routine)
                        timeStart = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())
                        print("Performing Voltage Sweep with set wavelength")
                        voltmin = self.voltageSweeps['VoltMin'][ii]
                        voltmax = self.voltageSweeps['VoltMax'][ii]
                        voltres = self.voltageSweeps['VoltRes'][ii]
                        A = self.voltageSweeps['ChannelA'][ii]
                        B = self.voltageSweeps['ChannelB'][ii]
                        IV = self.voltageSweeps['IV'][ii]
                        RV = self.voltageSweeps['RV'][ii]
                        PV = self.voltageSweeps['PV'][ii]
                        wavelength = self.voltageSweeps['Wavelength'][ii]
                        VoltA, CurA, ResA, PowA, VoltB, CurB, ResB, PowB = \
                            measurement.fixedWavelengthVoltageSweep(voltmin, voltmax, voltres, A, B, wavelength)
                        timeStop = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())
                        if IV:
                            self.graph.canvas.sweepResultDict = {}
                            if A:
                                self.graph.canvas.sweepResultDict['voltage'] = VoltA
                                self.graph.canvas.sweepResultDict['current'] = CurA
                                self.drawGraph(VoltA * 1e9, CurA, self.graph, 'Voltage (V)', 'Current (A)')

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Current (A)', ii, VoltA, CurA,
                                               'Voltage Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                               chipTimeStart)
                            if B:
                                self.graph.canvas.sweepResultDict['voltage'] = VoltB
                                self.graph.canvas.sweepResultDict['current'] = CurB
                                self.drawGraph(VoltB * 1e9, CurB, self.graph, 'Voltage (V)', 'Current (A)')

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Current (A)', ii, VoltB, CurB,
                                               'Voltage Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                               chipTimeStart)

                        if RV:
                            self.graph.canvas.sweepResultDict = {}
                            if A:
                                self.graph.canvas.sweepResultDict['voltage'] = VoltA
                                self.graph.canvas.sweepResultDict['resistance'] = ResA
                                self.drawGraph(VoltA * 1e9, ResA, self.graph, 'Voltage (V)', 'Resistance (Ohms)')

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Resistance (Ohms)', ii, VoltA, ResA,
                                               'Voltage Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                               chipTimeStart)

                            if B:
                                self.graph.canvas.sweepResultDict['voltage'] = VoltB
                                self.graph.canvas.sweepResultDict['resistance'] = ResB
                                self.drawGraph(VoltB * 1e9, ResB, self.graph, 'Voltage (V)', 'Resistance (Ohms)')

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Resistance (Ohms)', ii, VoltB, ResB,
                                               'Voltage Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                               chipTimeStart)
                        if PV:

                            self.graph.canvas.sweepResultDict = {}
                            if A:
                                self.graph.canvas.sweepResultDict['voltage'] = VoltA
                                self.graph.canvas.sweepResultDict['power'] = PowA
                                self.drawGraph(VoltA * 1e9, PowA, self.graph, 'Voltage (V)', 'Power (W)')

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Power (W)', ii, VoltA, PowA,
                                               'Voltage Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                               chipTimeStart)

                            if B:
                                self.graph.canvas.sweepResultDict['voltage'] = VoltB
                                self.graph.canvas.sweepResultDict['power'] = PowB
                                self.drawGraph(VoltB * 1e9, PowB, self.graph, 'Voltage (V)', 'Power (W)')

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Power (W)', ii, VoltB, PowB,
                                               'Voltage Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                               chipTimeStart)

                if device.getSetWavelengthCurrentSweeps():
                    currentSweeps = device.getSetWavelengthCurrentSweeps()
                    for routine in device.getSetWavelengthCurrentSweeps():
                        ii = self.setWavelengthCurrentSweeps['RoutineName'].index(routine)
                        timeStart = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())
                        print("Performing Current Sweep with set wavelength")
                        imin = currentSweeps['CurrentMin'][ii]
                        imax = currentSweeps['CurrentMax'][ii]
                        ires = currentSweeps['CurrentRes'][ii]
                        A = currentSweeps['ChannelA'][ii]
                        B = currentSweeps['ChannelB'][ii]
                        IV = currentSweeps['IV'][ii]
                        RV = currentSweeps['RV'][ii]
                        PV = currentSweeps['PV'][ii]
                        wavelength = currentSweeps['Wavelength'][ii]
                        VoltA, CurA, ResA, PowA, VoltB, CurB, ResB, PowB = \
                            measurement.fixedWavelengthCurrentSweep(imin, imax, ires, A, B, wavelength)
                        timeStop = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())
                        if IV:

                            self.graph.canvas.sweepResultDict = {}
                            if A:
                                self.graph.canvas.sweepResultDict['voltage'] = VoltA
                                self.graph.canvas.sweepResultDict['current'] = CurA
                                self.drawGraph(VoltA * 1e9, CurA, self.graph, 'Voltage (V)', 'Current (A)')

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Current (A)', ii, VoltA, CurA,
                                               'Current Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                               chipTimeStart)
                            if B:
                                self.graph.canvas.sweepResultDict['voltage'] = VoltB
                                self.graph.canvas.sweepResultDict['current'] = CurB
                                self.drawGraph(VoltB * 1e9, CurB, self.graph, 'Voltage (V)', 'Current (A)')

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Current (A)', ii, VoltB, CurB,
                                               'Current Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                               chipTimeStart)

                        if RV:

                            self.graph.canvas.sweepResultDict = {}
                            if A:
                                self.graph.canvas.sweepResultDict['voltage'] = VoltA
                                self.graph.canvas.sweepResultDict['resistance'] = ResA
                                self.drawGraph(VoltA * 1e9, ResA, self.graph, 'Voltage (V)', 'Resistance (Ohms)')

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Resistance (Ohms)', ii, VoltA, ResA,
                                               'Current Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                               chipTimeStart)

                            if B:
                                self.graph.canvas.sweepResultDict['voltage'] = VoltB
                                self.graph.canvas.sweepResultDict['resistance'] = ResB
                                self.drawGraph(VoltB * 1e9, ResB, self.graph, 'Voltage (V)', 'Resistance (Ohms)')

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Resistance (Ohms)', ii, VoltB, ResB,
                                               'Current Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                               chipTimeStart)
                        if PV:

                            self.graph.canvas.sweepResultDict = {}
                            if A:
                                self.graph.canvas.sweepResultDict['voltage'] = VoltA
                                self.graph.canvas.sweepResultDict['power'] = PowA
                                self.drawGraph(VoltA * 1e9, PowA, self.graph, 'Voltage (V)','Power (W)')


                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Power (W)', ii, VoltA, PowA,
                                               'Curent Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                               chipTimeStart)

                            if B:
                                self.graph.canvas.sweepResultDict['voltage'] = VoltB
                                self.graph.canvas.sweepResultDict['power'] = PowB
                                self.drawGraph(VoltB * 1e9, PowB, self.graph, 'Voltage (V)','Power (W)')

                                # save all associated files
                                self.saveFiles(device, 'Voltage (V)', 'Power (W)', ii, VoltB, PowB,
                                               'Current Sweep w Set Wavelength', motorCoordOpt, timeStart, timeStop,
                                               chipTimeStart)

                if device.getSetVoltageWavelengthSweeps():
                    for routine in device.getSetVoltageWavelengthSweeps():
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
                        voltage = self.setVoltageWavelengthSweeps['Voltage'][ii]
                        wav, pow = measurement.opticalSweepWithBiasVoltage(start, stop, stepsize, sweepspeed,
                                                                           sweeppower, laseroutput, numscans,
                                                                           initrange, rangedec, voltage, A, B)
                        timeStop = time.strftime("%d_%b_%Y_%H_%M_%S", time.localtime())

                        self.graph.canvas.sweepResultDict = {}
                        self.graph.canvas.sweepResultDict['wavelength'] = wav
                        self.graph.canvas.sweepResultDict['power'] = pow
                        self.drawGraph(wav * 1e9, pow, self.graph, 'Wavelength (nm)', 'Power (dBm)')

                        # save all associated files
                        self.saveFiles(device, 'Wavelength (nm)', 'Power (dBm)', ii, wav, pow,
                                       'Wavelength sweep w Bias Voltage', motorCoordOpt, timeStart, timeStop,
                                       chipTimeStart)

                camera.stoprecord()

            if abortFunction is not None and abortFunction():
                print('Aborted')
                return
            if updateFunction is not None:
                updateFunction(i)

    def drawGraph(self, x, y, graphPanel, xlabel, ylabel):
        graphPanel.axes.cla()
        graphPanel.axes.plot(x, y)
        graphPanel.axes.ticklabel_format(useOffset=False)
        self.graph.axes.set_xlabel(xlabel)
        self.graph.axes.set_ylabel(ylabel)
        graphPanel.canvas.draw()


    def save_pdf(self, deviceObject, x, y, xarr, yarr):
        # Create pdf file
        path = self.saveFolder
        d1 = deviceObject.getDeviceID().replace(":", "")
        pdfFileName = os.path.join(path, self.saveFolder + "\\" + d1 + ".pdf")
        plt.figure()
        plt.plot(xarr / 1000, yarr / 1000)
        plt.xlabel(x)
        plt.ylabel(y)
        plt.savefig(pdfFileName)
        plt.close()

    def save_mat(self, deviceObject, devNum, motorCoordOpt, xArray, yArray, x, y):
        path = self.saveFolder
        d1 = deviceObject.getDeviceID().replace(":", "")
        matFileName = os.path.join(path, self.saveFolder + "\\" + d1 + ".mat")

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

    def save_csv(self, deviceObject, testType, xArray, yArray, start, stop, chipStart, motorCoords, devNum):

        path = self.saveFolder
        d1 = deviceObject.getDeviceID().replace(":", "")
        csvFileName = os.path.join(path, self.saveFolder + "\\" + d1 + ".csv")
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
        devID = ["#Device ID:" + deviceObject.getDeviceID]
        writer.writerow(devID)
        gds = ["#Device coordinates (gds):" + deviceObject.getOpticalCoordinates()]
        writer.writerow(gds)
        motor = ["#Device coordinates (motor):" + motorCoords]
        writer.writerow(motor)
        chipStart = ["#Chip test start:" + chipStart]
        writer.writerow(chipStart)
        settings = ["#Settings:"]
        writer.writerow(settings)
        laser = ["#Laser:" + self.laser.getName()]
        writer.writerow(laser)
        detector = ["#Detector:" + self.laser.getDetector()]
        writer.writerow(detector)
        if testType == "Wavelength Sweep":
            wavsweep = deviceObject.getWavelengthSweeps()
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
            wavSweep = ["wavelength", xArray]
            writer.writerow(wavSweep)
            det1 = ["channel_1", yArray]
            writer.writerow(det1)
        if testType == "Wavelength Sweep w Bias Voltage":
            wavsweep = deviceObject.getSetVoltageWavelengthSweeps()
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
            wavSweep = ["wavelength", xArray]
            writer.writerow(wavSweep)
            det1 = ["channel_1", yArray]
            writer.writerow(det1)
        if testType == 'Voltage Sweep':
            iv = deviceObject.getVoltageSweeps()
            stepSize = ["Resolution:" + iv['VoltRes'][devNum]]
            writer.writerow(stepSize)
            startWav = ["#Start Voltage:" + iv['VoltMin'][devNum]]
            writer.writerow(startWav)
            stopWav = ["#Stop Voltage:" + iv['Voltmax'][devNum]]
            writer.writerow(stopWav)
            wavSweep = ["voltage", xArray]
            writer.writerow(wavSweep)
            det1 = ["current", yArray]
            writer.writerow(det1)
        if testType == 'Current Sweep':
            iv = deviceObject.getCurrentSweeps()
            stepSize = ["Resolution:" + iv['CurrentRes'][devNum]]
            writer.writerow(stepSize)
            startWav = ["#Start Current:" + iv['CurrentMin'][devNum]]
            writer.writerow(startWav)
            stopWav = ["#Stop Current:" + iv['CurrentMax'][devNum]]
            writer.writerow(stopWav)
            stitCount = ["#Stitch count: 0"]
            writer.writerow(stitCount)
            wavSweep = ["voltage", xArray]
            writer.writerow(wavSweep)
            det1 = ["current", yArray]
            writer.writerow(det1)
        if testType == 'Voltage Sweep w Set Wavelength':
            iv = deviceObject.getSetWavelengthVoltageSweeps()
            wav = ["Wavelength:" + iv['Wavelength'][devNum]]
            writer.writerow(wav)
            stepSize = ["Resolution:" + iv['VoltRes'][devNum]]
            writer.writerow(stepSize)
            startWav = ["#Start Voltage:" + iv['VoltMin'][devNum]]
            writer.writerow(startWav)
            stopWav = ["#Stop Voltage:" + iv['Voltmax'][devNum]]
            writer.writerow(stopWav)
            wavSweep = ["voltage", xArray]
            writer.writerow(wavSweep)
            det1 = ["current", yArray]
            writer.writerow(det1)
        if testType == 'Current Sweep w Set Wavelength':
            iv = deviceObject.getSetWavelengthCurrentSweeps()
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
            wavSweep = ["voltage", xArray]
            writer.writerow(wavSweep)
            det1 = ["current", yArray]
            writer.writerow(det1)
        f.close()

    def saveFiles(self, deviceObject, x, y, devNum, xArray, yArray, testType, motorCoord, start, stop, chipStart):
        self.save_pdf(deviceObject, x, y, xArray, yArray)
        self.save_mat(deviceObject, devNum, motorCoord, xArray, yArray, x, y)
        self.save_csv(deviceObject, testType, xArray, yArray, start, stop, chipStart, motorCoord, devNum)


class CoordinateTransformException(Exception):
    pass
