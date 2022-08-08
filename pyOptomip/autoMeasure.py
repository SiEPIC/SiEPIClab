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
from scipy.io import savemat
import time
import matplotlib.pyplot as plt
from collections import OrderedDict
from ElectroOpticDevice import ElectroOpticDevice
from measurementRoutines import measurementRoutines


class autoMeasure(object):

    def __init__(self, laser, motor, smu, fineAlign):
        self.laser = laser
        self.motor = motor
        self.smu = smu
        self.fineAlign = fineAlign
        self.saveFolder = os.getcwd()

    def readCoordFile(self, fileName):

        with open(fileName, 'r') as f:
            data = f.readlines()

        # Remove the first line since it is the header and remove newline char  
        dataStrip = [line.strip() for line in data[1:]]
        dataStrip2 = []
        for x in dataStrip:
            j = x.replace(" ", "")
            dataStrip2.append(j)
        # x,y,polarization,wavelength,type,deviceid,params
        reg = re.compile(r'(.*),(.*),(.*),([0-9]+),(.+),(.+),(.*)')
        # x,y,deviceid,padname,params
        regElec = re.compile(r'(.*),(.*),(.+),(.*),(.*)')

        self.devices = []

        # Parse the data in each line and put it into a list of devices
        for ii, line in enumerate(dataStrip2):
            if reg.match(line):
                matchRes = reg.findall(line)[0]
                devName = matchRes[5]
                device = ElectroOpticDevice(devName, matchRes[3], matchRes[2], float(matchRes[0]), float(matchRes[1]),
                                            matchRes[4])
                self.devices.append(device)
            else:
                if regElec.match(line):
                    matchRes = reg.findall(line)[0]
                    devName = matchRes[2]
                    for device in self.devices:
                        if device.getDeviceID() == devName:
                            device.addElectricalCoordinates(matchRes[3], float(matchRes[0]), float(matchRes[1]))
                else:
                    print('Warning: The entry\n%s\nis not formatted correctly.' % line)

    def findCoordinateTransform(self, motorCoords, gdsCoords):
        """ Finds the best fit affine transform which maps the GDS coordinates to motor coordinates."""

        # if len(motorCoords) != (len(gdsCoords)+1):
        # raise CoordinateTransformException('You must have the same number of motor coordinates and GDS coordinates')

        if len(motorCoords) < 3:
            raise CoordinateTransformException('You must have at least 3 device coordinates.')

        numTriples = len(motorCoords)

        Xgds = mat(zeros((numTriples + 1, numTriples)))  # 4x3
        Xmotor = mat(zeros((numTriples + 1, numTriples)))  # 4x3

        # zip: [0,Dev1MotorCoords,Dev1gds], [1,Dev2MotorCoords,Dev2gds], [2,Dev3MotorCoords,Dev3gds]
        for i, motorCoord, gdsCoord in zip(range(numTriples), motorCoords, gdsCoords):
            Xgds[0, i] = gdsCoord[0]
            Xgds[1, i] = gdsCoord[1]
            Xgds[2, i] = 0
            Xgds[3, i] = 1
            Xmotor[0, i] = motorCoord[0]
            Xmotor[1, i] = motorCoord[1]
            Xmotor[2, i] = motorCoord[2]
            Xmotor[3, i] = 1

        # Do least squares fitting
        M = linalg.lstsq(Xgds, Xmotor, rcond=-1)

        self.transformMatrix = M

        return M

    def gdsToMotorCoords(self, gdsCoords):
        """ Uses the calculated affine transform to map a GDS coordinate to a motor coordinate."""
        gdsCoordVec = mat([[gdsCoords[0]], [gdsCoords[1]], [0], [1]])
        motorCoordVec = self.transformMatrix * gdsCoordVec
        motorCoords = (float(motorCoordVec[0]), float(motorCoordVec[1]), float(motorCoordVec[2]))
        return motorCoords

    def beginMeasure(self, devices, testingParameters, abortFunction=None, updateFunction=None, updateGraph=True):
        """ Runs an automated measurement. For each device, wedge probe is moved out of the way, chip stage is moved
        so laser in aligned, wedge probe is moved to position. Various tests are performed depending on the contents
        of the testing parameters file.

        The sweep results, and metadata associated with the sweep are stored in a data file which is saved to the folder specified
        in self.saveFolder. An optional abort function can be specified which is called to determine if the measurement process should
        be stopped. Also, an update function is called which can be used to update UI elements about the measurement progress."""

        for i, d in enumerate(testingParameters['device']):
            for device in devices:
                if device.getDeviceID == d:
                    gdsCoordOpt = (device.getOpticalCoordinates[0], device.getOpticalCoordinates[1])
                    motorCoordOpt = self.gdsToMotorCoords(gdsCoordOpt)
                    gdsCoordElec = (device.getElectricalCoordinates[0], device.getElectricalicalCoordinates[1])
                    motorCoordElec = self.gdsToMotorCoords(gdsCoordElec)

                    #move wedge probe out of the way
                    self.motor.moveRelativeXYZElec(motorCoordElec[0], -2000, 2000)
                    #move chip stage
                    x = motorCoordOpt[0] - self.motor.getPosition[0]
                    y = motorCoordOpt[1] - self.motor.getPosition[1]
                    z = motorCoordOpt[2] - self.motor.getPosition[2]
                    self.motor.moveAbsoluteXYZOpt(motorCoordOpt[0], motorCoordOpt[1], motorCoordOpt[2])
                    #Move wedge probe and compensate for movement of chip stage
                    self.motor.moveAbsoluteXYZElec(motorCoordElec[0]+x, motorCoordElec[1]+y, motorCoordElec[2]+z)

                    self.fineAlign.doFineAlign()

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
