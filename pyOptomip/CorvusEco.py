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

"""
Created on Mon Jun 02 10:01:33 2014

@author: Stephen Lin
Last updated: July 15, 2014
"""
#MAIN ISSUES
#The Corvus does not return any errors for many things:
#e.g.: If an axis is not connected but is enabled through the code, everything will still proceed
#however, NONE of any of the axis will move when given the commmand (making it impossible to tell you which axis is not working)
#Corvus will tell you there is an internal error, but it does not give ANY details.


import time

class CorvusEcoClass():
    NumberOfAxis = 3 #default the axis number @ 3 just in case.
    name = 'CorvusEco'
    isSMU=False
    isMotor=True
    isLaser=False
    def connect(self,visaName,rm,Velocity,Acceleration,NumberOfAxis):
        self.ser = rm.get_instrument(visaName) #Connects to device with pyVisa
        self.ser.baud_rate = 57600 # Sets baudrate
        self.ser.write('identify') #Asks for identification
        print((self.ser.read()+ ' [Model Name][Hardware Ver][Software Ver][Internal Use][Dip-Switch]'))
        print('Connected\n')
        
        #Sets minimum # of axis to send commands to
        try:
            self.ser.write('%d setdim'%(NumberOfAxis))
            if NumberOfAxis >= 1:
                self.ser.write('1 1 setaxis')
                print('Axis 1 Enabled.')
            if NumberOfAxis >= 2:
                self.ser.write('1 2 setaxis')
                print('Axis 2 Enabled.')
            else:
                self.ser.write('0 2 setaxis')
            if NumberOfAxis >= 3:
                self.ser.write('1 3 setaxis')
                print('Axis 3 Enabled.')
            else:
                self.ser.write('0 3 setaxis')
            self.NumberOfAxis = NumberOfAxis
        except:
            self.showErr()


        #Sets units to um (microns)
        self.ser.write('1 0 setunit') #Virtual Axis
        self.ser.write('1 1 setunit') #Axis 1
        self.ser.write('1 2 setunit') #Axis 2
        self.ser.write('1 3 setunit') #Axis 3
        print ('Units are set to: Microns(um)\n')
        

        #Set Acceleration Function
        self.ser.write('0 setaccelfunc') #Sets acceleration for long travel distances, probably dont need, 0 means no accel
        
        #Set output port
        self.ser.write('1 setout') #Sets digital output, 1 means Dout1 = on, Dout2=OFF, Dout3=OFF
        
        #set trigger out
        self.ser.write('10 0 1 ot')#Out Trigger: [time][polarity][output]
        #time in range of 1-1000 in ms (integer)
        #polarity in range of 0 or 1
        #output in range of 1, 2 or 3
        self.setcloop(1)
        
    def disconnect(self):
        self.ser.close()
        print ('Corvus Eco Disconnected')
        

    #Units: (Unit/s) use setunit command   
    def setVelocity(self,velocity):
        self.ser.write(str(velocity)+' sv') #set velocity
        self.ser.write('gv') #Get Velocity
        response = self.ser.read()
        print(('Velocity set to: '+response+' [units]/s\n'))
        
    #Units: (Unit/s^2) use setunit command            
    def setAcceleration(self,Acceleration):
        self.ser.write(str(Acceleration)+' sa') #Set Acceleration
        self.ser.write('ga')#Get Acceleration
        response = self.ser.read()
        print(('Acceleration set to: '+response+' [units]/s^2\n'))
    
    #Closed Loop ----------------------------
    def setcloop(self,toggle):
        #0 = off
        #1 = on
        try:
            self.ser.write('%d 1 setcloop' %(toggle))
            self.ser.write('%d 2 setcloop' %(toggle))
            self.ser.write('%d 3 setcloop' %(toggle))
            if toggle == 0:
                print ('Close Loop Disabled for All Axis.')
            if toggle == 1:
                print ('Close Loop Enabled for All Axis.')
        except:
            self.showErr()

    #set scale type
    def setscaletype(self,stype):
    #value of 0 or 1
    # 0 = Analog
    # 1 = digital
        try:
            self.ser.write('%d 1 setscaletype'%(stype))
            self.ser.write('%d 2 setscaletype'%(stype))
            self.ser.write('%d 3 setscaletype'%(stype))
            if stype == 0:
                print ('Scale Type set to Analog for All Axis')
            if stype == 1:
                print ('Scale Type set to Digital for All Axis')
        except:
            self.showErr()
                
    def setclperiod(self,direction,distance):
        #+ or - for direction
        #distance in microns, value from 0.0000001 to 1.999999
            
        microndistance = distance/1000
            
        try:
            self.ser.write('%s %d 1 setclperiod'%(direction,microndistance))
            self.ser.write('%s %d 2 setclperiod'%(direction,microndistance))
            self.ser.write('%s %d 3 setclperiod'%(direction,microndistance))
            print('Clperiod Set Successfully')
        except:
            self.showErr()
            
            
    def setnselpos(self,pos):
    #pos: 0 or 1
    # 0 returns the calculated position
    # 1 returns the measured position
            
        try:
            self.ser.write('%d 1 setnselpos'%(pos))
            self.ser.write('%d 2 setnselpos'%(pos))
            self.ser.write('%d 3 setnselpos'%(pos))
            print ('Complete')
            #NOTE: Try doing this with axis disabled and see if the function still works
            #should still work even if axis disabled.
        except:
            self.showErr()
            
    #sets the unit for all axis
    #0 = microstep
    #1 = micron
    #2 = millimeters
    #3 = centimeters
    #4 = meters
    #5 = inches
    #6 = mil (1/1000 inch)
    def setunit(self,unit):
        self.ser.write('%d 0 setunit'%(unit))
        self.ser.write('%d 1 setunit'%(unit))
        self.ser.write('%d 2 setunit'%(unit))
        self.ser.write('%d 3 setunit'%(unit))
        print ('Units set successfully.')
        
    #Checks the currently set units
    #0 = microstep
    #1 = micron
    #2 = millimeters
    #3 = centimeters
    #4 = meters
    #5 = inches
    #6 = mil (1/1000 inch)
    def getunit(self,axis):
        self.ser.write('%d getunit'%(axis))
        value = self.ser.read()
        print(('Axis %d is set to unitvalue: %s'%(axis,value)))
            
#=======Movement functions============
    def moveX(self,distance):
        if self.NumberOfAxis == 1:       
            try:
                self.ser.write(str(distance)+' r')
                #print ('Move Complete')
            except:
                print('An Error has occured')
                self.showErr()
                
        if self.NumberOfAxis == 2:
            try:
                self.ser.write(str(distance)+' 0 r')
                #print ('Move Complete')
            except:
                print('An Error has occured')
                self.showErr()
                
        if self.NumberOfAxis == 3:
            try:
                self.ser.write(str(distance)+' 0 0 r')
                #print ('Move Complete')
            except:
                print('An Error has occured')
                self.showErr()

    def moveY(self,distance):
        if self.NumberOfAxis == 1:       
            print ('Error: Axis 2 Not Enabled.')
                
        if self.NumberOfAxis == 2:
            try:
                self.ser.write('0 '+str(distance)+' r')
                #print ('Move Complete')
            except:
                print('An Error has occured')
                self.showErr()
                
        if self.NumberOfAxis == 3:
            try:
                self.ser.write('0 '+str(distance)+' 0 r')
                #print ('Move Complete')
            except:
                print('An Error has occured')
                self.showErr()
            
    def moveZ(self,distance):
        if self.NumberOfAxis == 1:       
            print ('Error: Axis 3 Not Enabled.')
                
        if self.NumberOfAxis == 2:
            print ('Error: Axis 3 Not Enabled.')
                
        if self.NumberOfAxis == 3:
            try:
                self.ser.write('0 0 '+str(distance)+' r')
                #print ('Move Complete')
            except:
                print('An Error has occured')
                self.showErr()
                
    #Moves all the axis together
    #can be used regardless of how many axis are enabled
    def moveRelative(self,x,y=0,z=0):
        if self.NumberOfAxis == 1:       
            try:
                self.ser.write('%.6f r'%(x))
                #print ('Move Complete')
            except:
                print('An Error has occured')
                self.showErr()
                
        if self.NumberOfAxis == 2:
            try:
                self.ser.write('%.6f %.6f r'%(x,y))
                #print ('Move Complete')
            except:
                print('An Error has occured')
                self.showErr()
                
        if self.NumberOfAxis == 3:
            try:
                self.ser.write('%.6f %.6f %.6f r'%(x,y,z))
                #print ('Move Complete')
            except:
                print('An Error has occured')
                self.showErr()
        self.waitMoveComplete()
        
        
    def moveAbsoluteXY(self,x,y):
        xCurrentPos = self.getPosition()[0];
        yCurrentPos = self.getPosition()[1];
        self.moveRelative(x-xCurrentPos, y-yCurrentPos)
    
    def waitMoveComplete(self):
        while int(self.ser.ask('st')) & 1:
            time.sleep(0.001)
                
    #Absolute MOve
    #Has a possible range of +/- 16383mm
    #units are the ones defined to the axis (should be microns)
    
    #From manual: The move profile is calculated in respect to the velocity/acceleration
    #setup and the given hard or software limits. The axes are linear interpolated, 
    #this causes the controller to start and stop all active axes simultaneously
#    def moveAbsolute(self,x,y=0,z=0):
#        if self.NumberOfAxis == 1:       
#            try:
#                self.ser.write('%d m'%(x))
#                print ('Move Complete')
#            except:
#                print('An Error has occured')
#                self.showErr()
#                
#        if self.NumberOfAxis == 2:
#            try:
#                self.ser.write('%d %d m'%(x,y))
#                print ('Move Complete')
#            except:
#                print('An Error has occured')
#                self.showErr()
#                
#        if self.NumberOfAxis == 3:
#            try:
#                self.ser.write('%d %d %d m'%(x,y,z))
#                print ('Move Complete')
#            except:
#                print('An Error has occured')
#                self.showErr()
                
    def getPosition(self):
        try:
            self.ser.write('pos')
            motorPosStr = self.ser.read()
            res = list(map(float, motorPosStr.strip().split()))
        except Exception as e:
            print(e)
            print(motorPosStr)
            print('An Error has occured')
            self.showErr()
        return res
                         
    def clear(self): #Should clear any lingering messages in the device
        try:
            self.ser.write('clear')#Clears the parameter stack, refer to page 287 in manual for more detail
        except:
            self.showErr()
            
    def reset(self):#Resets the whole device, equivalent of disconnecting the power according to the manual
    #a beep should be heard after the device is reset
        try:
            self.ser.write('reset')
        except:
            self.showErr()
        
    def showErr(self):
        self.ser.write('ge') #Returns error and clears the error stack, Errors are given as codes which are listen in them manual
        error = str('Error Code: '+self.ser.read()+' (Refer to Manual Page 165)')
        raise Exception(error)
               
        