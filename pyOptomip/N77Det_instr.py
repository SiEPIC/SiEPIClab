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

from ctypes import *
import numpy as np;
from itertools import repeat;
import hp816x_instr
import math;


class hp816x_N77Det(hp816x_instr.hp816x):
    name = 'hp816x N77 Detector'
    numPWMSlots = 5;    
    maxPWMPoints = 100000;
    isDetect = True

    
    def connect(self, visaAddr, n77DetAddr, reset = 0, forceTrans=1, autoErrorCheck=1):
        super(hp816x_N77Det, self).connect(visaAddr, reset, forceTrans, autoErrorCheck)
        
        self.hN77Det = c_int32();

        queryID = 1; # The instrument ignores this value.
        res = self.hp816x_init(n77DetAddr.encode('utf-8'), queryID, reset, byref(self.hN77Det));
        self.checkErrorN77(res);
        self.registerMainframe(self.hN77Det);
        self.N77SlotInfo = self.getN77SlotInfo(); # Keep mainframe slot info
        self.pwmSlotIndex,self.pwmSlotMap = self.enumerateN77PWMSlots();
        self.activeSlotIndex = self.pwmSlotIndex;
        return
        
    def disconnect(self):
        super(hp816x_N77Det, self).disconnect();
        self.unregisterMainframe(self.hN77Det);

        res = self.hp816x_close(self.hN77Det);
        self.checkErrorN77(res);
        
    def getN77SlotInfo(self):
        slotInfoArr = (c_int32*self.numPWMSlots)()
        slotInfoArrPtr = cast(slotInfoArr, POINTER(c_int32))
        res = self.hp816x_getSlotInformation_Q(self.hN77Det, self.numPWMSlots, slotInfoArrPtr)
        self.checkErrorN77(res);
        return slotInfoArrPtr[:self.numPWMSlots]
        
    def enumerateN77PWMSlots(self):
        pwmSlotIndex = list();
        pwmSlotMap = list();
        ii = 1;
        for slot in self.N77SlotInfo:
            if slot == self.hp816x_SINGLE_SENSOR:
                pwmSlotIndex.append(ii);
                pwmSlotMap.append((ii,0));
                ii += 1;
            elif slot == self.hp816x_DUAL_SENSOR:
                pwmSlotIndex.append(ii);
                pwmSlotMap.append((ii,0));
                ii += 1;
                pwmSlotIndex.append(ii);
                pwmSlotMap.append((ii,1));
                ii += 1;
        return (pwmSlotIndex,pwmSlotMap)
        
    def getNumSweepChannels(self):
        return len(self.pwmSlotIndex);
        
    def setRangeParams(self, chan, initialRange, rangeDecrement, reset=0):
        res = self.hp816x_setInitialRangeParams(self.hN77Det, chan, reset, initialRange, rangeDecrement);
        self.checkErrorN77(res);
        return;
    
            
    def setPWMPowerUnit(self, slot, chan, unit):
        res = self.hp816x_set_PWM_powerUnit(self.hN77Det, slot, chan, self.sweepUnitDict[unit]);
        self.checkErrorN77(res);    
          
    def setPWMPowerRange(self, slot, chan, rangeMode = 'auto', range=0):
        res = self.hp816x_set_PWM_powerRange(self.hN77Det, slot, chan, self.rangeModeDict[rangeMode], range);
        self.checkErrorN77(res);  
        
    def checkInstrumentErrorN77(self):
        """ Reads error messages from the instrument"""
        ERROR_MSG_BUFFER_SIZE = 256;
        instErr = c_int32();
        c_errMsg = (c_char*ERROR_MSG_BUFFER_SIZE)();
        c_errMsgPtr = cast(c_errMsg, c_char_p);
        self.hp816x_error_query(self.hN77Det, byref(instErr), c_errMsgPtr);
        return instErr.value,c_errMsg.value
    
    def checkErrorN77(self, errStatus):
        ERROR_MSG_BUFFER_SIZE = 256;
        if errStatus < self.hp816x_SUCCESS:
            if errStatus == self.hp816x_INSTR_ERROR_DETECTED:
                instErr,instErrMsg = self.checkInstrumentError()
                raise InstrumentError('Error '+str(instErr)+': '+instErrMsg);
            else:
                c_errMsg = (c_char*ERROR_MSG_BUFFER_SIZE)();
                c_errMsgPtr = cast(c_errMsg, c_char_p);    

                self.hp816x_error_message(self.hN77Det, errStatus, c_errMsgPtr);
                raise InstrumentError(c_errMsg.value);
        return 0;
    
    def getLambdaScanResult(self, chan, useClipping, clipLimit, numPts):
        wavelengthArr = np.zeros(int(numPts));
        powerArr = np.zeros(int(numPts));
        res = self.hp816x_getLambdaScanResult(self.hN77Det, chan,useClipping,clipLimit, powerArr,wavelengthArr)
        self.checkErrorN77(res);
        return wavelengthArr, powerArr;
    
    def readPWM(self, slot, chan):
        """ read a single wavelength """
        powerVal = c_double();
        res = self.hp816x_PWM_readValue(self.hN77Det, slot, chan, byref(powerVal));
        # Check for out of range error
        if res == self.hp816x_INSTR_ERROR_DETECTED:
            instErr,instErrMsg = self.checkInstrumentError()
            if instErr == -231 or instErr == -261:
                return self.sweepClipLimit # Assumes unit is in dB
            else:
                raise InstrumentError('Error '+str(instErr)+': '+instErrMsg);
        self.checkError(res);      
        return float(powerVal.value); 

    def sweep(self):
        """ Performs a wavelength sweep """
        
        # Convert values from string representation to integers for the driver
        unitNum = self.sweepUnitDict[self.sweepUnit];
        outputNum = self.laserOutputDict[self.sweepLaserOutput];
        numScans = self.sweepNumScansDict[self.sweepNumScans];
        numChan = len(self.pwmSlotIndex); 
        numActiveChan = len(self.activeSlotIndex) # Number of active channels
        
        # Total number of points in sweep
        numTotalPoints = int(round((self.sweepStopWvl-self.sweepStartWvl)/self.sweepStepWvl+1));
        
        # The laser reserves 100 pm of spectrum which takes away from the maximum number of datapoints per scan
        # Also, we will reserve another 100 datapoints as an extra buffer.
        #maxPWMPointsTrunc = int(round(self.maxPWMPoints-100e-12/self.sweepStepWvl-1));
        maxPWMPointsTrunc = int(round(self.maxPWMPoints-math.ceil(100e-12/self.sweepStepWvl)))-100;
        numFullScans = int(numTotalPoints//maxPWMPointsTrunc);
        numRemainingPts = numTotalPoints % maxPWMPointsTrunc;
        
        stitchNumber = numFullScans+1
        
        print('Total number of datapoints: %d'%numTotalPoints)
        print('Stitch number: %d'%stitchNumber)
        
        # Create a list of the number of points per stitch
        numPointsLst = list();

        for x in repeat(maxPWMPointsTrunc, numFullScans):
            numPointsLst.append(int(x));
            
        numPointsLst.append(int(round(numRemainingPts)));
        
        startWvlLst = list();
        stopWvlLst = list();
        
        # Create a list of the start and stop wavelengths per stitch
        pointsAccum = 0;
        for points in numPointsLst:
            startWvlLst.append(self.sweepStartWvl+pointsAccum*self.sweepStepWvl);
            stopWvlLst.append(self.sweepStartWvl+(pointsAccum+points-1)*self.sweepStepWvl);
            pointsAccum += points;

        
        # Set sweep speed
        self.setSweepSpeed(self.sweepSpeed); 
        
        
        wavelengthArrPWM = np.zeros(int(numTotalPoints));
        powerArrPWM = np.zeros((int(numTotalPoints), numActiveChan))
        
        pointsAccum = 0;
        # Loop over all the stitches
        for points,startWvl,stopWvl in zip(numPointsLst,startWvlLst,stopWvlLst):
            print('Sweeping from %g nm to %g nm'%(startWvl*1e9,stopWvl*1e9))
            # If the start or end wavelength is not a multiple of 1 pm, the laser will sometimes choose the wrong start
            # or end wavelength for doing the sweep. To fix this, we will set the sweep start wavelength to the 
            # nearest multiple of 1 pm below the start wavelength and the nearest multiple above the end wavelength.
            # After the sweep is completed, the desired wavelength range is extracted from the results.
            startWvlAdjusted = startWvl;
            stopWvlAdjusted = stopWvl;
            if startWvl*1e12-int(startWvl*1e12) > 0:
                startWvlAdjusted = math.floor(startWvl*1e12)/1e12;
            if stopWvl*1e12-int(stopWvl*1e12) > 0:
                stopWvlAdjusted = math.ceil(stopWvl*1e12)/1e12;
                
            # Format the start and dtop wvl to 13 digits of accuracy (otherwise the driver will sweep the wrong range)
            startWvlAdjusted = float('%.13f'%(startWvlAdjusted))
            stopWvlAdjusted = float('%.13f'%(stopWvlAdjusted))
        
            c_numPts = c_uint32();
            c_numChanRet = c_uint32();
            res = self.hp816x_prepareMfLambdaScan(self.hDriver, unitNum, self.sweepPower, outputNum, numScans, numChan, \
                                                  startWvlAdjusted, stopWvlAdjusted, self.sweepStepWvl, byref(c_numPts), byref(c_numChanRet));

            self.checkError(res);
            numPts = int(c_numPts.value);    
            
            
            # Set range params
            for ii in self.activeSlotIndex:
                self.setRangeParams(ii, self.sweepInitialRange, self.sweepRangeDecrement);
        
            # This value is unused since getLambdaScanResult returns the wavelength anyways
            c_wavelengthArr = (c_double*int(numPts))();
            c_wavelengthArrPtr = cast(c_wavelengthArr, POINTER(c_double));
            
            # Perform the sweep
            res = self.hp816x_executeMfLambdaScan(self.hDriver, c_wavelengthArrPtr)
            self.checkError(res);
            
            wavelengthArrTemp = np.zeros(int(numPts));
            for zeroIdx,chanIdx in enumerate(self.activeSlotIndex):
                # zeroIdx is the index starting from zero which is used to add the values to the power array
                # chanIdx is the channel index used by the mainframe
                # Get power values and wavelength values from the laser/detector
                wavelengthArrTemp, powerArrTemp = self.getLambdaScanResult(chanIdx, self.sweepUseClipping, self.sweepClipLimit, numPts) 
                # The driver sometimes doesn't return the correct starting wavelength for a sweep
                # We will search the returned wavelength results to see the index at which
                # the deired wavelength starts at, and take values starting from there
                wavelengthStartIdx = self.findClosestValIdx(wavelengthArrTemp, startWvl);
                wavelengthStopIdx = self.findClosestValIdx(wavelengthArrTemp, stopWvl);
                wavelengthArrTemp = wavelengthArrTemp[wavelengthStartIdx:wavelengthStopIdx+1]
                powerArrTemp = powerArrTemp[wavelengthStartIdx:wavelengthStopIdx+1]
                powerArrPWM[pointsAccum:pointsAccum+points,zeroIdx] = powerArrTemp; 
            wavelengthArrPWM[pointsAccum:pointsAccum+points] = wavelengthArrTemp;
            pointsAccum += points;                                

        return (wavelengthArrPWM,powerArrPWM)        
        
class InstrumentError(Exception):
    pass;
        