
import pykka

from cvra_actuatorpub.trajectory_publisher import SimpleRPCActuatorPublisher, \
                                                  WheelbaseTrajectoryPoint, \
                                                  WheelbaseTrajectory

class StatePublisherActor(pykka.ThreadingActor):

    def __init__(self, receiver):
        super(StatePublisherActor, self).__init__()
        self.publisher = SimpleRPCActuatorPublisher(receiver)

    def on_receive(self, msg):
        cmd = msg.get('cmd')
        if cmd == 'base_traj':
            time = msg.get('time')
            delta_t = msg.get('dt')
            traj = msg.get('traj')
            wheelbase_points = [WheelbaseTrajectoryPoint(x, y, v, th, om) for (x, y, v, th, om) in traj]

            wheelbase_traj = WheelbaseTrajectory(time, delta_t, wheelbase_points)

            self.publisher.update_actuator('wheelbase', wheelbase_traj)

    def get_state(self, name, time):
        return self.publisher.get_state(name, time)
