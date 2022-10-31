def connect():
    print("Connected to dummy Corvus.")


class dummyCorvus:
    NumberOfAxis = 3  # default the axis number @ 3 just in case.
    name = 'Dummy CorvusEco'
    isSMU = False
    isMotor = True
    isOpt = True
    isElec = False
    isLaser = False
    isQontrol = False
    isDetect = False

    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        connect()

    def disconnect(self):
        print('Dummy Corvus Eco Disconnected')

    # Units: (Unit/s) use setunit command
    def setVelocity(self, velocity):
        print(('Velocity set to: ' + velocity + ' [units]/s\n'))

    # Units: (Unit/s^2) use setunit command
    def setAcceleration(self, Acceleration):
        print(('Acceleration set to: ' + Acceleration + ' [units]/s^2\n'))

    # Closed Loop ----------------------------
    def setcloop(self, toggle):
        # 0 = off
        # 1 = on
        try:
            if toggle == 0:
                print('Close Loop Disabled for All Axis.')
            if toggle == 1:
                print('Close Loop Enabled for All Axis.')
        except:
            self.showErr()

    # set scale type
    def setscaletype(self, stype):
        # value of 0 or 1
        # 0 = Analog
        # 1 = digital
        try:
            if stype == 0:
                print('Scale Type set to Analog for All Axis')
            if stype == 1:
                print('Scale Type set to Digital for All Axis')
        except:
            self.showErr()

    def setclperiod(self, direction, distance):
        # + or - for direction
        # distance in microns, value from 0.0000001 to 1.999999

        microndistance = distance / 1000

        try:
            print('Clperiod Set Successfully')
        except:
            self.showErr()

    def setnselpos(self, pos):
        # pos: 0 or 1
        # 0 returns the calculated position
        # 1 returns the measured position

        try:
            print('Complete')
            # NOTE: Try doing this with axis disabled and see if the function still works
            # should still work even if axis disabled.
        except:
            self.showErr()

    # sets the unit for all axis
    # 0 = microstep
    # 1 = micron
    # 2 = millimeters
    # 3 = centimeters
    # 4 = meters
    # 5 = inches
    # 6 = mil (1/1000 inch)
    def setunit(self, unit):
        print('Units set successfully.')

    # Checks the currently set units
    # 0 = microstep
    # 1 = micron
    # 2 = millimeters
    # 3 = centimeters
    # 4 = meters
    # 5 = inches
    # 6 = mil (1/1000 inch)
    def getunit(self, axis):

        print(('Axis %d is set to unitvalue: ' % (axis)))

    # =======Movement functions============
    def moveX(self, distance):
        if self.NumberOfAxis == 3:
            try:
                print('Moved x axis by %d' % distance)
                self.x += distance
            except:
                print('An Error has occured')
                self.showErr()

    def moveY(self, distance):

        if self.NumberOfAxis == 3:
            try:
                print('Moved y axis by %d' % distance)
                self.y += distance
            except:
                print('An Error has occured')
                self.showErr()

    def moveZ(self, distance):
        if self.NumberOfAxis == 3:
            try:
                print('Moved z axis by %d' % distance)
                self.z += distance
            except:
                print('An Error has occured')
                self.showErr()

    # Moves all the axis together
    # can be used regardless of how many axis are enabled
    def moveRelative(self, x, y=0, z=0):

        if self.NumberOfAxis == 3:
            try:
                print("moved x by %d, y by %d, z by %d" % (x, y, z))
                self.x += x
                self.y += y
                self.z += z
            except:
                print('An Error has occured')
                self.showErr()

    def moveAbsoluteXYZ(self, x, y, z):
        print("moved to position x:%d, y:%d, z:%d" % (x, y, z))
        self.moveRelative(x-self.x, y-self.y, z-self.z)

    def getPosition(self):
        return self.x, self.y, self.z

    def clear(self):  # Should clear any lingering messages in the device
        try:
            print("clear dummy corvus")  # Clears the parameter stack, refer to page 287 in manual for more detail
        except:
            self.showErr()

    def reset(self):  # Resets the whole device, equivalent of disconnecting the power according to the manual
        # a beep should be heard after the device is reset
        try:
            print("reset dummy corvus")
        except:
            self.showErr()

    def showErr(self):
        print("error with dummy corvus")
