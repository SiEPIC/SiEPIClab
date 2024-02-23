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
            routineType = self.find_string_in_brackets(routine)
            routineType = routineType.replace('_ida','')
            if routineType == 'wavelength_sweep':
                wavelengthSweepRoutines.append(routine)
        return wavelengthSweepRoutines

    def getVoltageSweepRoutines(self):
        voltageSweepRoutines = []
        for routine in self.routines:
            routineType = self.find_string_in_brackets(routine)
            routineType = routineType.replace('_ida','')
            if routineType == 'voltage_sweep':
                voltageSweepRoutines.append(routine)
        return voltageSweepRoutines

    def getCurrentSweepRoutines(self):
        currentSweepRoutines = []
        for routine in self.routines:
            routineType = self.find_string_in_brackets(routine)
            routineType = routineType.replace('_ida','')
            if routineType == 'current_sweep':
                currentSweepRoutines.append(routine)
        return currentSweepRoutines

    def getSetWavelengthVoltageSweepRoutines(self):
        setWavelengthVoltageSweepRoutines = []
        for routine in self.routines:
            routineType = self.find_string_in_brackets(routine)
            routineType = routineType.replace('_ida','')
            if routineType == 'set_Wavelength_Voltage_Sweep':
                setWavelengthVoltageSweepRoutines.append(routine)
        return setWavelengthVoltageSweepRoutines

    def getSetWavelengthCurrentSweepRoutines(self):
        setWavelengthCurrentSweepRoutines = []
        for routine in self.routines:
            routineType = routine.split(':')[0]
            if routineType == 'set_Wavelength_Current_Sweep':
                setWavelengthCurrentSweepRoutines.append(routine)
        return setWavelengthCurrentSweepRoutines

    def getSetVoltageWavelengthSweepRoutines(self):
        setVoltageWavelengthSweepRoutines = []
        for routine in self.routines:
            routineType = self.find_string_in_brackets(routine)
            routineType = routineType.replace('_ida','')
            if routineType == 'set_Voltage_Wavelength_Sweep':
                setVoltageWavelengthSweepRoutines.append(routine)
        return setVoltageWavelengthSweepRoutines

    def addRoutines(self, routines):
        """Adds the names of routines to be performed on this device to a list."""
        self.routines.extend(routines)

    def find_string_in_brackets(self, text):
        start_index = None
        end_index = None
        bracket_count = 0

        for i, char, in enumerate(text):
            if char == '(':
                start_index = i + 1
                bracket_count += 1
            elif char == ')':
                bracket_count -= 1
                if bracket_count == 0:
                    end_index = i
                    break
        if start_index is not None and end_index is not None:
            return text[start_index:end_index]
        else:
            return None




