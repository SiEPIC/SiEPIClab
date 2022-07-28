# TODO: Add the necessary keys to all self.deviceDict
class measurementRoutines:

    def __init__(self, flag, deviceInfo, smu, laser):

        self.deviceDict = deviceInfo
        self.SMU = smu
        self.laser = laser
        if flag == 'ELEC':
            self.ivSweep()
        if flag == 'OPT':
            self.opticalSweep()
        if flag == 'FIXWAVIV':
            self.fixedWavelengthIVSweep()
        if flag == 'BIASVOPT':
            self.opticalSweepWithBiasVoltages()

    def ivSweep(self):
        # min,max,res,independentVar
        self.SMU.ivsweep(self.deviceDict, self.deviceDict, self.deviceDict, self.deviceDict)

    # TODO: Fix this to use desired parameters
    def opticalSweep(self):
        self.laser.sweep()

    def fixedWavelengthIVSweep(self):
        # wavelength
        self.laser.setTLSWavelength(self.deviceDict, slot=self.laser.panel.getSelectedLaserSlot())
        # min,max,res,independentVar
        self.SMU.ivsweep(self.deviceDict, self.deviceDict, self.deviceDict, self.deviceDict)

    # TODO: Update Laser Sweep - also is channel info stored in dictionary?
    def opticalSweepWithBiasVoltages(self):
        # voltage, channel
        self.SMU.setVoltage(self.deviceDict, self.deviceDict)
        self.laser.sweep()
