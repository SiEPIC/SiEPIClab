
from autoMeasure import *
import unittest
import numpy as np
import matplotlib.pyplot as plt

import dummyMotorParameters
import dummyLaserParameters
import SMUParameters
import fineAlign


class TestTransformMatrix(unittest.TestCase):

    def __init__(self, parent):
        """
        Set up for testing accuracy of transform matrix calculations.
        Args:
            parent: unittest.TestCase
        """
        super(TestTransformMatrix, self).__init__(parent)
        laser = dummyLaserParameters
        motor = dummyMotorParameters
        smu = SMUParameters
        fineA = fineAlign
        # Setting up test motor and gds coordinates
        self.motorCoords = [[-10, 10, 300], [-10, -10, 1000], [10, -10, 10]]
        self.gdsCoords = [[-10, 10, 1], [-10, -10, 1], [10, -10, 1]]

        # Auto measure object used for testing
        self.autoMeasure = autoMeasure(laser, motor, motor, smu, fineA)

        # Create test matrix
        self.TestMatrix1 = self.autoMeasure.findCoordinateTransformOpt(self.motorCoords, self.gdsCoords)

    def test_Matrix_Redo(self):
        """Plots the motor and gds plane as well as the given and transformed point."""

        plt.rcParams["figure.figsize"] = [7.00, 3.50]
        plt.rcParams["figure.autolayout"] = True

        # gds plane
        A = [self.gdsCoords[0][0], self.gdsCoords[0][1], self.gdsCoords[0][2]]
        B = [self.gdsCoords[1][0], self.gdsCoords[1][1], self.gdsCoords[1][2]]
        C = [self.gdsCoords[2][0], self.gdsCoords[2][1], self.gdsCoords[2][2]]
        v1 = [B[0] - A[0], B[1] - A[1], B[2] - A[2]]
        v2 = [C[0] - A[0], C[1] - A[1], C[2] - A[2]]
        n1 = np.cross(v1, v2)
        n1 = -n1 / n1[2]
        k1 = -(n1[0] * A[0] + n1[1] * A[1] + n1[2] * A[2])

        # motor plane
        D = [self.motorCoords[0][0], self.motorCoords[0][1], self.motorCoords[0][2]]
        E = [self.motorCoords[1][0], self.motorCoords[1][1], self.motorCoords[1][2]]
        F = [self.motorCoords[2][0], self.motorCoords[2][1], self.motorCoords[2][2]]
        v3 = [E[0] - D[0], E[1] - D[1], E[2] - D[2]]
        v4 = [F[0] - D[0], F[1] - D[1], F[2] - D[2]]
        n2 = np.cross(v3, v4)
        n2 = -n2 / n2[2]
        k2 = -(n2[0] * D[0] + n2[1] * D[1] + n2[2] * D[2])

        x = np.linspace(-10, 10, 100)
        y = np.linspace(-10, 10, 100)

        x, y = np.meshgrid(x, y)

        eq1 = n1[0] * x + n1[1] * y + k1
        eq2 = n2[0] * x + n2[1] * y + k2

        T = self.autoMeasure.coordinate_transform_matrix(self.motorCoords, self.gdsCoords)
        print(T)
        oldCoords = self.gdsCoords[0]
        newCoords = self.autoMeasure.perform_transform(oldCoords)

        fig = plt.figure()

        ax = fig.gca(projection='3d')

        ax.plot_surface(x, y, eq1)
        ax.plot_surface(x, y, eq2)
        ax.scatter(oldCoords[0], oldCoords[1], 1, color='green')
        ax.scatter(newCoords[0], newCoords[1], newCoords[2], color='red')
        print(oldCoords)
        print(newCoords)

        plt.show()

    def test_in_plane(self):
        """Check whether the transformed point is within the motor plane."""

        # motor plane
        D = [self.motorCoords[0][0], self.motorCoords[0][1], self.motorCoords[0][2]]
        E = [self.motorCoords[1][0], self.motorCoords[1][1], self.motorCoords[1][2]]
        F = [self.motorCoords[2][0], self.motorCoords[2][1], self.motorCoords[2][2]]
        v3 = [E[0] - D[0], E[1] - D[1], E[2] - D[2]]
        v4 = [F[0] - D[0], F[1] - D[1], F[2] - D[2]]
        n2 = np.cross(v3, v4)
        k2 = (n2[0] * D[0] + n2[1] * D[1] + n2[2] * D[2])

        T = self.autoMeasure.coordinate_transform_matrix(self.motorCoords, self.gdsCoords)
        print(T)
        oldCoords = self.gdsCoords[0]
        newCoords = self.autoMeasure.perform_transform(oldCoords)

        newEq = n2[0]*newCoords[0]+n2[1]*newCoords[1]+n2[2]*newCoords[2]
        self.assertEqual(k2, newEq)

    def test_new_vs_old(self):
        """Check the x and y coordinates for the motor against those calculated using the old method."""
        T = self.autoMeasure.coordinate_transform_matrix(self.motorCoords, self.gdsCoords)
        newCoords = self.autoMeasure.perform_transform(self.gdsCoords[0])
        print(newCoords)
        S = self.autoMeasure.findCoordinateTransform(self.motorCoords, self.gdsCoords)
        oldCoords = self.autoMeasure.gdsToMotor(self.gdsCoords[0])
        print(oldCoords)
        self.assertEqual(newCoords[0][0], oldCoords[0])
        self.assertAlmostEqual(newCoords[1][0], oldCoords[1], 10)


if __name__ == '__main__':
    unittest.main()
