from thorlabs_apt_device import BSC
import re


class BSC203Motor:
    name = 'BSC203'
    isMotor = True
    isOpt = False
    isElec = True
    isLaser = False
    isDetect = False
    isSMU = False

    def __init__(self):
        self.bsc = None
        self.numAxes = 0
        self.position = [0, 0, 0]
        self.minPositionSet = False
        self.minXPosition = 0
        self.maxZPositionSet = False
        self.maxZPosition = 0

    def connect(self, SerialPortName, NumberOfAxis):
        self.visaName = SerialPortName
        numbers = re.findall('[0-9]+', SerialPortName)
        COM = "COM" + numbers[0]
        self.bsc = BSC(serial_port=COM, x=NumberOfAxis, home=False)
        self.bsc.identify()
        self.status = self.bsc.status_
        self.numAxes = NumberOfAxis
        print('Connected\n')

        # Sets maximum # of axis to send commands to
        if NumberOfAxis >= 6 | NumberOfAxis < 0:
            print('Invalid number of axes. Please enter at most six axes.\n')
            self.numAxes = 6

    def disconnect(self):
        self.bsc.close()

    def moveRelativeXYZ(self, x, y, z):
        if self.minPositionSet is False and self.maxZPositionSet is False:
            self.bsc.move_relative(distance=int(1000 * x), bay=0, channel=0)
            self.bsc.move_relative(distance=int(1000 * y), bay=1, channel=0)
            self.bsc.move_relative(distance=int(1000 * z), bay=2, channel=0)
            self.position[0] = self.position[0] - x
            self.position[1] = self.position[1] - y
            self.position[2] = self.position[2] - z
        elif self.minPositionSet is True and self.maxZPositionSet is False:
            if self.position[0] - x < self.minXPosition:
                print("Cannot Move Past Minimum X Position.")
            else:
                self.bsc.move_relative(distance=int(1000 * x), bay=0, channel=0)
                self.bsc.move_relative(distance=int(1000 * y), bay=1, channel=0)
                self.bsc.move_relative(distance=int(1000 * z), bay=2, channel=0)
                self.position[0] = self.position[0] - x
                self.position[1] = self.position[1] - y
                self.position[2] = self.position[2] - z
        elif self.minPositionSet is False and self.maxZPositionSet is True:
            if self.position[2] - z >= (self.maxZPosition - 80):
                print("Please Lift Wedge Probe.")
            else:
                self.bsc.move_relative(distance=int(1000 * x), bay=0, channel=0)
                self.bsc.move_relative(distance=int(1000 * y), bay=1, channel=0)
                self.bsc.move_relative(distance=int(1000 * z), bay=2, channel=0)
                self.position[0] = self.position[0] - x
                self.position[1] = self.position[1] - y
                self.position[2] = self.position[2] - z
        elif self.minPositionSet is True and self.maxZPositionSet is True:
            if self.position[0] - x < self.minXPosition:
                print("Cannot Move Past Minimum X Position.")
            elif self.position[2] - z >= (self.maxZPosition - 80):
                print("Please Lift Wedge Probe.")
            else:
                self.bsc.move_relative(distance=int(1000 * x), bay=0, channel=0)
                self.bsc.move_relative(distance=int(1000 * y), bay=1, channel=0)
                self.bsc.move_relative(distance=int(1000 * z), bay=2, channel=0)
                self.position[0] = self.position[0] - x
                self.position[1] = self.position[1] - y
                self.position[2] = self.position[2] - z


    def moveRelativeX(self, x):
        if self.minPositionSet is False:
            if x != 0:
                print('Please Set Minimum Position in X Axis.')
            else:
                pass
        else:
            if self.position[0] - x < self.minXPosition:
                print("Cannot Move Past Minimum X Position.")
            else:
                self.bsc.move_relative(distance=int(1000 * x), bay=0, channel=0)
                self.position[0] = self.position[0] - x

    def moveRelativeY(self, y):
        self.bsc.move_relative(distance=int(1000 * y), bay=1, channel=0)
        self.position[1] = self.position[1] - y

    def moveRelativeZ(self, z):
        self.bsc.move_relative(distance=int(1000 * z), bay=2, channel=0)
        self.position[2] = self.position[2] - z

    def getPosition(self):
        try:
            x = self.position[0]
            y = self.position[1]
            z = self.position[2]
            return [x, y, z]
        except Exception as e:
            print(e)
            print('An Error has occured')

    def setMinXPosition(self, minPosition):
        self.minXPosition = minPosition
        self.minPositionSet = True
