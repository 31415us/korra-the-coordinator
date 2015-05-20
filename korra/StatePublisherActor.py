
import pykka
import time
import logging

from decimal import Decimal

from cvra_actuatorpub.trajectory_publisher import SimpleRPCActuatorPublisher, \
                                                  WheelbaseTrajectoryPoint, \
                                                  WheelbaseTrajectory

class StatePublisherActor(pykka.ThreadingActor):

    def __init__(self, receiver):
        super(StatePublisherActor, self).__init__()
        self.publisher = SimpleRPCActuatorPublisher(receiver)

    def on_receive(self, msg):
        cmd = msg.get('cmd')
        try:
            if cmd == 'molly':
                tm = msg.get('time')
                delta_t = msg.get('dt')
                traj = msg.get('traj')
                wheelbase_points = [WheelbaseTrajectoryPoint(x, y, v, th, om) for (x, y, v, th, om) in traj]

                print(len(wheelbase_points))

                milliseconds = int(delta_t * 1000)

                dt = Decimal(int(milliseconds // 1000)) + Decimal(milliseconds % 1000) / Decimal(1000)

                wheelbase_traj = WheelbaseTrajectory(tm, dt, wheelbase_points)

                self.publisher.update_actuator('molly', wheelbase_traj)

            elif cmd == 'publish':
                    self.publisher.publish(time.time())
        except Exception as e:
            print('cmd', cmd)
            logging.exception("StatePublisher crash")

    def get_state(self, name, tm):
        return self.publisher.get_state(name, tm)
