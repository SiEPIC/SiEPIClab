import qontrol
import re

class QontrolMotor:
    name = 'Qontrol'
    isQontrol = True
    isMotor = False
    isOpt = False
    isElec = True
    isLaser = False
    isDetect = False
    isSMU = False

    def __init__(self):
        self.q = None
        self.numAxes = 0

    def connect(self, SerialPortName, NumberOfAxis):
        numbers = re.findall('[0-9]+', SerialPortName)
        COM = "COM" + numbers[0]
        self.q = qontrol.MXMotor(serial_port_name=COM)
        self.q.ustep[:] = 7
        self.numAxes = NumberOfAxis
        print('Connected\n')

        # Sets maximum # of axis to send commands to
        if NumberOfAxis >= 6 | NumberOfAxis < 0:
            print('Invalid number of axes. Please enter at most six axes.\n')
            self.numAxes = 6

    def disconnect(self):
        self.q.close()

    # Moves all the axis together
    # can be used regardless of how many axis are enabled
    def moveAbsoluteXYZ(self, x, y, z):
        print("Absolute")
        self.q[0] = x
        self.q.wait_until_stopped()
        self.q[1] = y
        self.q.wait_until_stopped()
        self.q[2] = z
        self.q.wait_until_stopped()

    def moveRelativeXYZ(self, x, y, z):
        xCurrentPos = self.q[0]
        yCurrentPos = self.q[1]
        zCurrentPos = self.q[2]
        print(xCurrentPos)
        print(yCurrentPos)
        self.q[0] = x - xCurrentPos
        self.q.wait_until_stopped()
        self.q[1] = y - yCurrentPos
        self.q.wait_until_stopped()
        self.q[2] = z - zCurrentPos
        self.q.wait_until_stopped()

