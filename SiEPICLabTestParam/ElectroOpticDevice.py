class ElectroOpticDevice:

    def __init__(self, device_id, wavelength, polarization, opticalCoords, type):
        """Object used to store all information associated with an electro-optic device"""
        self.device_id = device_id
        self.wavelength = wavelength
        self.polarization = polarization
        self.opticalCoordinates = opticalCoords
        self.type = type
        self.electricalCoordinates = []
        self.routines = []

    def addElectricalCoordinates(self, elecCoords):
        """Associates a bondpad with the device"""
        self.electricalCoordinates.append(elecCoords)

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

    def getDeviceWavelength(self):
        return self.wavelength

    def getDevicePolarization(self):
        return self.polarization

    def getDeviceType(self):
        """Returns the type of the device"""
        x = self.type#.split(',')
        return x

    def getReferenceBondPad(self):
        """Returns the name and coordinates of the left-most bond pad within
        an electro-optic device in the form of a list [bond pad name, x coordinates, y coordinates]"""
        if self.electricalCoordinates:
            reference = self.electricalCoordinates[0]
            for bondPad in self.electricalCoordinates:
                if bondPad[1] < reference[1]:
                    reference = bondPad
            return reference

    def hasRoutines(self):
        if self.routines:
            return True
        else:
            return False

    def getWavelengthSweepRoutines(self):
        wavelengthSweepRoutines = []
        for routine in self.routines:
            routineType = routine.split(':')[0]
            if routineType == 'Wavelength Sweep':
                wavelengthSweepRoutines.append(routine.split(':')[1])
        return wavelengthSweepRoutines

    def getVoltageSweepRoutines(self):
        voltageSweepRoutines = []
        for routine in self.routines:
            routineType = routine.split(':')[0]
            if routineType == 'Voltage Sweep':
                voltageSweepRoutines.append(routine.split(':')[1])
        return voltageSweepRoutines

    def getCurrentSweepRoutines(self):
        currentSweepRoutines = []
        for routine in self.routines:
            routineType = routine.split(':')[0]
            if routineType == 'Current Sweep':
                currentSweepRoutines.append(routine.split(':')[1])
        return currentSweepRoutines

    def getSetWavelengthVoltageSweepRoutines(self):
        setWavelengthVoltageSweepRoutines = []
        for routine in self.routines:
            routineType = routine.split(':')[0]
            if routineType == 'Set Wavelength Voltage Sweep':
                setWavelengthVoltageSweepRoutines.append(routine.split(':')[1])
        return setWavelengthVoltageSweepRoutines

    def getSetWavelengthCurrentSweepRoutines(self):
        setWavelengthCurrentSweepRoutines = []
        for routine in self.routines:
            routineType = routine.split(':')[0]
            if routineType == 'Set Wavelength Current Sweep':
                setWavelengthCurrentSweepRoutines.append(routine.split(':')[1])
        return setWavelengthCurrentSweepRoutines

    def getSetVoltageWavelengthSweepRoutines(self):
        setVoltageWavelengthSweepRoutines = []
        for routine in self.routines:
            routineType = routine.split(':')[0]
            if routineType == 'Set Voltage Wavelength Sweep':
                setVoltageWavelengthSweepRoutines.append(routine.split(':')[1])
        return setVoltageWavelengthSweepRoutines

    def addRoutines(self, routines):
        """Adds the names of routines to be performed on this device to a list."""
        self.routines.extend(routines)



