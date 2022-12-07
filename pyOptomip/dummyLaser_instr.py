
class dummylaser(object):

    # Constants
    name = 'Dummy Laser'
    isMotor = False
    isLaser = True
    isDetect = True
    isSMU = False

    def __init__(self):
        self.numPWMSlots = 9
        self.connected = False

    def __del__(self):
        if self.connected:
            self.disconnect()

    def connect(self, visaAddr, reset=0, forceTrans=1, autoErrorCheck=1):
        """ Connects to the instrument.
        visaAddr -- VISA instrument address e.g. GPIB0::20::INSTR
        reset -- Reset instrument after connecting
        """
        if self.connected:
            print('Already connected to the laser. Aborting connection.')
            return
        print('Connected to the laser')
        self.connected = True

    def sweep(self):
        """ Performs a wavelength sweep """
        print('Performing wavelength sweep.')

    def disconnect(self):
        self.connected = False
        print('Disconnected from the laser')