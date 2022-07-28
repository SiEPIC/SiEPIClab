class ElectroOpticDevice:

    def __init__(self, device_id, wavelength, polarization, x, y):

        self.device_id = device_id
        self.wavelength = wavelength
        self.polarization = polarization

        self.opticalCoordinates = [x, y]
        self.electricalCoordinates = []

    def addElectricalCoordinates(self, padname, x, y):

        self.electricalCoordinates.append([padname, x, y])

    def getOpticalCoordinates(self):

        return self.opticalCoordinates

    def getElectricalCoordinates(self):

        return self.electricalCoordinates

    def getDeviceID(self):

        return self.device_id

    #Returns the name and coordinates of the left-most bond pad within an electro-optic device in the form
    #of a list [bondpad name, x coordinates, y coordinates]
    def getReferenceBondPad(self):

        reference = self.electricalCoordinates[0]
        for bondpad in self.electricalCoordinates:
            if bondpad[1] < reference[1]:
                reference = bondpad
        return reference

