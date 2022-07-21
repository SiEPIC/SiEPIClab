import numpy as np
from autoMeasure import *
import unittest


class TestTransformMatrix(unittest.TestCase):

    def SetUp(self):

        laser =
        motor =
        fineAlign =
        motorCoords =
        gdsCoords =

        self.autoMeasure = autoMeasure(laser, motor, fineAlign)
        self.TestMatrix1 = autoMeasure.findCoordinateTransform(motorCoords, gdsCoords)

    def test_AffineTransform(self):
        self.assertEqual(TestMatrix1[3][0], 0)
        self.assertEqual(TestMatrix1[3][1], 0)
        self.assertEqual(TestMatrix1[3][2], 0)
        self.assertEqual(TestMatrix1[3][3], 1)


if __name__ == '__main__':
    unittest.main()
