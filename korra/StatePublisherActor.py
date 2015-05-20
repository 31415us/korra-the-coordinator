
import pykka
import time

from cvra_actuatorpub.trajectory_publisher import SimpleRPCActuatorPublisher, \
                                                  WheelbaseTrajectoryPoint, \
                                                  WheelbaseTrajectory

class StatePublisherActor(pykka.ThreadingActor):

    def __init__(self, receiver):
        super(StatePublisherActor, self).__init__()
        self.publisher = SimpleRPCActuatorPublisher(receiver)

    def on_receive(self, msg):
        cmd = msg.get('cmd')
        if cmd == 'molly':
            tm = msg.get('time')
            delta_t = msg.get('dt')
            traj = msg.get('traj')
            wheelbase_points = [WheelbaseTrajectoryPoint(x, y, v, th, om) for (x, y, v, th, om) in traj]

            wheelbase_traj = WheelbaseTrajectory(tm, delta_t, wheelbase_points)

            self.publisher.update_actuator('molly', wheelbase_traj)

        elif cmd == 'publish':
            self.publisher.publish(time.time())

    def get_state(self, name, tm):
        return self.publisher.get_state(name, tm)
