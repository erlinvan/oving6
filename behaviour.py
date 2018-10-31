from time import sleep
import random
import basic_robot.imager2 as IMR
from Sensob import *
from basic_robot.reflectance_sensors import ReflectanceSensors
from basic_robot.camera import Camera
from basic_robot.motors import Motors
from basic_robot.ultrasonic import Ultrasonic
from basic_robot.zumo_button import ZumoButton

class Behavior:
    def __init__(self, bbcon):
        self.initfunc(bbcon)

    def initfunc(self, bbcon):
        self.bbcon = bbcon
        self.sensobs = []
        self.motor_rec = []
        self.active_flag = False
        self.halt_request = False
        self.priority = 1.0
        self.match_degree = 0
        self.weight = 0

    def consider_deactivation(self):
        # When a behavior is active (active_flag = True), the behavior must consider deactivation each timestep
        pass

    def consider_activation(self):
        # When a behavior is inacvtive (active_flag = False), it must consider activation
        pass

    def sense_and_act(self):
        # The core computations that use sensob readings to produce motor recommendations and halt requests
        self.match_degree = something

    def weight_update(self):
        self.weight = self.priority*self.match_degree

    def update(self):
        if self.active_flag:
            self.consider_deactivation()
        else:
            self.consider_activation()
        self.sense_and_act() # Updates the match_degree and motor_rec
        self.weight_update() # Updates the weight

class UV_behavior(Behavior):
    def __init__(self, bbcon):
        self.initfunc(bbcon)
        self.sensobs.append(UV())
        self.active_flag = True
        self.bbcon.active_behaviors.append(self)

    def sense_and_act(self):
        self.sensobs[0].get_value()
        dist = self.sensobs[0].value
        if dist >= 10:
            self.bbcon.camera_activate = False
            self.motor_rec = [('F', 0.4, 0.6)]
            self.match_degree = 0.6
            self.weight_update()
        else:
            self.bbcon.camera_activate = True
            self.motor_rec = [('S', 0, 0)]
            self.match_degree = 0.3
            self.weight_update()

class camera_behavior(Behavior):
    #skrive oppførselen vi vil den skal gjøre her.

    def __init__(self, bbcon):
        self.initfunc(bbcon)
        self.active_flag = True
        self.sensobs.append(CameraSensob())
        self.bbcon.active_behaviors.append(self)

    def consider_deactivation(self):
        if self.bbcon.camera_activate:
            self.active_flag = True
        else:
            self.active_flag = False
            self.bbcon.active_behaviors.pop(self.bbcon.active_behaviors.index(self))

    def consider_activation(self):
        if self.bbcon.camera_activate:
            self.active_flag = True
            if self not in self.bbcon.active_behaviors:
                self.bbcon.active_behaviors.append(self)
        else:
            self.active_flag = False

    def sense_and_act(self):
        if self.active_flag:
            self.consider_deactivation()
        else:
            self.consider_activation()
        if self.active_flag:
            fraction = self.sensobs[0].get_value()
            index = fraction.index(max(fraction))
            if max(fraction) > 0.8:
                if index == 0:      #rød
                    #self.motor_rec = ['L', 0.2, 1.0]
                    self.chaaarge()
                    self.match_degree = 0.5
                    self.weight_update()
                elif index == 1:    #grønn
                    #self.motor_rec = ['R', 0.2, 1.0]
                    self.retreat()
                    self.match_degree = 0.5
                    self.weight_update()
                else:               #blå
                    #self.motor_rec = ['L', 0.5, 1.0]
                    self.turnaround()
                    self.match_degree = 0.5
                    self.weight_update()
            else:
                self.motor_rec = [('B', 0.2, 0.5)]
                self.match_degree = 0.1
                self.weight_update()


    def charge(self):
        self.motor_rec = [('F', 0.7, 1.0)]

    def retreat(self):
        self.motor_rec = [('B', 0.2, 1.0)]

    def turnaround(self):
        self.motor_rec = [('R', 0.5, 1.0), ('F', 0.2, 1.0)]


class proximity_behavior(Behavior):

    def __init__(self, bbcon):
        self.initfunc(bbcon)
        self.sensobs.append(Proximity())
        self.active_flag = True
        self.bbcon.active_behaviors.append(self)

    def sense_and_act(self):
        val = self.sensobs[0].get_value()
        if val[0] == True:
            self.motor_rec = [('R', 0.5, 1.5)]
            self.match_degree = 1
        elif val[1] == True:
            self.motor_rec = [('L', 0.5, 1.5)]
            self.match_degree = 1
        else:
            self.motor_rec = [('S', 0.25, 1)]
            self.match_degree = 0otor_recommendation)
