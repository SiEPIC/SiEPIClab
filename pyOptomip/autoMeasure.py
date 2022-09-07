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

    def __init__(self, laser, motorOpt, motorElec, smu, fineAlign):
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

    def readCoordFile(self, fileName):
        """
        Reads a coordinate file generated using the automated coordinate extraction in k-layout.
        Stores all data as a list of ElectroOpticDevice objects, self.devices.
        Args:
            fileName: Path to desired text file, a string
        """
        with open(fileName, 'r') as f:
            data = f.readlines()

        # Remove the first line since it is the header and remove newline char  
        dataStrip = [line.strip() for line in data[1:]]
        dataStrip2 = []
        for x in dataStrip:
            j = x.replace(" ", "")
            dataStrip2.append(j)
        # x,y,polarization,wavelength,type,deviceid,params
        reg = re.compile(r'([0-9]+),([0-9]+),(T(E|M)),([0-9]+),(.+?),(.+),(.*)')
        # x, y, deviceid, padname, params
        regElec = re.compile(r'([0-9]+),([0-9]+),(.+),(.+),(.*)')

        self.devices = []
        self.devSet = set()

        # Parse the data in each line and put it into a list of devices
        for ii, line in enumerate(dataStrip2):
            if reg.match(line):
                matchRes = reg.findall(line)[0]
                devName = matchRes[6]
                if devName in self.devSet:
                    devName = "X:"+matchRes[0]+"Y:"+matchRes[1]+devName
                self.devSet.add(devName)
                device = ElectroOpticDevice(devName, matchRes[3], matchRes[2], float(matchRes[0]), float(matchRes[1]),
                                            matchRes[5])
                self.devices.append(device)
            else:
                if regElec.match(line):
                    print(line)
                    matchRes = reg.findall(line)[0]
                    devName = matchRes[2]
                    for device in self.devices:
                        if device.getDeviceID() == devName:
                            device.addElectricalCoordinates(matchRes[3], float(matchRes[0]), float(matchRes[1]))
                else:
                    if line == "" or line == "%X-coord,Y-coord,deviceID,padName,params":
                        pass
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
        motorCoordVec = self.transformMatrix*gdsCoordVec
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

        newMotorCoords = self.T@gdsVector

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

        newMotorCoords = self.TMopt@gdsVector

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

        newMotorCoords = self.TMelec@gdsVector

        return newMotorCoords

    def beginMeasure(self, devices, testingParameters, checkList, abortFunction=None, updateFunction=None,
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

        # For each device
        for i, d in enumerate(testingParameters['device']):
            for device in devices:
                if device.getDeviceID == d:

                    # Find motor coordinates for desired device
                    gdsCoordOpt = (device.getOpticalCoordinates[0], device.getOpticalCoordinates[1])
                    motorCoordOpt = self.gdsToMotorCoordsOpt(gdsCoordOpt)
                    gdsCoordElec = (device.getElectricalCoordinates[0], device.getElectricalicalCoordinates[1])
                    motorCoordElec = self.gdsToMotorCoordsElec(gdsCoordElec)

                    # move wedge probe out of the way
                    self.motorElec.moveRelativeXYZElec(motorCoordElec[0], -2000, 2000)

                    # move chip stage
                    x = motorCoordOpt[0] - self.motorOpt.getPosition[0]
                    y = motorCoordOpt[1] - self.motorOpt.getPosition[1]
                    z = motorCoordOpt[2] - self.motorOpt.getPosition[2]
                    self.motorOpt.moveAbsoluteXYZOpt(motorCoordOpt[0], motorCoordOpt[1], motorCoordOpt[2])

                    # Move wedge probe and compensate for movement of chip stage
                    self.motorElec.moveAbsoluteXYZElec(motorCoordElec[0] + x, motorCoordElec[1] + y,
                                                       motorCoordElec[2] + z)

                    # Fine align to device
                    res, completed = self.fineAlign.doFineAlign()

                    # If fine align fails change text colour of device to red in the checklist
                    if completed is False:
                        for ii in range(self.checkList.GetItemCount()):
                            if self.devices[self.checkList.GetItemData(ii)].getDeviceID() == device.getDeviceID:
                                self.checkList.SetItemTextColour(ii, wx.Colour(255, 0, 0))

                    # Check which type of measurement is to be completed
                    if testingParameters['ELECflag'][i] is True:
                        measurementRoutines('ELEC', testingParameters, i, self.smu, self.laser)
                    if testingParameters['OPTICflag'][i] is True:
                        measurementRoutines('OPT', testingParameters, i, self.smu, self.laser)
                    if testingParameters['setwflag'] is True:
                        measurementRoutines('FIXWAVIV', testingParameters, i, self.smu, self.laser)
                    if testingParameters['setvflag'] is True:
                        measurementRoutines('BIASVOPT', testingParameters, i, self.smu, self.laser)

                    print('GDS: (%g,%g) Motor: (%g,%g,%g)' % (gdsCoordOpt[0], gdsCoordOpt[1], gdsCoordOpt[2],
                                                              motorCoordOpt[0], motorCoordOpt[1]))

                    # Create matlab file
                    matFileName = os.path.join(self.saveFolder, d + '.mat')

                    # Save sweep data and metadata to the mat file
                    matDict = dict()
                    matDict['scandata'] = dict()
                    matDict['metadata'] = dict()
                    matDict['scandata']['wavelength'] = testingParameters['Wavelengths'][i]
                    matDict['scandata']['power'] = testingParameters['Sweeppower'][i]
                    matDict['metadata']['device'] = d
                    matDict['metadata']['gds_x_coord'] = device.getOpticalCoordinates[0]
                    matDict['metadata']['gds_y_coord'] = device.getOpticalCoordinates[1]
                    matDict['metadata']['motor_x_coord'] = motorCoordOpt[0]
                    matDict['metadata']['motor_y_coord'] = motorCoordOpt[1]
                    matDict['metadata']['motor_z_coord'] = motorCoordOpt[2]
                    matDict['metadata']['measured_device_number'] = i
                    timeSeconds = time.time()
                    matDict['metadata']['time_seconds'] = timeSeconds
                    matDict['metadata']['time_str'] = time.ctime(timeSeconds)
                    savemat(matFileName, matDict)

                    # Create pdf file
                    pdfFileName = os.path.join(self.saveFolder, d + '.pdf')
                    plt.figure()
                    plt.plot(testingParameters['Wavelengths'][i] * 1e9, testingParameters['Sweeppower'][i])
                    plt.xlabel('Wavelength (nm)')
                    plt.ylabel('Power (dBm)')
                    plt.savefig(pdfFileName)
                    plt.close()

            if abortFunction is not None and abortFunction():
                print('Aborted')
                return
            if updateFunction is not None:
                updateFunction(i)


class CoordinateTransformException(Exception):
    pass
