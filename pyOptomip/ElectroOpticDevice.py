class ElectroOpticDevice:

    def __init__(self, device_id, wavelength, polarization, x, y, type):
        """Object used to store all information associated with an electro-optic device"""
        self.device_id = device_id
        self.wavelength = wavelength
        self.polarization = polarization
        self.opticalCoordinates = [x, y]
        self.electricalCoordinates = []
        self.type = type
        self.wavelengthSweeps = {'Start': [], 'Stop': [], 'Stepsize': [], 'Sweeppower': [], 'Sweepspeed': [],
                                 'Laseroutput': [], 'Numscans': [], 'InitialRange': [], 'RangeDec': []}
        self.voltageSweeps = {'VoltMin': [], 'VoltMax': [], 'VoltRes': [], 'IV': [], 'RV': [], 'PV': [],
                              'ChannelA': [], 'ChannelB': []}
        self.currentSweeps = {'CurrentMin': [], 'CurrentMax': [], 'CurrentRes': [], 'IV': [], 'RV': [],
                              'PV': [], 'ChannelA': [], 'ChannelB': []}
        self.setWavelengthVoltageSweeps = {'VoltMin': [], 'VoltMax': [], 'VoltRes': [], 'IV': [], 'RV': [],
                                           'PV': [], 'ChannelA': [], 'ChannelB': [], 'Wavelength': []}
        self.setWavelengthCurrentSweeps = {'CurrentMin': [], 'CurrentMax': [], 'CurrentRes': [], 'IV': [],
                                           'RV': [], 'PV': [], 'ChannelA': [], 'ChannelB': [],
                                           'Wavelength': []}
        self.setVoltageWavelengthSweeps = {'Start': [], 'Stop': [], 'Stepsize': [], 'Sweeppower': [],
                                           'Sweepspeed': [], 'Laseroutput': [], 'Numscans': [],
                                           'InitialRange': [], 'RangeDec': [], 'ChannelA': [], 'ChannelB': [],
                                           'Voltage': []}

    def addElectricalCoordinates(self, padName, x, y):
        """Associates a bondpad with the device"""
        self.electricalCoordinates.append([padName, x, y])

    def getOpticalCoordinates(self):
        """Returns the coordinates of the optical input for the device as [x coordinate, y coordinate]"""
        if self.opticalCoordinates:
            return self.opticalCoordinates

    def getElectricalCoordinates(self):
        """Return a list of electrical bondpads. Bondpads are stored as lists in the form [pad name,
        x coordinate, y coordinate]"""
        return self.electricalCoordinates

    def getDeviceID(self):
        """Returns the device id of the device. IDs should be unique for each device within a chip"""
        return self.device_id

    def getDeviceType(self):
        """Returns the type of the device"""
        x = self.type.split(',')
        return x[0]

    def getReferenceBondPad(self):
        """Returns the name and coordinates of the left-most bond pad within
        an electro-optic device in the form of a list [bond pad name, x coordinates, y coordinates]"""
        if self.electricalCoordinates:
            reference = self.electricalCoordinates[0]
            for bondPad in self.electricalCoordinates:
                if bondPad[1] < reference[1]:
                    reference = bondPad
            return reference

    def addWavelengthSweep(self, start, stop, stepsize, sweeppower, sweepspeed, laseroutput, numscans,
                           initialrange, rangedec):
        """"""
        self.wavelengthSweeps['Start'].append(start)
        self.wavelengthSweeps['Stop'].append(stop)
        self.wavelengthSweeps['Stepsize'].append(stepsize)
        self.wavelengthSweeps['Sweeppower'].append(sweeppower)
        self.wavelengthSweeps['Sweepspeed'].append(sweepspeed)
        self.wavelengthSweeps['Laseroutput'].append(laseroutput)
        self.wavelengthSweeps['Numscans'].append(numscans)
        self.wavelengthSweeps['InitialRange'].append(initialrange)
        self.wavelengthSweeps['RangeDec'].append(rangedec)

    def addVoltageSweep(self, voltmin, voltmax, voltres, iv, rv, pv, a, b):
        """"""
        self.voltageSweeps['VoltMin'].append(voltmin)
        self.voltageSweeps['VoltMax'].append(voltmax)
        self.voltageSweeps['VoltRes'].append(voltres)
        self.voltageSweeps['IV'].append(iv)
        self.voltageSweeps['RV'].append(rv)
        self.voltageSweeps['PV'].append(pv)
        self.voltageSweeps['ChannelA'].append(a)
        self.voltageSweeps['ChannelB'].append(b)

    def addCurrentSweep(self, currentmin, currentmax, currentres, iv, rv, pv, a, b):
        """"""
        self.currentSweeps['CurrentMin'].append(currentmin)
        self.currentSweeps['CurrentMax'].append(currentmax)
        self.currentSweeps['CurrentRes'].append(currentres)
        self.currentSweeps['IV'].append(iv)
        self.currentSweeps['RV'].append(rv)
        self.currentSweeps['PV'].append(pv)
        self.currentSweeps['ChannelA'].append(a)
        self.currentSweeps['ChannelB'].append(b)

    def addSetWavelengthVoltageSweep(self, voltmin, voltmax, voltres, iv, rv, pv, a, b, wavelengths):
        """"""
        for wavelength in wavelengths:
            self.setWavelengthVoltageSweeps['VoltMin'].append(voltmin)
            self.setWavelengthVoltageSweeps['VoltMax'].append(voltmax)
            self.setWavelengthVoltageSweeps['VoltRes'].append(voltres)
            self.setWavelengthVoltageSweeps['IV'].append(iv)
            self.setWavelengthVoltageSweeps['RV'].append(rv)
            self.setWavelengthVoltageSweeps['PV'].append(pv)
            self.setWavelengthVoltageSweeps['ChannelA'].append(a)
            self.setWavelengthVoltageSweeps['ChannelB'].append(b)
            self.setWavelengthVoltageSweeps['Wavelength'].append(wavelength)

    def addSetWavelengthCurrentSweep(self, currentmin, currentmax, currentres, iv, rv, pv, a, b, wavelengths):
        """"""
        for wavelength in wavelengths:
            self.setWavelengthCurrentSweeps['CurrentMin'].append(currentmin)
            self.setWavelengthCurrentSweeps['CurrentMax'].append(currentmax)
            self.setWavelengthCurrentSweeps['CurrentRes'].append(currentres)
            self.setWavelengthCurrentSweeps['IV'].append(iv)
            self.setWavelengthCurrentSweeps['RV'].append(rv)
            self.setWavelengthCurrentSweeps['PV'].append(pv)
            self.setWavelengthCurrentSweeps['ChannelA'].append(a)
            self.setWavelengthCurrentSweeps['ChannelB'].append(b)
            self.setWavelengthCurrentSweeps['Wavelength'].append(wavelength)

    def addSetVoltageWavelengthSweep(self, start, stop, stepsize, sweeppower, sweepspeed, laseroutput,
                                     numscans, initialrange, rangedec, a, b, voltages):
        """"""
        for voltage in voltages:
            self.setVoltageWavelengthSweeps['Start'].append(start)
            self.setVoltageWavelengthSweeps['Stop'].append(stop)
            self.setVoltageWavelengthSweeps['Stepsize'].append(stepsize)
            self.setVoltageWavelengthSweeps['Sweeppower'].append(sweeppower)
            self.setVoltageWavelengthSweeps['Sweepspeed'].append(sweepspeed)
            self.setVoltageWavelengthSweeps['Laseroutput'].append(laseroutput)
            self.setVoltageWavelengthSweeps['Numscans'].append(numscans)
            self.setVoltageWavelengthSweeps['InitialRange'].append(initialrange)
            self.setVoltageWavelengthSweeps['RangeDec'].append(rangedec)
            self.setVoltageWavelengthSweeps['ChannelA'].append(a)
            self.setVoltageWavelengthSweeps['ChannelB'].append(initialrange)
            self.setVoltageWavelengthSweeps['Voltage'].append(voltage)

    def getWavelengthSweeps(self):
        return self.wavelengthSweeps

    def getVoltageSweeps(self):
        return self.voltageSweeps

    def getCurrentSweeps(self):
        return self.currentSweeps

    def getSetWavelengthVoltageSweeps(self):
        return self.setWavelengthVoltageSweeps

    def getSetWavelengthCurrentSweeps(self):
        return self.setWavelengthCurrentSweeps

    def getSetVoltageWavelengthSweeps(self):
        return self.setVoltageWavelengthSweeps

    def hasRoutines(self):
        return self.wavelengthSweeps or self.voltageSweeps or self.currentSweeps or \
               self.setWavelengthVoltageSweeps or self.setWavelengthCurrentSweeps or \
               self.setVoltageWavelengthSweeps

