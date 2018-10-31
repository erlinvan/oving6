import random
from Sensob import *
from arbitrator import *
from behavior import *
from Wheels import *
import basic_robot.imager2 as IMR
from basic_robot.reflectance_sensors import ReflectanceSensors
from basic_robot.camera import Camera
from basic_robot.motors import Motors
from basic_robot.ultrasonic import Ultrasonic
from basic_robot.zumo_button import ZumoButton
from time import sleep

class BBCON:
    def __init__(self):
        self.behaviors = []
        self.active_behaviors = []
        self.inactive_behaviors = []
        self.sensobs = []
        self.motobs = []
        self.current_timestep = 0
        self.arbitrator = Arbitrator(self, False)
        self.camera_activate = False

        # Adds all behaviors to the BBCON
        self.add_behavior(UV_behavior(self))
        self.add_behavior(camera_behavior(self))
        self.add_behavior(proximity_behavior(self))

        # Adds all the sensobs used by the behaviors to the BBCON
        for behavior in self.behaviors:
            for sensob in behavior.sensobs:
                if sensob not in self.sensobs:
                    self.add_sensob(sensob)

        # Adds motob
        self.motobs = [Wheels()]

    def add_behavior(self, behavior):
        self.behaviors.append(behavior)

    def add_sensob(self, sensob):
        self.sensobs.append(sensob)

    def activate_behavior(self, behavior):
        if behavior not in self.active_behaviors:
            self.active_behaviors.append(behavior)

    def deactivate_behavior(self, behavior):
        if behavior in self.active_behaviors:
            self.active_behaviors.pop(behavior)

    def run_one_timestep(self):
        for i in range(len(self.sensobs)):
            self.sensobs[i].update()
        for j in range(len(self.behaviors)):
            self.behaviors[j].update()
        self.motobs[0].update(self.arbitrator.choose_action().motor_rec)
        sleep(0.4)
        for sensob in self.sensobs:
            sensob.reset()

def main():
    bbcon = BBCON()
    x = False
    ZumoButton().wait_for_press()
    while   x == False:
        bbcon.run_one_timestep()
        print(bbcon.active_behaviors)

if __name__ == '__main__':
    main()
