
import pykka
import time

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
                init_state = msg.get(self.flip + '_arm_state')
                msg = {
                       'cmd' : self.flip + '_arm_traj',
                       'time' : now,
                       'dt': self.arm.arm.dt,
                       'z' : [init_state(0)],
                       'shoulder' : [init_state(1)],
                       'elbow' : [init_state(2)],
                       'wrist' : [init_state(3)]
                       }
                self.state_publisher.tell(nmsg)
        except Exception as e:
            print(cmd)
            logging.exception(self.flip + " arm crashed")

    def send_new_traj(self):
        now = time.time()
        state = self.get_arm_state(now + self.estimated_delay) # state is pos & vel JointSpacePoint

        env_proxy = self.environment.proxy()
        target = env_proxy.get_target(self.flip+'-arm').get() # target is pos & vel RobotSpacePoint

        z, shoulder, elbow, wrist = self.arm.goto(state, target)

        msg = {
                'cmd' : self.flip + '_arm_traj',
                'time' : now + self.estimated_delay,
                'dt': self.arm.arm.dt,
                'z' : z,
                'shoulder' : shoulder,
                'elbow' : elbow,
                'wrist' : wrist
               }

        self.state_publisher.tell(msg)

    def get_arm_state(self, time):
        state_proxy = self.state_publisher.proxy()

        z_state = state_proxy.get_state(self.flip+'-z', time).get()
        shoulder_state = state_proxy.get_state(self.flip+'-shoulder', time).get()
        elbow_state = state_proxy.get_state(self.flip+'-elbow', time).get()
        wrist_state = state_proxy.get_state(self.flip+'-wrist', time).get()

        return joint_states_to_arm(z_state, shoulder_state, elbow_state, wrist_state)
