
import pykka

from korra.TimerActor import TimerActor

class KorraActor(pykka.ThreadingActor):

    def __init__(self, state_pub, env, molly):
        super(KorraActor, self).__init__()
        self.state_pub = state_pub
        self.env = env
        self.molly = molly
        self.molly_timer = TimerActor(self, 0.1, 'molly_timer')

    def on_receive(msg):
        cmd = msg.get('cmd')

        if cmd == 'molly_timer':
            self.molly.tell({'cmd' : 'send_traj'})
        elif cmd == 'set_target':
            target = cmd.get('target')
            nmsg = {
                    'cmd' : 'update_target',
                    'target' : target
                    }
            self.env.tell(nmsg)
            self.molly.tell({'cmd' : 'send_traj'})
        elif cmd == 'ramp_down':
            nmsg = {
                    'cmd' : 'update_target',
                    'target' : None
                    }
            self.env.tell(nmsg)
            self.molly.tell({'cmd' : 'send_traj'})


