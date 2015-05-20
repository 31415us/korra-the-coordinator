
import pykka
import time

from korra.StatePublisherActor import StatePublisherActor
from korra.MollyActor import MollyActor
from korra.EnvironmentActor import EnvironmentActor
from korra.KorraActor import KorraActor
from korra.TimerActor import TimerActor

from molly.Vec2D import Vec2D

class Tester(object):

    def __init__(self):
        self.env = EnvironmentActor.start()
        self.state_pub = StatePublisherActor.start(('localhost', 20000))
        self.molly = MollyActor.start(self.state_pub, self.env, 0.1, 0.3)

        self.korra = KorraActor.start(self.state_pub, self.env, self.molly, (1, 1, 0, 0, 0))

        self.molly_timer = TimerActor.start(self.korra, 0.2, 'molly_timer')
        self.pub_timer = TimerActor.start(self.korra, 0.1, 'publish_timer')

    def init_explicit(self, init_state):
        self.molly.tell({'cmd' : 'init', 'robot_state' : init_state})
        time.sleep(0.2)
        self.molly_timer.tell({'cmd' : 'start'})
        self.pub_timer.tell({'cmd' : 'start'})


    def set_target(self, x, y):
        target = Vec2D(x, y)

        msg = {}
        msg['cmd'] = 'molly_target'
        msg['target'] = target

        self.korra.tell(msg)

    def stop(self):
        self.korra.tell({'cmd' : 'ramp_down'})

    def is_alive(self):
        print('env', self.env.is_alive())
        print('state_pub', self.state_pub.is_alive())
        print('molly', self.molly.is_alive())
        print('korra', self.korra.is_alive())

    def shutdown(self):
        pykka.ActorRegistry.stop_all()

if __name__ == "__main__":
    t = Tester()
    t.is_alive()
    t.init_explicit((1, 1, 0, 0, 0))
    t.set_target(2.0, 1.0)
