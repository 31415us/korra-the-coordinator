import unittest
from pickit.Datatypes import *
import korra.ArmUtils as utils

class HelperFunctionsTest(unittest.TestCase):
    def test_joint_states_to_arm(self):
        z = (1, 2)
        shoulder = (3, 4)
        elbow = (5, 6)
        wrist = (7, 8)

        (pos, vel) = utils.joint_states_to_arm(z, shoulder, elbow, wrist)

        self.assertAlmostEqual(pos.z, z[0])
        self.assertAlmostEqual(vel.z, z[1])

        self.assertAlmostEqual(pos.theta1, shoulder[0])
        self.assertAlmostEqual(vel.theta1, shoulder[1])

        self.assertAlmostEqual(pos.theta2, elbow[0])
        self.assertAlmostEqual(vel.theta2, elbow[1])

        self.assertAlmostEqual(pos.theta3, wrist[0])
        self.assertAlmostEqual(vel.theta3, wrist[1])

    def test_arm_to_joint_traj(self):
        pass
