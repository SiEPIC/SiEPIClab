
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

    def connect(self, SerialPortName, NumberOfAxis):
        numbers = re.findall('[0-9]+', SerialPortName)
        COM = "COM" + numbers[0]
        self.bsc = BSC(serial_port=COM, x=NumberOfAxis, home = False)
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

    # Moves all the axis together
    # can be used regardless of how many axis are enabled
    def moveAbsoluteXYZ(self, x, y, z):
        self.bsc.move_absolute(position= int(x), bay=1, channel=0)
        self.bsc.move_absolute(position= int(y), bay=2, channel=0)
        self.bsc.move_absolute(position= int(z), bay=0, channel=0)

    def moveRelativeXYZ(self, x, y, z):
        self.bsc.move_relative(distance=int(1000 * x), bay = 1, channel=0)
        self.bsc.move_relative(distance=int(1000 * y), bay = 2, channel=0)
        self.bsc.move_relative(distance=int(1000 * z), bay=0, channel=0)

    def getPosition(self):
        try:
            x = self.bsc.status_[0][0]["position"]
            y = self.bsc.status_[1][0]["position"]
            z = self.bsc.status_[2][0]["position"]
            return [x,y,z]
        except Exception as e:
            print(e)
            print('An Error has occured')

