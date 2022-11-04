
from pylablib.devices import Thorlabs


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
        self.bsc = Thorlabs.kinesis.KinesisMotor(SerialPortName, scale='stage')
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
        print("Absolute")
        self.bsc.move_by(x, channel=0)
        self.bsc.wait_move()
        self.bsc.move_by(y, channel=1)
        self.bsc.wait_move()
        self.bsc.move_by(z, channel=2)
        self.bsc.wait_move()

    def moveRelativeXYZ(self, x, y, z):
        self.bsc.move_to(x, channel=0)
        self.bsc.wait_move()
        self.bsc.move_to(y, channel=1)
        self.bsc.wait_move()
        self.bsc.move_to(z, channel=2)
        self.bsc.wait_move()
