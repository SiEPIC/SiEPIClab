import numpy as np
from autoMeasure import *
import unittest

from pyOptomip.dummyMotorParameters import dummyMotorParameters
from pyOptomip.dummyLaserParameters import dummyLaserParameters
from pyOptomip.fineAlign import fineAlign


class TestTransformMatrix(unittest.TestCase):

    def SetUp(self):
        laser = dummyLaserParameters
        motor = dummyMotorParameters
        fineA = fineAlign(laser, motor)
        motorCoords = []
        gdsCoords = []

        self.autoMeasure = autoMeasure(laser, motor, fineA)
        self.TestMatrix1 = autoMeasure.findCoordinateTransform(motorCoords, gdsCoords)

    def test_AffineTransform(self):
        self.assertEqual(self.TestMatrix1[3][0], 0)
        self.assertEqual(self.TestMatrix1[3][1], 0)
        self.assertEqual(self.TestMatrix1[3][2], 0)
        self.assertEqual(self.TestMatrix1[3][3], 1)


if __name__ == '__main__':
    unittest.main()
