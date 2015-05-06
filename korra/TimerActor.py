
import pykka
import time

class TimerActor(pykka.ThreadingActor):
    "actor that periodically sends a message to target \
     inspired by: \
     https://github.com/jodal/pykka/issues/24"

    def __init__(self, target, sleep_time):
        super(TimerActor, self).__init__()
        self.target = target
        self.sleep_time = sleep_time
        self.running = False

    def on_receive(self, msg):

        if msg.get('cmd') == 'start':
            self.running = True
            self.trigger()
        elif msg.get('cmd') == 'stop':
            self.running = False
        elif msg.get('cmd') == 'trigger':
            self.trigger()

    def trigger(self):
        if not self.running:
            return
        time.sleep(self.sleep_time)
        self.target.tell({'cmd' : 'timer_event'})
        self.actor_ref.tell({'cmd' : 'trigger'})
