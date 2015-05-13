
import unittest
import pykka

from korra.EnvironmentActor import EnvironmentActor
from molly.Vec2D import Vec2D

class EnvironmentActorTest(unittest.TestCase):

    def setUp(self):
        self.env = EnvironmentActor.start(Vec2D(1, 1), Vec2D(1, 0), 0.1)

    def tearDown(self):
        pykka.ActorRegistry.stop_all()

    def test_init(self):
        enemies = self.env.proxy().get_enemies().get()
        self.assertTrue(len(enemies) == 0)

        self.assertTrue(self.env.proxy().get_friend().get() is None)

        (pos, heading, speed, _) = self.env.proxy().get_robot_state(0.0).get()

        self.assertTrue(pos == Vec2D(1, 1))
        self.assertTrue(heading == Vec2D(1, 0))
        self.assertTrue(speed == 0.0)

        (traj, _) = self.env.proxy().get_traj().get()
        self.assertTrue(not traj)

    def test_update_friend(self):
        pos = Vec2D(2, 2)

        msg = {
                'cmd' : 'update_friend',
                'friend' : pos
              }
        self.env.tell(msg)

        friend = self.env.proxy().get_friend().get()

        self.assertTrue(friend == pos)

    def test_update_enemy(self):
        pos = Vec2D()
        msg = {
                'cmd' : 'update_enemy',
                'enemy' : (pos, 1)
                }
        self.env.tell(msg)

        enemies = self.env.proxy().get_enemies().get()
        self.assertTrue(len(enemies) == 1)
        self.assertTrue(enemies[0] == pos)

