
import pykka
import logging

from korra.TimerActor import TimerActor

class KorraActor(pykka.ThreadingActor):

    def __init__(self, state_pub, env, molly, robot_init_state):
        super(KorraActor, self).__init__()
        self.state_pub = state_pub
        self.env = env
        self.molly = molly
        #self.molly.tell({'cmd' : 'init', 'robot_state' : robot_init_state})
        self.molly_future = None

    def on_receive(self, msg):
        cmd = msg.get('cmd')

        try:
            if cmd == 'molly_timer':
                self.molly.tell({'cmd' : 'send_traj'})
            elif cmd == 'publish_timer':
                self.state_pub.tell({'cmd' : 'publish'})
            elif cmd == 'molly_target':
                target = msg.get('target')
                nmsg = {
                        'cmd' : 'update_target',
                        'target' : target,
                        'planner' : 'molly'
                        }
                self.env.tell(nmsg)
                self.molly.tell({'cmd' : 'send_traj'})
            elif cmd == 'ramp_down':
                nmsg = {
                        'cmd' : 'update_target',
                        'target' : None,
                        'planner' : 'molly'
                        }
                self.env.tell(nmsg)
                self.molly.tell({'cmd' : 'send_traj'})
        except Exception as e:
            print('cmd', cmd)
            logging.exception('korra crash')


