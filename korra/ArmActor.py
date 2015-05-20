import pykka
import time
import logging

from pickit.Datatypes import *
from pickit import ArmManager

from korra.ArmUtils import ArmWrapper, joint_states_to_arm


class ArmActor(pykka.ThreadingActor):
    def __init__(self, state_publisher, environment, estimated_delay, flip):
        super(ArmActor, self).__init__()
        self.estimated_delay = estimated_delay
        self.state_publisher = state_publisher
        self.environment = environment
        self.flip = flip

        # Get initial state of arm to initialise Arm
        now = time.time()
        q0 = JointSpacePoint(0.0, 0.0, 0.0, 0.0)
        self.arm = ArmWrapper(q0, flip)

    def on_receive(self, msg):
        cmd = msg.get('cmd')
        try:
            if cmd == 'send_' + self.flip + '_arm_traj':
                self.send_new_traj()
            elif cmd == 'init':
                now = time.time()
                init_z = msg.get(self.flip + '_z_state')
                init_shoulder = msg.get(self.flip + '_shoulder_state')
                init_elbow = msg.get(self.flip + '_elbow_state')
                init_wrist = msg.get(self.flip + '_wrist_state')
                nmsg = {
                    'cmd': self.flip + '_arm_traj',
                    'time': now,
                    'dt': self.arm.arm.dt,
                    'z': [(init_z[0], init_z[1], 0, 0)],
                    'shoulder': [(init_shoulder[0], init_shoulder[1], 0, 0)],
                    'elbow': [(init_elbow[0], init_elbow[1], 0, 0)],
                    'wrist': [(init_wrist[0], init_wrist[1], 0, 0)]
                }
                self.state_publisher.tell(nmsg)
        except Exception as e:
            print(cmd)
            logging.exception(self.flip + " arm crashed")

    def send_new_traj(self):
        now = time.time()
        state = self.get_arm_state(now + self.estimated_delay
                                   )  # state is pos & vel JointSpacePoint

        env_proxy = self.environment.proxy()
        target = env_proxy.get_target(self.flip + '_arm').get(
        )  # target is pos & vel RobotSpacePoint

        print(target)

        z, shoulder, elbow, wrist = self.arm.goto(state, target)

        msg = {
            'cmd': self.flip + '_arm_traj',
            'time': now + self.estimated_delay,
            'dt': self.arm.arm.dt,
            'z': z,
            'shoulder': shoulder,
            'elbow': elbow,
            'wrist': wrist
        }

        self.state_publisher.tell(msg)

    def get_arm_state(self, time):
        state_proxy = self.state_publisher.proxy()

        z_state = state_proxy.get_state(self.flip + '-z', time).get()
        shoulder_state = state_proxy.get_state(self.flip + '-shoulder',
                                               time).get()
        elbow_state = state_proxy.get_state(self.flip + '-elbow', time).get()
        wrist_state = state_proxy.get_state(self.flip + '-wrist', time).get()

        return joint_states_to_arm(z_state, shoulder_state, elbow_state,
                                   wrist_state)
