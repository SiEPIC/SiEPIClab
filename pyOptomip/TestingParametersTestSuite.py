import numpy as np
from TestParameters import *
import unittest




class TestTestingParameters(unittest.TestCase):

    def SetUp(self):
        laser = dummyLaserParameters
        motor = dummyMotorParameters
        fineA = fineAlign(laser, motor)
        motorCoords = []
        gdsCoords = []

        self.testparameters = TestParameters()
        self.autoMeasure = autoMeasure(laser, motor, fineA)
        self.TestMatrix1 = autoMeasure.findCoordinateTransform(motorCoords, gdsCoords)

    def test_AffineTransform(self):
        self.assertEqual(self.TestMatrix1[3][0], 0)
        self.assertEqual(self.TestMatrix1[3][1], 0)
        self.assertEqual(self.TestMatrix1[3][2], 0)
        self.assertEqual(self.TestMatrix1[3][3], 1)


if __name__ == '__main__':
    unittest.main()
