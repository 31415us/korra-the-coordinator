import pykka
import logging

from korra.TimerActor import TimerActor


class KorraActor(pykka.ThreadingActor):
    def __init__(self, state_pub, env, molly, right_arm, left_arm):
        super(KorraActor, self).__init__()
        self.state_pub = state_pub
        self.env = env
        self.molly = molly
        self.right_arm = right_arm
        self.left_arm = left_arm

    def on_receive(self, msg):
        cmd = msg.get('cmd')
        logging.debug('KorraActor received command: {}'.format(cmd))

        try:
            if cmd == 'molly_timer':
                self.molly.tell({'cmd': 'send_traj'})
            elif cmd == 'publish_timer':
                self.state_pub.tell({'cmd': 'publish'})
            elif cmd == 'molly_target':
                target = msg.get('target')
                nmsg = {
                    'cmd': 'update_target',
                    'target': target,
                    'planner': 'molly'
                }
                self.env.tell(nmsg)
                self.molly.tell({'cmd': 'send_traj'})
            elif cmd == 'right_arm_target':
                target = msg.get('target')
                nmsg = {
                    'cmd': 'update_target',
                    'target': target,
                    'planner': 'right_arm'
                }
                self.env.tell(nmsg)
                self.right_arm.tell({'cmd': 'send_right_arm_traj'})
            elif cmd == 'left_arm_target':
                target = msg.get('target')
                nmsg = {
                    'cmd': 'update_target',
                    'target': target,
                    'planner': 'left_arm'
                }
                self.env.tell(nmsg)
                self.left_arm.tell({'cmd': 'send_left_arm_traj'})
            elif cmd == 'ramp_down':
                nmsg = {
                    'cmd': 'update_target',
                    'target': None,
                    'planner': 'molly'
                }
                self.env.tell(nmsg)
                self.molly.tell({'cmd': 'send_traj'})

                nmsg = {
                    'cmd': 'update_target',
                    'target': None,
                    'planner': 'right_arm'
                }
                self.env.tell(nmsg)
                self.right_arm.tell({'cmd': 'send_right_arm_traj'})

                nmsg = {
                    'cmd': 'update_target',
                    'target': None,
                    'planner': 'left_arm'
                }
                self.env.tell(nmsg)
                self.left_arm.tell({'cmd': 'send_left_arm_traj'})
        except Exception:
            logging.exception('korra crash')
