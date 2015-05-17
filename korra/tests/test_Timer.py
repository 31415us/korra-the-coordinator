
import unittest
import time
import pykka

from korra.TimerActor import TimerActor

class MockTimeReceiver(pykka.ThreadingActor):

    def __init__(self):
        super(MockTimeReceiver, self).__init__()
        self.timer_event_count = 0

    def on_receive(self, msg):
        if msg.get('cmd') == 'timer_event':
            self.timer_event_count += 1
        else:
            # in this test suite we expect to only receive timer_event 
            # messages
            raise Error()


class TimerTest(unittest.TestCase):

    def setUp(self):
        self.rec = MockTimeReceiver.start()
        self.timer = TimerActor.start(self.rec, 0.1, 'timer_event')

    def tearDown(self):
        pykka.ActorRegistry.stop_all()

    def test_start(self):
        self.assertTrue(not self.timer.proxy().running.get(1.0))
        self.timer.tell({'cmd' : 'start'})
        self.assertTrue(self.timer.proxy().running.get(1.0))

    def test_stop(self):
        self.timer.tell({'cmd' : 'start'})
        self.assertTrue(self.timer.proxy().running.get(1.0))
        self.timer.tell({'cmd' : 'stop'})
        self.assertTrue(not self.timer.proxy().running.get(1.0))

    def test_msg_receive(self):
        "test if some timer_event message has been received by moch receiver"
        self.timer.tell({'cmd' : 'start'})
        time.sleep(0.2) # wait for at least 1 timer_event to happen
        self.timer.tell({'cmd' : 'stop'})
        self.assertTrue(self.rec.proxy().timer_event_count.get(1.0) > 0)
