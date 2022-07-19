class ElectroOpticDevice:

    def __init__(self, device_id, wavelength, polarization, x, y):

        self.device_id = device_id
        self.wavelength = wavelength
        self.polarization = polarization

        self.opticalCoordinates = [device_id, x, y]
        self.electricalCoordinates = []

    def addElectricalCoordinates(self, padname, x, y):

        self.electricalCoordinates.append([padname, x, y])

    def getOpticalCoordinates(self):

        return self.opticalCoordinates

    def getElectricalCoordinates(self):

        return self.electricalCoordinates

    def getDeviceID(self):

        return self.device_id


