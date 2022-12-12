
class measurementRoutines:

    def __init__(self, smu, laser, activeDetectors):
        """A class containing different types of measurement routines including iv sweeps, optical spectrum sweeps
        iv sweeps at fixed wavelengths and optical sweeps with bias voltages."""

        self.SMU = smu
        self.laser = laser
        self.activeDetectors = activeDetectors
        self.laserOutputMap = dict([('High power', 'highpower'), ('Low SSE', 'lowsse')])
        self.laserNumSweepMap = dict([('1', 1), ('2', 2), ('3', 3)])

    def voltageSweep(self, voltmin, voltmax, voltres, A, B):
        try:
            if A:
                self.SMU.turnchannelon('A')
            if B:
                self.SMU.turnchannelon('B')
            self.SMU.ivsweep(float(voltmin), float(voltmax), float(voltres), 'Voltage')
            self.SMU.turnchanneloff('A')
            self.SMU.turnchanneloff('B')
            return self.SMU.voltageresultA, self.SMU.currentresultA, self.SMU.resistanceresultA, self.SMU.powerresultA, self.SMU.voltageresultB, self.SMU.currentresultB, self.SMU.resistanceresultB,self.SMU.powerresultB

        except Exception as e:
            print(e)

    def currentSweep(self, imin, imax, ires, A, B):
        try:
            if A:
                self.SMU.turnchannelon('A')
            if B:
                self.SMU.turnchannelon('B')
            self.SMU.ivsweep(float(imin), float(imax), float(ires), 'Current')
            self.SMU.turnchanneloff('A')
            self.SMU.turnchanneloff('B')

            return self.SMU.voltageresultA, self.SMU.currentresultA, self.SMU.resistanceresultA,\
                    self.SMU.powerresultA, self.SMU.voltageresultB, self.SMU.currentresultB, self.SMU.resistanceresultB,\
                    self.SMU.powerresultB

        except Exception as e:
            print(e)

    def copySweepSettings(self, start, stop, stepsize, sweepspeed, sweeppower, laseroutput, numscans, initrange, rangedec):
        """ Copies the current sweep settings in the dictionary to the laser object."""
        self.laser.sweepStartWvl = float(start) / 1e9
        self.laser.sweepStopWvl = float(stop) / 1e9
        self.laser.sweepStepWvl = float(stepsize) / 1e9
        self.laser.sweepSpeed = sweepspeed
        self.laser.sweepUnit = 'dBm'
        self.laser.sweepPower = float(sweeppower)
        self.laser.sweepLaserOutput = self.laserOutputMap[laseroutput]
        self.laser.sweepNumScans = self.laserNumSweepMap[numscans]
        self.laser.sweepInitialRange = initrange
        self.laser.sweepRangeDecrement = rangedec
        activeDetectors = self.activeDetectors
        if len(activeDetectors) == 0:
            raise Exception('Cannot perform sweep. No active detectors selected.')
        self.laser.activeSlotIndex = activeDetectors

    def opticalSweep(self, start, stop, stepsize, sweepspeed, sweeppower, laseroutput, numscans, initrange, rangedec):
        try:
            self.copySweepSettings(start, stop, stepsize, sweepspeed, sweeppower, laseroutput, numscans, initrange, rangedec)
            self.lastSweepWavelength, self.lastSweepPower = self.laser.sweep()
            return self.lastSweepWavelength, self.lastSweepPower

        except Exception as e:
            print(e)
        self.laser.setAutorangeAll()

    def fixedWavelengthVoltageSweep(self, voltmin, voltmax, voltres, A, B, wavelength):
        try:
            self.laser.setTLSWavelength(float(wavelength)*float(1e-9))
            return self.voltageSweep(float(voltmin), float(voltmax), float(voltres), A, B)
        except Exception as e:
            print(e)

    def fixedWavelengthCurrentSweep(self, imin, imax, ires, A, B, wavelength):
        try:
            self.laser.setTLSWavelength(float(wavelength)*float(1e-9))
            return self.currentSweep(float(imin), float(imax), float(ires), A, B)
        except Exception as e:
            print(e)

    def opticalSweepWithBiasVoltage(self, start, stop, stepsize, sweepspeed, sweeppower, laseroutput, numscans,
                                    initrange, rangedec, voltage, A, B):
        if A:
            self.SMU.setVoltage(voltage, 'A')
        if B:
            self.SMU.setVoltage(voltage, 'B')
        return self.opticalSweep(start, stop, stepsize, sweepspeed, sweeppower, laseroutput, numscans, initrange, rangedec)
