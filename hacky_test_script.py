import pykka
import time

from korra.StatePublisherActor import StatePublisherActor
from korra.MollyActor import MollyActor
from korra.ArmActor import ArmActor
from korra.EnvironmentActor import EnvironmentActor
from korra.KorraActor import KorraActor
from korra.TimerActor import TimerActor

from molly.Vec2D import Vec2D
from pickit.Datatypes import RobotSpacePoint


class Tester(object):
    def __init__(self):
        self.env = EnvironmentActor.start()
        self.state_pub = StatePublisherActor.start(('localhost', 20000))
        self.molly = MollyActor.start(self.state_pub, self.env, 0.1, 0.3)
        self.right_arm = ArmActor.start(self.state_pub, self.env, 0.1, 'right')
        self.left_arm = ArmActor.start(self.state_pub, self.env, 0.1, 'left')

        self.korra = KorraActor.start(self.state_pub, self.env, self.molly,
                                      self.right_arm, self.left_arm)

        self.molly_timer = TimerActor.start(self.korra, 0.2, 'molly_timer')
        self.pub_timer = TimerActor.start(self.korra, 0.1, 'publish_timer')

    def init_explicit(self, init_state):
        self.molly.tell({'cmd': 'init', 'robot_state': init_state})
        self.right_arm.tell({
            'cmd': 'init',
            'right_shoulder_state': (0, 0),
            'right_elbow_state': (0, 0),
            'right_wrist_state': (0, 0),
            'right_z_state': (0, 0),
        })
        self.left_arm.tell({
            'cmd': 'init',
            'left_shoulder_state': (0, 0),
            'left_elbow_state': (0, 0),
            'left_wrist_state': (0, 0),
            'left_z_state': (0, 0),
        })
        time.sleep(0.2)
        self.molly_timer.tell({'cmd': 'start'})
        self.pub_timer.tell({'cmd': 'start'})

    def set_target(self, x, y):
        target = Vec2D(x, y)

        msg = {}
        msg['cmd'] = 'molly_target'
        msg['target'] = target

        self.korra.tell(msg)

    def set_arm_target(self, flip, x, y, z, gripper_heading):
        target_pos = RobotSpacePoint(x, y, z, gripper_heading)
        target_vel = RobotSpacePoint(0, 0, 0, 0)

        target = (target_pos, target_vel)

        msg = {}
        msg['cmd'] = flip + '_arm_target'
        msg['target'] = target

        self.korra.tell(msg)

    def stop(self):
        self.korra.tell({'cmd': 'ramp_down'})

    def is_alive(self):
        print('env', self.env.is_alive())
        print('state_pub', self.state_pub.is_alive())
        print('molly', self.molly.is_alive())
        print('right_arm', self.right_arm.is_alive())
        print('left_arm', self.left_arm.is_alive())
        print('korra', self.korra.is_alive())

    def shutdown(self):
        pykka.ActorRegistry.stop_all()


if __name__ == "__main__":
    t = Tester()
    t.is_alive()
    t.init_explicit((1, 1, 0, 0, 0))
    t.is_alive()
    # t.set_target(2.0, 1.0)
    t.set_arm_target('right', 0.2, 0.1, 0, 0)
