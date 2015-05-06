
import pykka
import time

class EnvironmentActor(pykka.ThreadingActor):

    def __init__(self, init_pos, init_heading, time_resolution):
        super(EnvironmentActor, self).__init__()

        self.time_res = time_resolution

        # robot state
        self.robot_pos = init_pos
        self.robot_heading = init_heading
        self.robot_speed = 0.0

        # robot current target
        self.target_pos = None

        # trajectory
        self.trajectory = []
        self.traj_base_time = time.time()

        # enemy pos
        self.enemy1 = None
        self.enemy2 = None

        # friend pos
        self.friend = None

    def on_receive(self, msg):
        command = msg.get('cmd')

        if command == 'update_friend':
            self.friend = msg.get('friend')
        elif command == 'update_enemy':
            (pos, e_id) = msg.get('enemy')
            if e_id == 1:
                self.enemy1 = pos
            elif e_id == 2:
                self.enemy2 = pos
        elif command == 'update_traj':
            (base_time, traj) = msg.get('traj')
            self.trajectory = traj
            self.traj_base_time = base_time
        elif command == 'update_target':
            self.target_pos = msg.get('target')
        
    def get_enemies(self):
        res = []
        if self.enemy1 is not None:
            res.append(self.enemy1)
        if self.enemy2 is not None:
            res.append(self.enemy2)
        return res

    def get_friend(self):
        return self.friend

    def get_robot_state(self, time_offset):
        if not self._update_pos().get():
            # invalid state
            return None

        if not self.trajectory:
            return (self.robot_pos,
                    self.robot_heading,
                    self.robot_speed,
                    time.time() + time_offset)

        now = time.time()
        future = (now - self.traj_base_time) / self.time_res

        if future < len(self.trajectory):
            (pos, speed, acc, t) = self.trajectory[future]
        else:
            (pos, speed, acc, t) = self.trajectory[-1]

        return (pos, speed.normalized(), speed.length(), now + t)

    def _update_pos(self):
        now = time.time()
        to_drop = (now - self.traj_base_time) / self.time_res
        new_traj = self.trajectory[to_drop:]

        if new_traj:
            self.trajectory = new_traj
            self.traj_base_time = now
            return True

        (last_pos, last_speed, last_acc, _) = self.trajectory[-1]

        if last_speed.length() > 0:
            # enter invalid state
            self.robot_pos = last_pos
            self.robot_heading = last_speed.normalized()
            self.robot_speed = last_speed.length()
            return False

        (_, prev_speed, _, _) = self.trajectory[-2]

        # approximate heading by second to last velocity vector
        self.robot_pos = last_pos
        self.robot_heading = prev_speed.normalized()
        self.robot_speed = 0.0

        self.trajectory = []
        self.traj_base_time = now

        return True



