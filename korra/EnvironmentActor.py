
import pykka
import time

class EnvironmentActor(pykka.ThreadingActor):

    def __init__(self, init_pos, init_heading, time_resolution):
        super(EnvironmentActor, self).__init__()

        # robot current target
        self.planner_targets = {}

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
        elif command == 'update_target':
            planner_name = msg.get('planner')
            target = msg.get('target')
            self.planner_targets[planner_name] = target
        
    def get_enemies(self):
        res = []
        if self.enemy1 is not None:
            res.append(self.enemy1)
        if self.enemy2 is not None:
            res.append(self.enemy2)
        return res

    def get_friend(self):
        return self.friend

    def get_target(self, planner_name):
        return self.planner_targets.get(planner_name)

