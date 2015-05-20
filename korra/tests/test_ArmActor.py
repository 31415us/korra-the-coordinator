import pykka
import time
import unittest

from korra.ArmActor import ArmActor
from pickit.Datatypes import RobotSpacePoint

class DummyEnv(pykka.ThreadingActor):

    def on_receive(self, msg):
        raise Error()

    def get_target(self, name):
        return (RobotSpacePoint(0.2, 0.1, 0, 0),
                RobotSpacePoint(0, 0, 0, 0))

class DummyState(pykka.ThreadingActor):

    def __init__(self):
        super(DummyState, self).__init__()
        self.time = None
        self.traj_z = None
        self.traj_shoulder = None
        self.traj_elbow = None
        self.traj_wrist = None

    def on_receive(self, msg):
        if msg.get('cmd') == 'right_arm_traj':
            self.time = msg.get('time')
            self.traj_z = msg.get('z')
            self.traj_shoulder = msg.get('shoulder')
            self.traj_elbow = msg.get('elbow')
            self.traj_wrist = msg.get('wrist')
        else:
            raise Error()

    def get_state(self, name, time):
        return (0, 0)

    def get_time(self):
        return self.time

    def get_traj_z(self):
        return self.traj_z

    def get_traj_shoulder(self):
        return self.traj_shoulder

    def get_traj_elbow(self):
        return self.traj_elbow

    def get_traj_wrist(self):
        return self.traj_wrist

class ArmActorTest(unittest.TestCase):

    def setUp(self):
        self.dummy_env = DummyEnv.start()
        self.dummy_state = DummyState.start()
        self.arm = ArmActor.start(self.dummy_state, self.dummy_env, 0.5, 'right')

    def tearDown(self):
        pykka.ActorRegistry.stop_all()

    def test_sendtraj(self):
        msg = {'cmd' : 'send_right_arm_traj'}

        self.assertTrue(self.dummy_state.proxy().get_time().get() is None)
        self.assertTrue(self.dummy_state.proxy().get_traj_z().get() is None)
        self.assertTrue(self.dummy_state.proxy().get_traj_shoulder().get() is None)
        self.assertTrue(self.dummy_state.proxy().get_traj_elbow().get() is None)
        self.assertTrue(self.dummy_state.proxy().get_traj_wrist().get() is None)

        self.arm.tell(msg)
        time.sleep(0.2) # wait for trajectory computation to finish

        self.assertTrue(self.dummy_state.proxy().get_time().get() is not None)
        self.assertTrue(self.dummy_state.proxy().get_traj_z().get() is not None)
        self.assertTrue(self.dummy_state.proxy().get_traj_shoulder().get() is not None)
        self.assertTrue(self.dummy_state.proxy().get_traj_elbow().get() is not None)
        self.assertTrue(self.dummy_state.proxy().get_traj_wrist().get() is not None)
