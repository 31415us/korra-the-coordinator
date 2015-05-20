import unittest

from math import pi

from molly.Vec2D import Vec2D

import korra.Utils as utils


class HelperFunctionsTest(unittest.TestCase):
    def test_robot_to_molly(self):
        robot_state = (0, 0, 1, pi / 2, 0)

        ref_pos = Vec2D()
        ref_heading = Vec2D(0, 1)
        ref_speed = 1.0

        (pos, heading, speed) = utils.robot_state_to_molly(robot_state)

        self.assertTrue(pos.is_equal(ref_pos))
        self.assertTrue(heading.is_equal(ref_heading))
        self.assertAlmostEqual(speed, ref_speed)

    def test_molly_to_robot_v0(self):
        molly_point = (Vec2D(), Vec2D(), Vec2D(), 0.0)
        prev_robot_state = (0, 0, 0, pi / 4, pi / 4)

        ref_state = (0, 0, 0, pi / 2, 0)

        out = utils.molly_to_robot_state(molly_point, prev_robot_state, 1.0)

        self.assertAlmostEqual(out[0], ref_state[0])
        self.assertAlmostEqual(out[1], ref_state[1])
        self.assertAlmostEqual(out[2], ref_state[2])
        self.assertAlmostEqual(out[3], ref_state[3])
        self.assertAlmostEqual(out[4], ref_state[4])

    def test_molly_to_robot_vnot0(self):
        molly_point = (Vec2D(), Vec2D(1, 0), Vec2D(0, 0.1), 0.0)
        prev_robot_state = (0, 0, 1, 0, 0)

        ref_state = (0, 0, 1, 0, 0.1)

        out = utils.molly_to_robot_state(molly_point, prev_robot_state, 1.0)

        self.assertAlmostEqual(out[0], ref_state[0])
        self.assertAlmostEqual(out[1], ref_state[1])
        self.assertAlmostEqual(out[2], ref_state[2])
        self.assertAlmostEqual(out[3], ref_state[3])
        self.assertAlmostEqual(out[4], ref_state[4])


class MollyWrapperTest(unittest.TestCase):
    def setUp(self):
        self.wrapper = utils.MollyWrapper()

    def test_traj_no_target(self):
        robot_state = (0, 0, 1, 0, 0)
        target = None
        obstacles = []

        traj = self.wrapper.get_trajectory(robot_state, target, obstacles)

        # test that ramp_down trajectory is generated
        gen = iter(traj)
        (_, _, prev_v, _, _) = next(gen)
        for (_, _, v, _, _) in gen:
            self.assertTrue(v <= prev_v)
            prev_v = v

    def test_target_eq_pos(self):
        robot_state = (0, 0, 0, 0, 0)
        target = Vec2D()
        obstacles = []

        traj = self.wrapper.get_trajectory(robot_state, target, obstacles)

        self.assertTrue(len(traj) == 1)

        state = traj[0]

        self.assertAlmostEqual(state[0], robot_state[0])
        self.assertAlmostEqual(state[1], robot_state[1])
        self.assertAlmostEqual(state[2], robot_state[2])
        self.assertAlmostEqual(state[3], robot_state[3])
        self.assertAlmostEqual(state[4], robot_state[4])

    def test_speed_zero_rotate(self):
        robot_state = (0, 0, 0, 0, 0)
        target = Vec2D(0, 1)
        obstacles = []

        traj = self.wrapper.get_trajectory(robot_state, target, obstacles)

        self.assertTrue(len(traj) > 10)

        sub_traj = traj[:10]

        prev_theta = 0
        for (_, _, _, theta, _) in sub_traj:
            self.assertTrue(prev_theta <= theta)
            prev_theta = theta
