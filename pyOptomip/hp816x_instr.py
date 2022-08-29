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
import numpy.ctypeslib as npct;
from itertools import repeat;
import math;
import string


class hp816x(object):
    
    # Constants
    name = 'hp816x'
    isMotor=False
    isLaser=True
    # Slot info
    hp816x_UNDEF = 0;
    hp816x_SINGLE_SENSOR = 1;
    hp816x_DUAL_SENSOR = 2;
    hp816x_FIXED_SINGLE_SOURCE = 3;
    hp816x_FIXED_DUAL_SOURCE = 4;
    hp816x_TUNABLE_SOURCE = 5;
    hp816x_SUCCESS = 0;
    hp816x_ERROR = int('0x80000000', 16);
    hp816x_INSTR_ERROR_DETECTED = -1074000633; # 0xBFFC0D07
    
    maxPWMPoints = 20001;
    
    
    sweepStartWvl = 1530e-9;
    sweepStopWvl = 1570e-9;
    sweepStepWvl = 1e-9;
    sweepSpeed = '10nm';
    sweepUnit = 'dBm'
    sweepPower = 0;
    sweepLaserOutput = 'lowsse';
    sweepNumScans = 3;
    sweepPWMChannel = 'all';
    sweepInitialRange = -20;
    sweepRangeDecrement = 20;
    sweepUseClipping = 1;
    sweepClipLimit = -100;
    

    rangeModeDict = dict([('auto',1), ('manual',0)]);
    sweepSpeedDict = dict([('80nm',-1), ('40nm',0), ('20nm',1), ('10nm',2), ('5nm',3), ('0.5nm',4), ('auto',5)]);
    laserOutputDict = dict([('highpower',0), ('lowsse',1)]);
    laserStateDict = dict([('off',0), ('on',1)]);
    sweepUnitDict = dict([('dBm',0), ('W',1)]);
    sweepNumScansDict = dict([(1,0), (2,1), (3,2)]);
    laserSelModeDict = dict([('min',0), ('default',1), ('max',2), ('manual',3)]);
    mainframePortDict = dict([('8163',3), ('8164',5), ('none',1)]);
    
    
    def __init__(self, libLocation='hp816x_64.dll'):
        """ Initializes the driver.
        libLocation -- Location of hp816x_32.dll library. It will search the system's PATH variable by default.
        """
        
        self.hLib = WinDLL('hp816x_64.dll');
        self.createPrototypes();
        self.connected = False
        
    def __del__(self):
        if self.connected:
            self.disconnect()

    def connect(self, visaAddr, reset = 0, forceTrans=1, autoErrorCheck=1):
        """ Connects to the instrument.
        visaAddr -- VISA instrument address e.g. GPIB0::20::INSTR
        reset -- Reset instrument after connecting
        """
        if self.connected:
            print('Already connected to the laser. Aborting connection.')
            return
        self.hDriver = c_int32(); # Handle to the driver.
        queryID = 1; # The instrument ignores this value.
        res = self.hp816x_init(visaAddr.encode('utf-8'), queryID, reset, byref(self.hDriver));
        self.checkError(res);
        # Set force transaction mode
        self.setForceTransaction(forceTrans);
        # Set error checking mode
        self.setErrorCheckMode(autoErrorCheck);
        
        # Get the mainframe type
        deviceIdnStr = self.gpibQueryString('*IDN?'.encode('utf-8'))
        deviceIdnStr = deviceIdnStr.strip().decode('utf-8').split(',')
        print('The mainframe is: %s'%deviceIdnStr[1])
        
        if '8164' in deviceIdnStr[1]:
            mainframeType = '8164'
        elif '8163' in deviceIdnStr[1]:
            mainframeType = '8163'
        else:
            mainframeType = 'none'

        

        self.numSlots = self.mainframePortDict[mainframeType];        
        # Get the slot info
        self.slotInfo = self.getSlotInfo();
        self.pwmSlotIndex,self.pwmSlotMap = self.enumeratePWMSlots();
        self.activeSlotIndex = self.pwmSlotIndex;
        # Register the mainframe so it can do sweeps
        self.registerMainframe(self.hDriver);
        print('Connected to the laser')
        self.connected = True
    
        
    def setForceTransaction(self, force):
        """ When force is true, always send commands to the instrument, even if the commands
            do not change the instrument's state. If false, only send commands which would change
            the instrument's state.
        """
        res = self.hp816x_forceTransaction(self.hDriver, force);
        self.checkError(res);
        return;
        
    def setErrorCheckMode(self, check):
        """ When check is true, enables auto error checking. When false, disables error
            checking which could make the driver execute faster
        """
        res = self.hp816x_errorQueryDetect(self.hDriver, check);
        self.checkError(res);
        return;
        
    def getSlotInfo(self):
        slotInfoArr = (c_int32*self.numSlots)()
        slotInfoArrPtr = cast(slotInfoArr, POINTER(c_int32))
        res = self.hp816x_getSlotInformation_Q(self.hDriver, self.numSlots, slotInfoArrPtr)
        self.checkError(res);
        return slotInfoArrPtr[:self.numSlots]
        
    def enumeratePWMSlots(self):
        """ Returns two lists:
            pwmSlotIndex - List containing index for each detector
            pwmSlotMap - List of tuples containing the index and detector number for each detector
        """
        pwmSlotIndex = list();
        pwmSlotMap = list();
        slotIndex = 0; # Slot index
        enumeratedIndex = 0 # PWM index starting from zero
        for slot in self.slotInfo:
            if slot == self.hp816x_SINGLE_SENSOR:
                pwmSlotIndex.append(enumeratedIndex);
                pwmSlotMap.append((slotIndex,0));
                #slotIndex += 1;
                enumeratedIndex += 1
            elif slot == self.hp816x_DUAL_SENSOR:
                pwmSlotIndex.append(enumeratedIndex);
                pwmSlotMap.append((slotIndex,0));
                #slotIndex += 1;
                enumeratedIndex += 1
                pwmSlotIndex.append(enumeratedIndex);
                pwmSlotMap.append((slotIndex,1));
                #slotIndex += 1;
                enumeratedIndex += 1
            slotIndex += 1
        return (pwmSlotIndex,pwmSlotMap)
                                    
    
    def registerMainframe(self, handle):
        """ Registers a mainframe so it can participate in a sweep """
        res = self.hp816x_registerMainframe(handle);
        self.checkError(res);
        return;
        
    def unregisterMainframe(self, handle):
        res = self.hp816x_unregisterMainframe(handle);
        self.checkError(res);
        return;
        
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
    
    def getLambdaScanResult(self, chan, useClipping, clipLimit, numPts):
        """ Gets the optical power results from a sweep. """
        wavelengthArr = np.zeros(int(numPts));
        powerArr = np.zeros(int(numPts));
        res = self.hp816x_getLambdaScanResult(self.hDriver, chan,useClipping,clipLimit, powerArr,wavelengthArr)
        self.checkError(res);
        return wavelengthArr, powerArr;

    def disconnect(self):
        self.unregisterMainframe(self.hDriver);
        res = self.hp816x_close(self.hDriver);
        self.checkError(res);
        self.connected = False
        print('Disconnected from the laser')
        
        
    def getNumPWMChannels(self):
        """ Returns the number of registered PWM channels """
        
        # The driver function to do this doesn't seem to work... It always returns zero
        #numChan = c_uint32();
        #res = self.hp816x_getNoOfRegPWMChannels_Q(self.hDriver, byref(numChan));
        numPWMChan = 0;
        for slot in self.slotInfo:
            if slot == self.hp816x_SINGLE_SENSOR:
                numPWMChan += 1;
            elif slot == self.hp816x_DUAL_SENSOR:
                numPWMChan += 2;
        
        return numPWMChan;
        
        
    def getNumSweepChannels(self):
        return len(self.pwmSlotIndex);
        
    def setRangeParams(self, chan, initialRange, rangeDecrement, reset=0):
        res = self.hp816x_setInitialRangeParams(self.hDriver, chan, reset, initialRange, rangeDecrement);
        self.checkError(res);
        return;
        
    def setAutorangeAll(self):
        """ Turns on autorange for all detectors and sets units to dBm """
        for slotinfo in self.pwmSlotMap:
            detslot = slotinfo[0];
            detchan = slotinfo[1]
            
            self.setPWMPowerUnit(detslot, detchan, 'dBm')
            self.setPWMPowerRange(detslot, detchan, rangeMode='auto')
        
    def checkError(self, errStatus):
        ERROR_MSG_BUFFER_SIZE = 256;
        if errStatus < self.hp816x_SUCCESS:
            if errStatus == self.hp816x_INSTR_ERROR_DETECTED:
                instErr,instErrMsg = self.checkInstrumentError()
                raise InstrumentError('Error '+str(instErr)+': '+instErrMsg);
            else:
                c_errMsg = (c_char*ERROR_MSG_BUFFER_SIZE)();
                c_errMsgPtr = cast(c_errMsg, c_char_p);    

                self.hp816x_error_message(self.hDriver, errStatus, c_errMsgPtr);
                raise InstrumentError(c_errMsg.value);
        return 0;
        
    def checkInstrumentError(self):
        """ Reads error messages from the instrument"""
        ERROR_MSG_BUFFER_SIZE = 256;
        instErr = c_int32();
        c_errMsg = (c_wchar*ERROR_MSG_BUFFER_SIZE)();
        c_errMsgPtr = cast(c_errMsg, c_char_p);
        self.hp816x_error_query(self.hDriver, byref(instErr), c_errMsgPtr);
        return instErr.value,c_errMsg.value
        
    def setSweepSpeed(self, speed):
        speedNum = self.sweepSpeedDict[speed];
        res = self.hp816x_setSweepSpeed(self.hDriver, speedNum);
        self.checkError(res);
        return;
        
    def readPWM(self, slot, chan):
        """ read a single wavelength """
        powerVal = c_double();
        res = self.hp816x_PWM_readValue(self.hDriver, slot, chan, byref(powerVal));
        # Check for out of range error
        if res == self.hp816x_INSTR_ERROR_DETECTED:
            instErr,instErrMsg = self.checkInstrumentError()
            if instErr == -231 or instErr == -261:
                return self.sweepClipLimit # Assumes unit is in dB
            else:
                raise InstrumentError('Error '+str(instErr)+': '+instErrMsg);
        self.checkError(res);      
        return float(powerVal.value);      
        
    def setPWMAveragingTime(self, slot, chan, avgTime):
        res = self.hp816x_set_PWM_averagingTime(self.hDriver, slot, chan, avgTime);
        self.checkError(res);
        
    def getAutoTLSSlot(self):
        """ Returns the slot number of the first found tunable laser source in the mainframe """
        for slot in self.slotInfo:
            if slot == self.hp816x_TUNABLE_SOURCE:
                return self.slotInfo.index(slot)
        raise Exception('Error: No tunable laser source found.')
        
    def findTLSSlots(self):
        """ Returns a list of all tunable lasers in the mainframe """
        tlsSlotList = []
        for ii,slot in enumerate(self.slotInfo):
            if slot == self.hp816x_TUNABLE_SOURCE:
                tlsSlotList.append(ii)
        if tlsSlotList == []:
            raise Exception('Error: No tunable laser source found.')
        return tlsSlotList
        
    def setTLSOutput(self, output, slot='auto'):
        if slot == 'auto':
            slot = self.getAutoTLSSlot();
            
        res = self.hp816x_set_TLS_opticalOutput(self.hDriver, int(slot), self.laserOutputDict[output]);
        self.checkError(res);    
        
    def setPWMPowerUnit(self, slot, chan, unit):
        res = self.hp816x_set_PWM_powerUnit(self.hDriver, slot, chan, self.sweepUnitDict[unit]);
        self.checkError(res);    
          
    def setPWMPowerRange(self, slot, chan, rangeMode = 'auto', range=0):
        res = self.hp816x_set_PWM_powerRange(self.hDriver, slot, chan, self.rangeModeDict[rangeMode], range);
        self.checkError(res);  
        
        
    def setTLSState(self, state, slot='auto'):
        """ turn on or off"""
        if slot == 'auto':
            slot = self.getAutoTLSSlot();
            
        res = self.hp816x_set_TLS_laserState(self.hDriver, int(slot), self.laserStateDict[state]);
        self.checkError(res);  
        
    def setTLSWavelength(self, wavelength, selMode='manual', slot='auto'):
        if slot == 'auto':
            slot = self.getAutoTLSSlot();
        
        res = self.hp816x_set_TLS_wavelength(self.hDriver, int(slot), self.laserSelModeDict[selMode], wavelength);
        self.checkError(res);
        
    def setTLSPower(self, power, slot='auto', selMode='manual', unit='dBm'):
        if slot == 'auto':
            slot = self.getAutoTLSSlot();
        
        res = self.hp816x_set_TLS_power(self.hDriver, int(slot), self.sweepUnitDict[unit], self.laserSelModeDict[selMode],\
              power);
        self.checkError(res);
        
    def sendGpibCmd(self, cmd):
        """ Sends a GPIB command to the mainframe
            cmd -- Command to send to the device """
        self.hp816x_cmd(self.hDriver, cmd);
        
    def gpibQueryString(self, cmd):
        """ Sends a GPIB command to the mainframe and reads a string result"""
        MSG_BUFFER_SIZE = 256;
        c_Msg = (c_char*MSG_BUFFER_SIZE)();
        c_MsgPtr = cast(c_Msg, c_char_p);
        res = self.hp816x_cmdString_Q(self.hDriver, cmd, MSG_BUFFER_SIZE, c_MsgPtr)
        self.checkError(res);
        return c_MsgPtr.value
        
    def getSlotInstruments(self):
        """ Gets the name of each instrument in the slots """
        instStr = self.gpibQueryString('*OPT?')
        return list(map(string.strip,instStr[:-1].split(',')))
        
    def findClosestValIdx(self, array, value):
        idx = (abs(array-value)).argmin()
        return idx 
        
    def sweepReturnEquidistantData(self, value):
        """ Specifies whether or not a laser sweep returns equidistant wavelength values
            Default is on. This may need to be disbled on some lasers when the step size is
            very small"""
        res = self.hp816x_returnEquidistantData(self.hDriver, value)  
        return res
    
    def createPrototypes(self):
        """ Creates function prototypes for the C function calls to the driver library """

        #         Completion and Error Codes
        #  
        # VI_SUCCESS    A long equal to zero
        # VI_ERROR      A long equal to hex 0x80000000
        #  
        #  
        #  
        # Other VISA Definitions
        #  
        # The size of the following three symbols is operating system dependent and is equal to the default integer size.
        #  
        #  
        # VI_NULL       An integer equal to 0
        #  
        # VI_TRUE       An integer equal to 1
        # VI_FALSE      An integer equal to 0
        #  
        #  
        # Variable types
        #  
        #  
        # ViUInt32      A 32-bit unsigned integer
        # ViPUInt32     A pointer to a 32-bit unsigned integer
        # ViAUInt32     An array of 32-bit unsigned integers
        #  
        # ViInt32       A 32-bit signed integer
        # ViPInt32      A pointer to a 32-bit signed integer
        # ViAInt32      An array of 32-bit signed integers
        #  
        # ViUInt16      A 16-bit unsigned integer
        # ViPUInt16     A pointer to a 16-bit unsigned integer
        # ViAUInt16     An array of 16-bit unsigned integers
        #  
        # ViInt16       A 16-bit signed integer
        # ViPInt16      A pointer to a 16-bit signed integer
        #  
        # ViAInt16      An array of 16-bit signed integers
        #  
        # ViUInt8       A unsigned byte
        # ViPUInt8      A pointer to an unsigned byte
        # ViAUInt8      An arrays of unsigned bytes
        #  
        # ViInt8        A 8-bit signed integer
        # ViPInt8       A pointer to a 8-bit signed integer
        # ViAInt8       An array of 8-bit signed 
        #  
        # ViChar        A character
        # ViPChar       A pointer to a character
        # ViAChar       An array of characters
        #  
        # ViByte        A byte
        # ViPByte       A pointer to a byte
        # ViAByte       An array of bytes
        #  
        # ViAddr        A Void pointer
        # ViPAddr       A pointer to a void pointer
        #  
        # ViAAddr       An array of void pointers
        #  
        # ViReal32      A 32-bit floating point
        # ViPReal32     A pointer to a 32-bit floating point
        # ViAReal32     An array of 32-bit floating points
        #  
        # ViReal64      A 64-bit floating point
        # ViPReal64     A pointer a 64-bit floating point
        #  
        # ViAReal64     A pointer to an array of 64-bit floating points
        #  
        # ViBuf A pointer to an array of bytes
        # ViPBuf        A pointer to an array of bytes
        # ViABuf        An array of byte pointers
        #  
        # ViString      An array of characters
        # ViPString     A pointer to an array of characters
        #  
        # ViAString     An array of ViStrings
        #  
        # ViRsrc        A ViString
        # ViPRsrc       A pointer to a ViString
        # ViARsrc       An array of ViStrings
        #  
        # ViBoolean     A 16-bit unsigned boolean value
        # ViPBoolean    A pointer to a 16-bit unsigned boolean
        #  
        # ViABoolean    An array of 16-bit unsigned booleans
        #  
        # ViStatus      A 32-bit integer status value
        # ViPStatus     A pointer to a 32-bit integer status value
        # ViAStatus     An array of 32-bit integer status values
        #  
        # ViVersion     A 32-bit unsigned integer version number
        # ViPVersion	A pointer to a 32-bit unsigned integer version number
        #  
        # ViAVersion	An array of 32-bit unsigned integer version numbers
        #  
        # ViObject	A 32-bit unsigned integer object
        # ViPObject	A pointer to a 32-bit unsigned integer object
        #  
        # ViAObject	An array of 32-bit unsigned objects
        #  
        # ViSession	A 32-bit unsigned integer object
        # ViPSession	A pointer to a 32-bit unsigned integer object
        # ViASession	An array of 32-bit unsigned objects

        array_1d_double = npct.ndpointer(dtype=np.double, ndim=1, flags='CONTIGUOUS')

        # Function prototype definitions

        # ViStatus _VI_FUNC hp816x_init(ViRsrc resourceName, ViBoolean IDQuery, ViBoolean reset, ViPSession ihandle);
        self.hp816x_init = self.hLib.hp816x_init;
        self.hp816x_init.argtypes = [c_char_p, c_uint16, c_uint16, POINTER(c_int32)];
        self.hp816x_init.restype = c_int32;
        
        # ViStatus _VI_FUNC hp816x_close(ViSession ihandle);
        self.hp816x_close = self.hLib.hp816x_close;
        self.hp816x_close.argtypes = [c_int32];
        self.hp816x_close.restype = c_int32;
        
        # ViStatus _VI_FUNC hp816x_set_TLS_parameters(ViSession ihandle, ViInt32 TLSSlot, ViInt32 powerUnit, ViInt32 opticalOutput, ViBoolean turnLaser, ViReal64 power, ViReal64 attenuation, ViReal64 wavelength);
        self.hp816x_set_TLS_parameters = self.hLib.hp816x_set_TLS_parameters;
        self.hp816x_set_TLS_parameters.argtypes = [c_int32, c_int32, c_int32, c_int32, c_uint16, c_double, c_double, c_double];
        self.hp816x_set_TLS_parameters.restype = c_int32;

        # ViStatus _VI_FUNC hp816x_registerMainframe(ViSession ihandle);
        self.hp816x_registerMainframe = self.hLib.hp816x_registerMainframe;
        self.hp816x_registerMainframe.argtypes = [c_int32]
        self.hp816x_registerMainframe.restype = c_int32;

        # ViStatus _VI_FUNC hp816x_prepareMfLambdaScan(ViSession ihandle, ViInt32 powerUnit, ViReal64 power, ViInt32 opticalOutput, ViInt32 numberofScans, ViInt32 PWMChannels, ViReal64 startWavelength, ViReal64 stopWavelength, ViReal64 stepSize, ViUInt32 numberofDatapoints, ViUInt32 numberofChannels);
        self.hp816x_prepareMfLambdaScan = self.hLib.hp816x_prepareMfLambdaScan;
        self.hp816x_prepareMfLambdaScan.argtypes = [c_int32, c_int32, c_double, c_int32, c_int32, c_int32, c_double, c_double, c_double, POINTER(c_uint32), POINTER(c_uint32)]
        self.hp816x_prepareMfLambdaScan.restype = c_int32;

        # ViStatus _VI_FUNC hp816x_executeMfLambdaScan(ViSession ihandle, ViReal64wavelengthArray[]);
        self.hp816x_executeMfLambdaScan = self.hLib.hp816x_executeMfLambdaScan;
        self.hp816x_executeMfLambdaScan.argtypes = [c_int32, POINTER(c_double)]
        self.hp816x_executeMfLambdaScan.restype = c_int32;

        # ViStatus _VI_FUNC hp816x_setSweepSpeed(ViSession ihandle, ViInt32 Sweep_Speed);
        self.hp816x_setSweepSpeed = self.hLib.hp816x_setSweepSpeed;
        self.hp816x_setSweepSpeed.argtypes = [c_int32, c_int32]
        self.hp816x_setSweepSpeed.restype = c_int32;

        # ViStatus _VI_FUNC hp816x_getLambdaScanResult(ViSession ihandle, ViInt32 PWMChannel, ViBoolean cliptoLimit, ViReal64 clippingLimit, ViReal64powerArray[], ViReal64lambdaArray[]);
        self.hp816x_getLambdaScanResult = self.hLib.hp816x_getLambdaScanResult;
        self.hp816x_getLambdaScanResult.argtypes = [c_int32, c_int32, c_uint16, c_double, array_1d_double, array_1d_double]
        self.hp816x_getLambdaScanResult.restype = c_int32;

        # ViStatus _VI_FUNC hp816x_forceTransaction(ViSession ihandle, ViBoolean forceTransaction);
        self.hp816x_forceTransaction = self.hLib.hp816x_forceTransaction;
        self.hp816x_forceTransaction.argtypes = [c_int32, c_uint16]
        self.hp816x_forceTransaction.restype = c_int32;

        # ViStatus _VI_FUNC hp816x_errorQueryDetect(ViSession ihandle, ViBoolean automaticErrorDetection);
        self.hp816x_errorQueryDetect = self.hLib.hp816x_errorQueryDetect;
        self.hp816x_errorQueryDetect.argtypes = [c_int32, c_uint16]
        self.hp816x_errorQueryDetect.restype = c_int32;

        # ViStatus _VI_FUNC hp816x_error_query(ViSession ihandle, ViPInt32 instrumentErrorCode, ViChar errorMessage[]);
        self.hp816x_error_query = self.hLib.hp816x_error_query;
        self.hp816x_error_query.argtypes = [c_int32, POINTER(c_int32), c_char_p]
        self.hp816x_error_query.restype = c_int32;

        # ViStatus _VI_FUNC hp816x_error_message(ViSession ihandle, ViStatus errorCode, ViString errorMessage);
        self.hp816x_error_message = self.hLib.hp816x_error_message;
        self.hp816x_error_message.argtypes = [c_int32, c_int32, c_char_p]
        self.hp816x_error_message.restype = c_int32;

        # ViStatus _VI_FUNC hp816x_set_PWM_parameters(ViSession ihandle, ViInt32 PWMSlot, ViInt32 channelNumber, ViBoolean rangeMode, ViBoolean powerUnit, ViBoolean internalTrigger, ViReal64 wavelength, ViReal64 averagingTime, ViReal64 powerRange);
        self.hp816x_set_PWM_parameters = self.hLib.hp816x_set_PWM_parameters;
        self.hp816x_set_PWM_parameters.argtypes = [c_int32, c_int32, c_int32, c_uint16, c_uint16, c_uint16, c_double, c_double, c_double]
        self.hp816x_set_PWM_parameters.restype = c_int32;

        # ViStatus _VI_FUNC hp816x_set_PWM_averagingTime(ViSession ihandle, ViInt32 PWMSlot, ViInt32 channelNumber, ViReal64 averagingTime);
        self.hp816x_set_PWM_averagingTime = self.hLib.hp816x_set_PWM_averagingTime;
        self.hp816x_set_PWM_averagingTime.argtypes = [c_int32, c_int32, c_int32, c_double]
        self.hp816x_set_PWM_averagingTime.restype = c_int32;

        # ViStatus _VI_FUNC hp816x_set_PWM_wavelength(ViSession ihandle, ViInt32 PWMSlot, ViInt32 channelNumber, ViReal64 wavelength);
        self.hp816x_set_PWM_wavelength = self.hLib.hp816x_set_PWM_wavelength;
        self.hp816x_set_PWM_wavelength.argtypes = [c_int32, c_int32, c_int32, c_double]
        self.hp816x_set_PWM_wavelength.restype = c_int32;

        # ViStatus _VI_FUNC hp816x_set_PWM_powerRange(ViSession ihandle, ViInt32 PWMSlot, ViInt32 channelNumber, ViBoolean rangeMode, ViReal64 powerRange);
        self.hp816x_set_PWM_powerRange = self.hLib.hp816x_set_PWM_powerRange;
        self.hp816x_set_PWM_powerRange.argtypes = [c_int32, c_int32, c_int32, c_uint16, c_double]
        self.hp816x_set_PWM_powerRange.restype = c_int32;

        # ViStatus _VI_FUNC hp816x_set_PWM_powerUnit(ViSession ihandle, ViInt32 PWMSlot, ViInt32 channelNumber, ViInt32 powerUnit);
        self.hp816x_set_PWM_powerUnit = self.hLib.hp816x_set_PWM_powerUnit;
        self.hp816x_set_PWM_powerUnit.argtypes = [c_int32, c_int32, c_int32, c_int32]
        self.hp816x_set_PWM_powerUnit.restype = c_int32;

        # ViStatus _VI_FUNC hp816x_PWM_readValue(ViSession ihandle, ViInt32 PWMSlot, ViUInt32 channelNumber, ViPReal64 measuredValue);
        self.hp816x_PWM_readValue = self.hLib.hp816x_PWM_readValue;
        self.hp816x_PWM_readValue.argtypes = [c_int32, c_int32, c_uint32, POINTER(c_double)]
        self.hp816x_PWM_readValue.restype = c_int32;

        # ViStatus _VI_FUNC hp816x_set_TLS_opticalOutput(ViSession ihandle, ViInt32 TLSSlot, ViInt32 setOpticalOutput);
        self.hp816x_set_TLS_opticalOutput = self.hLib.hp816x_set_TLS_opticalOutput;
        self.hp816x_set_TLS_opticalOutput.argtypes = [c_int32, c_int32, c_int32]
        self.hp816x_set_TLS_opticalOutput.restype = c_int32;
        
        # ViStatus _VI_FUNC hp816x_getSlotInformation_Q(ViSession ihandle, ViInt32 arraySize, ViInt32 slotInformation[]);
        self.hp816x_getSlotInformation_Q = self.hLib.hp816x_getSlotInformation_Q;
        self.hp816x_getSlotInformation_Q.argtypes = [c_int32, c_int32, POINTER(c_int32)]
        self.hp816x_getSlotInformation_Q.restype = c_int32;

        # ViStatus _VI_FUNC hp816x_getNoOfRegPWMChannels_Q(ViSession ihandle, ViUInt32 numberofPWMChannels);
        self.hp816x_getNoOfRegPWMChannels_Q = self.hLib.hp816x_getNoOfRegPWMChannels_Q;
        self.hp816x_getNoOfRegPWMChannels_Q.argtypes = [c_int32, POINTER(c_uint32)]
        self.hp816x_getNoOfRegPWMChannels_Q.restype = c_int32;
        
        # ViStatus _VI_FUNC hp816x_setInitialRangeParams(ViSession ihandle, ViInt32 PWMChannel, ViBoolean resettoDefault, ViReal64 initialRange, ViReal64 rangeDecrement);
        self.hp816x_setInitialRangeParams = self.hLib.hp816x_setInitialRangeParams;
        self.hp816x_setInitialRangeParams.argtypes = [c_int32, c_int32, c_uint16, c_double, c_double]
        self.hp816x_setInitialRangeParams.restype = c_int32;
        
        
        self.hp816x_unregisterMainframe = self.hLib.hp816x_unregisterMainframe;
        self.hp816x_unregisterMainframe.argtypes = [c_int32]
        self.hp816x_unregisterMainframe.restype = c_int32;
        
        # ViStatus _VI_FUNC hp816x_set_TLS_laserState(ViSession ihandle, ViInt32 TLSSlot, ViBoolean laserState);
        self.hp816x_set_TLS_laserState = self.hLib.hp816x_set_TLS_laserState;
        self.hp816x_set_TLS_laserState.argtypes = [c_int32, c_int32, c_uint16]
        self.hp816x_set_TLS_laserState.restype = c_int32;
        
        # ViStatus _VI_FUNC hp816x_set_TLS_wavelength(ViSession ihandle, ViInt32 TLSSlot, ViInt32 wavelengthSelection, ViReal64 wavelength);
        self.hp816x_set_TLS_wavelength = self.hLib.hp816x_set_TLS_wavelength;
        self.hp816x_set_TLS_wavelength.argtypes = [c_int32, c_int32, c_int32, c_double]
        self.hp816x_set_TLS_wavelength.restype = c_int32;
        
        # ViStatus _VI_FUNC hp816x_set_TLS_power(ViSession ihandle, ViInt32 TLSSlot, ViInt32 unit, ViInt32 powerSelection, ViReal64 manualPower);
        self.hp816x_set_TLS_power = self.hLib.hp816x_set_TLS_power;
        self.hp816x_set_TLS_power.argtypes = [c_int32, c_int32, c_int32, c_int32, c_double]
        self.hp816x_set_TLS_power.restype = c_int32;
        
        # ViStatus _VI_FUNC hp816x_cmd(ViSession ihandle, ViCharcommandString[]);
        self.hp816x_cmd = self.hLib.hp816x_cmd;
        self.hp816x_cmd.argtypes = [c_int32, c_char_p]
        self.hp816x_cmd.restype = c_int32;
        
        self.hp816x_cmdString_Q = self.hLib.hp816x_cmdString_Q
        self.hp816x_cmdString_Q.argtypes = [c_int32, c_char_p, c_int32, c_char_p]
        self.hp816x_cmdString_Q.restype = c_int32
        
        # ViStatus _VI_FUNC hp816x_returnEquidistantData(ViSession ihandle, ViBoolean equallySpacedDatapoints);
        self.hp816x_returnEquidistantData = self.hLib.hp816x_returnEquidistantData
        self.hp816x_returnEquidistantData.argtypes = [c_int32, c_uint16]
        self.hp816x_returnEquidistantData.restype = c_int32
        

        
class InstrumentError(Exception):
    pass;
        
    
