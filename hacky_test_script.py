
import pykka
from time import time, sleep

from korra.StatePublisherActor import StatePublisherActor
from korra.MollyActor import MollyActor
from korra.EnvironmentActor import EnvironmentActor
from korra.KorraActor import KorraActor

from molly.Vec2D import Vec2D

ENV = None
STATE_PUB = None
MOLLY = None
KORRA = None

def initialize(self):

    ENV = EnvironmentActor.start()
    STATE_PUB = StatePublisherActor.start(('localhost', 1337))
    MOLLY = MollyActor.start(STATE_PUB, ENV, 0.1, 0.3)

    KORRA = KorraActor.start(STATE_PUB, ENV, MOLLY, (0, 0, 0, 0, 0))

def set_target(x, y):
    target = Vec2D(x, y)

    msg = {}
    msg['cmd'] = 'molly_target'
    msg['target'] = target

    KORRA.tell(msg)

def stop():
    KORRA.tell({'cmd' : 'ramp_down'})

