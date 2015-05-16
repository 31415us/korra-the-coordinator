
from math import pi

from molly.Vec2D import Vec2D
from molly.Settings import Settings
from molly.Pathplanner import get_path, ramp_down

from pickit.Joint import Joint
from pickit.Datatypes import JointMinMaxConstraint, TimeToDestination 
class MollyWrapper(object):

    def __init__(self):
        self.settings = Settings()
        max_omega = self.settings.max_v / (2 * pi)
        max_alpha = self.settings.max_acc / (2 * pi)
        self.joint = Joint('rotate', JointMinMaxConstraint(pos_min=-2*pi,
                                                           pos_max=2*pi,
                                                           vel_min=-max_omega,
                                                           vel_max=max_omega,
                                                           acc_min=-max_alpha,
                                                           acc_max=max_alhpa))


    def get_trajectory(robot_state, target, obstacles):
        (x, y, vx, vy, theta, omega) = robot_state

        (pos, heading, speed)= robot_state_to_molly(robot_state)

        if target is None:
            molly_traj = ramp_down(pos, heading, speed, self.settings)

            return molly_traj_to_robot_state_traj(robot_state,
                                                  molly_traj,
                                                  self.settings.time_resolution)

        traj = []
        if speed < 1e-3:
            # when standing still it's probably more efficient to first
            # turn towards the target before starting to move
            vec_to_target = (target - pos)
            target_theta = Vec2D(1, 0).oriented_angle(vec_to_target)
            traj = traj + rotate_robot(robot_state,
                                       target_theta,
                                       self.joint,
                                       self.settings.time_resolution)

        molly_traj = get_path(self.settings,
                              [], # assume no dynamic polygonal obstacles
                              obstacles,
                              pos,
                              heading,
                              speed,
                              target)

        traj = traj + molly_traj_to_robot_state_traj(robot_state,
                                                     molly_traj,
                                                     self.settings.time_resolution)

        return traj



def robot_state_to_molly(robot_state):
    (x, y, vx, vy, theta, omega) = robot_state
    pos = Vec2D(x, y)
    heading = Vec2D(1, 0).rotate(theta)
    speed = Vec2D(vx, vy).length()

    return (pos, heading, speed)

def molly_to_robot_state(molly_point, prev_robot_state, delta_t):
    (pos, vel, acc, _) = molly_point
    (_, _, _, _, prev_theta, prev_omega) = prev_robot_state

    if vel.length() < Vec2D.EPSILON:
        theta = prev_theta + prev_omega * delta_t
        omega = 0.0
    else:
        theta = Vec2D(1, 0).oriented_angle(vel)
        omega = (vel.pox_x * acc.pos_y - vel.pos_y * acc.pos_x)
        omega /= vel.dot(vel)

    return (pos.pos_x,
            pos.pos_y,
            vel.pos_x,
            vel.pos_y,
            theta,
            omega)

def molly_traj_to_robot_state_traj(robot_init_state, molly_traj, delta_t):
    res = []

    prev_state = robot_init_state
    for molly_point in molly_traj:
        state = molly_to_robot_state(molly_point, prev_state, delta_t)
        res.append(state)
        prev_state = state

    return res

def rotate_robot(robot_state,
                 target_heading,
                 joint,
                 delta_t):

    (x, y, vx, vy, theta, omega) = robot_state

    time_to_dest = joint.time_to_destination(theta, omega, target_heading, 0)

    path = joint.get_path(theta, omega, target_heading, 0, time_to_dest.tf, delta_t)

    res = []
    for (t, pos, vel, acc) in path:
        res.append((x, y, vx, vy, pos, vel))

    return res
