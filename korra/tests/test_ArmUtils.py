import unittest
from pickit.Datatypes import *
import korra.ArmUtils as utils


class HelperFunctionsTest(unittest.TestCase):
    def test_joint_states_to_arm(self):
        z = (1.1, 1.2, 0, 0)
        shoulder = (1.3, 1.4, 0, 0)
        elbow = (1.5, 1.6, 0, 0)
        wrist = (1.7, 1.8, 0, 0)

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


class ArmWrapperTest(unittest.TestCase):
    def setUp(self):
        q0 = JointSpacePoint(0, 0, 0, 0)
        flip = 'right'
        self.arm = utils.ArmWrapper(q0, flip)

    def test_goto(self):
        start_pos = JointSpacePoint(0, 0, 0, 0)
        start_vel = JointSpacePoint(0, 0, 0, 0)
        start = (start_pos, start_vel)

        target_pos = RobotSpacePoint(0.2, 0.1, 0, 0)
        target_vel = RobotSpacePoint(0, 0, 0, 0)
        target = (target_pos, target_vel)

        pz, ps, pe, pw = self.arm.goto(start, target)

        start_tool_pos = self.arm.arm.arm.forward_kinematics(start_pos)
        self.arm.arm.arm.compute_jacobian()
        start_tool_vel = self.arm.arm.arm.get_tool_vel(start_vel)
        rs, re, rz, rw = self.arm.arm.goto(start_tool_pos, start_tool_vel,
                                           target_pos, target_vel)

        for z, z_ref in zip(pz, rz):
            self.assertAlmostEqual(z[0], z_ref[1])
            self.assertAlmostEqual(z[1], z_ref[2])
            self.assertAlmostEqual(z[2], z_ref[3])

        for s, s_ref in zip(ps, rs):
            self.assertAlmostEqual(s[0], s_ref[1])
            self.assertAlmostEqual(s[1], s_ref[2])
            self.assertAlmostEqual(s[2], s_ref[3])

        for e, e_ref in zip(pe, re):
            self.assertAlmostEqual(e[0], e_ref[1])
            self.assertAlmostEqual(e[1], e_ref[2])
            self.assertAlmostEqual(e[2], e_ref[3])

        for w, w_ref in zip(pw, rw):
            self.assertAlmostEqual(w[0], w_ref[1])
            self.assertAlmostEqual(w[1], w_ref[2])
            self.assertAlmostEqual(w[2], w_ref[3])
