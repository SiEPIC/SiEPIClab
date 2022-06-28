import qontrol


class QontrolMotor:
    name = 'Qontrol'
    isQontrol = True
    isMotor = False
    isLaser = False

    def __init__(self):
        self.q = None
        self.numAxes = 0

    def connect(self, SerialPortName, NumberOfAxis):
        self.q = qontrol.MXMotor(serial_port_name=SerialPortName)
        self.numAxes = NumberOfAxis
        print('Connected\n')

        # Sets maximum # of axis to send commands to
        if NumberOfAxis >= 6 | NumberOfAxis < 0:
            print('Invalid number of axes. Please enter at most six axes.\n')
            self.numAxes = 6

    def disconnect(self):
        self.q.close()
