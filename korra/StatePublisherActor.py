import pykka
import time
import logging

from decimal import Decimal

from cvra_actuatorpub.trajectory_publisher import SimpleRPCActuatorPublisher, \
                                                  WheelbaseTrajectoryPoint, \
                                                  WheelbaseTrajectory, \
                                                  TrajectoryPoint, \
                                                  Trajectory


class StatePublisherActor(pykka.ThreadingActor):
    def __init__(self, receiver):
        super(StatePublisherActor, self).__init__()
        self.publisher = SimpleRPCActuatorPublisher(receiver)

    def on_receive(self, msg):
        cmd = msg.get('cmd')
        print(cmd)
        try:
            if cmd == 'molly':
                tm = msg.get('time')
                delta_t = msg.get('dt')
                traj = msg.get('traj')
                wheelbase_points = [WheelbaseTrajectoryPoint(x, y, v, th, om)
                                    for (x, y, v, th, om) in traj]

                milliseconds = int(delta_t * 1000)

                dt = Decimal(int(milliseconds // 1000)) + Decimal(
                    milliseconds % 1000) / Decimal(1000)

                wheelbase_traj = WheelbaseTrajectory(tm, dt, wheelbase_points)

                self.publisher.update_actuator('molly', wheelbase_traj)

            elif cmd == 'right_arm_traj':
                tm = msg.get('time')
                delta_t = msg.get('dt')
                traj_z = msg.get('z')
                traj_shoulder = msg.get('shoulder')
                traj_elbow = msg.get('elbow')
                traj_wrist = msg.get('wrist')

                points_z = [TrajectoryPoint(pos, vel, acc, trq)
                            for (pos, vel, acc, trq) in traj_z]
                points_shoulder = [TrajectoryPoint(pos, vel, acc, trq)
                                   for (pos, vel, acc, trq) in traj_shoulder]
                points_elbow = [TrajectoryPoint(pos, vel, acc, trq)
                                for (pos, vel, acc, trq) in traj_elbow]
                points_wrist = [TrajectoryPoint(pos, vel, acc, trq)
                                for (pos, vel, acc, trq) in traj_wrist]

                milliseconds = int(delta_t * 1000)
                dt = Decimal(int(milliseconds // 1000)) + Decimal(
                    milliseconds % 1000) / Decimal(1000)

                self.publisher.update_actuator('right-z', Trajectory(tm, dt,
                                                                     points_z))
                self.publisher.update_actuator(
                    'right-shoulder', Trajectory(tm, dt, points_shoulder))
                self.publisher.update_actuator(
                    'right-elbow', Trajectory(tm, dt, points_elbow))
                self.publisher.update_actuator(
                    'right-wrist', Trajectory(tm, dt, points_wrist))

            elif cmd == 'left_arm_traj':
                tm = msg.get('time')
                delta_t = msg.get('dt')
                traj_z = msg.get('z')
                traj_shoulder = msg.get('shoulder')
                traj_elbow = msg.get('elbow')
                traj_wrist = msg.get('wrist')

                points_z = [TrajectoryPoint(pos, vel, acc, trq)
                            for (pos, vel, acc, trq) in traj_z]
                points_shoulder = [TrajectoryPoint(pos, vel, acc, trq)
                                   for (pos, vel, acc, trq) in traj_shoulder]
                points_elbow = [TrajectoryPoint(pos, vel, acc, trq)
                                for (pos, vel, acc, trq) in traj_elbow]
                points_wrist = [TrajectoryPoint(pos, vel, acc, trq)
                                for (pos, vel, acc, trq) in traj_wrist]

                milliseconds = int(delta_t * 1000)
                dt = Decimal(int(milliseconds // 1000)) + Decimal(
                    milliseconds % 1000) / Decimal(1000)

                self.publisher.update_actuator('left-z', Trajectory(tm, dt,
                                                                    points_z))
                self.publisher.update_actuator(
                    'left-shoulder', Trajectory(tm, dt, points_shoulder))
                self.publisher.update_actuator(
                    'left-elbow', Trajectory(tm, dt, points_elbow))
                self.publisher.update_actuator(
                    'left-wrist', Trajectory(tm, dt, points_wrist))

            elif cmd == 'publish':
                self.publisher.publish(time.time())
        except Exception as e:
            print('cmd', cmd)
            logging.exception("StatePublisher crash")

    def get_state(self, name, tm):
        return self.publisher.get_state(name, tm)
