
import pykka
import time
import unittest

from korra.MollyActor import MollyActor

from molly.Vec2D import Vec2D

class DummyEnv(pykka.ThreadingActor):

    def on_receive(self, msg):
        raise Error()

    def get_target(self):
        return Vec2D(1, 0)

    def get_enemies(self):
        return []

    def get_friend(self):
        return None

class DummyState(pykka.ThreadingActor):

    def __init__(self):
        super(DummyState, self).__init__()
        self.time = None
        self.traj = None

    def on_receive(self, msg):
        if msg.get('cmd') == 'base_traj':
            self.time = msg.get('time')
            self.traj = msg.get('traj')
        else:
            raise Error()

    def get_state(self, time):
        return (0, 0, 0, 0, 0, 0)

    def get_time(self):
        return self.time

    def get_traj(self):
        return self.traj

class MollyActorTest(unittest.TestCase):

    def setUp(self):
        self.dummy_env = DummyEnv.start()
        self.dummy_state = DummyState.start()
        self.molly = MollyActor.start(self.dummy_state, self.dummy_env, 1.0, 1.0)

    def tearDown(self):
        pykka.ActorRegistry.stop_all()

    def test_sendtraj(self):
        msg = {'cmd' : 'send_traj'}

        self.assertTrue(self.dummy_state.proxy().get_time().get() is None)
        self.assertTrue(self.dummy_state.proxy().get_traj().get() is None)

        self.molly.tell(msg)
        time.sleep(0.2) # wait for trajectory computation to finish

        self.assertTrue(self.dummy_state.proxy().get_time().get() is not None)
        self.assertTrue(self.dummy_state.proxy().get_traj().get() is not None)
