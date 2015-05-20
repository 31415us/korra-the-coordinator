
import pykka
from time import time, sleep

from korra.StatePublisherActor import StatePublisherActor
from korra.MollyActor import MollyActor
from korra.EnvironmentActor import EnvironmentActor
from korra.KorraActor import KorraActor

from molly.Vec2D import Vec2D

class Tester(object):

    def __init__(self):
        self.env = EnvironmentActor.start()
        self.state_pub = StatePublisherActor.start(('localhost', 20000))
        self.molly = MollyActor.start(self.state_pub, self.env, 0.1, 0.3)

        self.korra = KorraActor.start(self.state_pub, self.env, self.molly, (1, 1, 0, 0, 0))


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
