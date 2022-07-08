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

class autoMeasure(object):
     
    def __init__(self, laser, motor, fineAlign):
        self.laser = laser
        self.motor = motor
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
        reg = re.compile(r'(.*),(.*),(.*),(.[0-9]+),(.+),(.+)')


        self.deviceCoordDict = OrderedDict();
        
        # Parse the data in each line and put it into a dict
        for ii, line in enumerate(dataStrip):
            if reg.match(line):
                matchRes = reg.findall(line)[0]
                devName = matchRes[5]
                if devName in self.deviceCoordDict:
                    uniqueDevName = devName+'_'+str(ii)
                    print('Warning: The device name %s is duplicated. Changing its name to %s.'%(devName,uniqueDevName))
                    devName = uniqueDevName
                self.deviceCoordDict[devName] = dict()
                self.deviceCoordDict[devName]['x'] = float(matchRes[0])
                self.deviceCoordDict[devName]['y'] = float(matchRes[1])
                self.deviceCoordDict[devName]['polarization'] = matchRes[2]
                self.deviceCoordDict[devName]['wavelength'] = matchRes[3]
                print(matchRes[3])
                self.deviceCoordDict[devName]['type'] = matchRes[4]
                print(matchRes[4])
                self.deviceCoordDict[devName]['comment'] = matchRes[5]
                print(matchRes[5])
                self.deviceCoordDict[devName]['id'] = ii
                self.deviceCoordDict[devName]['line'] = line
            else:
                print('Warning: The entry\n%s\nis not formatted correctly.' %line)
    
    def findCoordinateTransform(self, motorCoords, gdsCoords):
        """ Finds the best fit affine transform which maps the GDS coordinates to motor coordinates."""
        
        if len(motorCoords) != len(gdsCoords):
            raise CoordinateTransformException('You must have the same number of motor coordinates and GDS coordinates')
        
        if len(motorCoords) < 3:
            raise CoordinateTransformException('You must have at least 3 coordinate pairs.')
        
        numPairs = len(motorCoords)
    
        X = mat(zeros((2*numPairs,2*numPairs)))
        Xp = mat(zeros((2*numPairs,1)))
        
        for ii,motorCoord,gdsCoord in zip(range(numPairs),motorCoords,gdsCoords):
            X[2*ii,0:3] = mat([gdsCoord[0],gdsCoord[1],1])
            X[2*ii+1,3:6] = mat([gdsCoord[0],gdsCoord[1],1])
            Xp[2*ii:2*ii+2] = mat([[motorCoord[0]],[motorCoord[1]]])
        
        # Do least squares fitting
        a = linalg.lstsq(X,Xp)
        
        A = vstack((a[0][0:3].T,a[0][3:6].T,mat([0,0,1])))
        
        self.transformMatrix = A
        
        return A
        
    def gdsToMotorCoords(self, gdsCoords):
        """ Uses the calculated affine transform to map a GDS coordinate to a motor coordinate."""
        gdsCoordVec = mat([[gdsCoords[0]],[gdsCoords[1]],[1]])
        motorCoordVec = self.transformMatrix*gdsCoordVec
        motorCoords = (float(motorCoordVec[0]),float(motorCoordVec[1]))
        return motorCoords
        
    def beginMeasure(self, devices, abortFunction=None, updateFunction=None, updateGraph=True):
        """ Runs an automated measurement. For each device, it moves to the interpolated motor coordinates and does a sweep.
        The sweep results, and metadata associated with the sweep are stored in a data file which is saved to the folder specified
        in self.saveFolder. An optional abort function can be specified which is called to determine if the measurement process should
        be stopped. Also, an update function is called which can be used to update UI elements about the measurement progress."""
        for ii,d in enumerate(devices):
            gdsCoord = (self.deviceCoordDict[d]['x'],self.deviceCoordDict[d]['y'])
            motorCoord = self.gdsToMotorCoords(gdsCoord)
            self.motor.moveAbsoluteXY(motorCoord[0], motorCoord[1])
            self.fineAlign.doFineAlign()
            sweepWavelength, sweepPower = self.laser.sweep()
            if updateGraph:
                # Update the graph on the main window
                wx.CallAfter(self.laser.ctrlPanel.laserPanel.laserPanel.drawGraph, sweepWavelength*1e9, sweepPower)
            print('GDS: (%g,%g) Motor: (%g,%g)'%(gdsCoord[0],gdsCoord[1],motorCoord[0],motorCoord[1]))
            matFileName = os.path.join(self.saveFolder, d+'.mat')
            
            # Save sweep data and metadata to the mat file
            matDict = dict()
            matDict['scandata'] = dict()
            matDict['metadata'] = dict()
            matDict['scandata']['wavelength'] = sweepWavelength
            matDict['scandata']['power'] = sweepPower
            matDict['metadata']['device'] = d
            matDict['metadata']['gds_x_coord'] = self.deviceCoordDict[d]['x']
            matDict['metadata']['gds_y_coord'] = self.deviceCoordDict[d]['y']
            matDict['metadata']['motor_x_coord'] = motorCoord[0]
            matDict['metadata']['motor_y_coord'] = motorCoord[1]
            matDict['metadata']['measured_device_number'] = ii
            matDict['metadata']['coord_file_line'] = self.deviceCoordDict[d]['line']
            timeSeconds = time.time()
            matDict['metadata']['time_seconds'] = timeSeconds
            matDict['metadata']['time_str'] = time.ctime(timeSeconds)
            
            savemat(matFileName, matDict)
            
            pdfFileName = os.path.join(self.saveFolder, d+'.pdf')
            plt.figure()
            plt.plot(sweepWavelength*1e9, sweepPower)
            plt.xlabel('Wavelength (nm)')
            plt.ylabel('Power (dBm)')
            plt.savefig(pdfFileName)
            plt.close()
            
            if abortFunction != None and abortFunction():
                print('Aborted')
                return
            if updateFunction != None:
                updateFunction(ii)
        

class CoordinateTransformException(Exception):
    pass