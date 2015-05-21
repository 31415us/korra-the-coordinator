import pykka
import time
import logging

from molly.Vec2D import Vec2D
from molly.Circle import Circle

from korra.Utils import MollyWrapper


class MollyActor(pykka.ThreadingActor):
    def __init__(self, state_publisher, environment, estimated_delay,
                 obstacle_radius):
        super(MollyActor, self).__init__()
        self.estimated_delay = estimated_delay
        self.state_publisher = state_publisher
        self.environment = environment
        self.obstacle_radius = obstacle_radius
        self.molly_wrapper = MollyWrapper()

    def on_receive(self, msg):
        cmd = msg.get('cmd')
        logging.debug('MollyActor received command {}'.format(cmd))
        try:
            if cmd == 'send_traj':
                self.send_new_traj()
            elif cmd == 'init':
                init_state = msg.get('robot_state')
                nmsg = {
                    'cmd': 'molly',
                    'dt': self.molly_wrapper.settings.time_resolution,
                    'time': time.time(),
                    'traj': [init_state]
                }
                self.state_publisher.tell(nmsg)
        except Exception:
            logging.exception("molly crashed")

    def send_new_traj(self):
        now = time.time()
        state_proxy = self.state_publisher.proxy()
        env_proxy = self.environment.proxy()

        robot_state = state_proxy.get_state('molly',
                                            now + self.estimated_delay).get()

        target = env_proxy.get_target('molly').get()

        logging.info("Got asked to move from {} to {}".format(
            (robot_state[0], robot_state[1]), target))

        enemy_pos = env_proxy.get_enemies().get()
        friend_pos = env_proxy.get_friend().get()

        obstacles = [Circle(e, self.obstacle_radius) for e in enemy_pos]

        if friend_pos is not None:
            logging.info("Adding friend obstacle at {}".format(friend_pos))
            obstacles.append(Circle(friend_pos, self.obstacle_radius))

        traj = self.molly_wrapper.get_trajectory(robot_state, target,
                                                 obstacles)

        msg = {
            'cmd': 'molly',
            'time': now + self.estimated_delay,
            'traj': traj,
            'dt': self.molly_wrapper.settings.time_resolution
        }

        self.state_publisher.tell(msg)
