
import pykka
import time

from molly.Vec2D import Vec2D
from molly.Circle import Circle

from korra.Utils import MollyWrapper

class MollyActor(pykka.ThreadingActor):

    def __init__(self, state_publisher, environment, estimated_delay, obstacle_radius):
        super(MollyActor, self).__init__()
        self.estimated_delay = estimated_delay
        self.state_publisher = state_publisher
        self.environment = environment
        self.obstacle_radius = obstacle_radius
        self.molly_wrapper = MollyWrapper()

    def on_receive(self, msg):
        if msg.get('cmd') == 'send_traj':
            self.send_new_traj()

    def send_new_traj(self):
        now = time.time()
        state_proxy = self.state_publisher.proxy()
        env_proxy = self.environment.proxy()

        robot_state = state_proxy.get_state(now + self.estimated_delay).get()
        target = env_proxy.get_target().get()

        enemy_pos = env_proxy.get_enemies().get()
        friend_pos = env_proxy.get_friend().get()

        obstacles = [Circle(e, self.obstacle_radius) for e in enemy_pos]
        if not friend_pos is None:
            obstacles.append(Cricle(friend_pos, self.obstacle_radius))

        traj = self.molly_wrapper.get_trajectory(robot_state, target, obstacles)

        msg = {
                'cmd' : 'base_traj',
                'time' : now + self.estimated_delay,
                'traj' : traj
               }

        self.state_publisher.tell(msg)


