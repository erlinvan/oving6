import random
from camera import *
from imager2 import *
from motors import *
from irproximity_sensor import *
from reflectance_sensors import *
from ultrasonic import *
from zumo_button import *
from time import sleep

class BBCON:

    def __init__(self):
        self.behaviors = [] #liste med alle behaviors
        self.active_behav = [] #list of active behaviors
        #self.inactive_behaviors = []
        self.sensobs = [] #liste med sensor objekter
        self.motobs = [] #liste med motor objekter
        self.arbitrator = Arbitrator(self, False)
        self.current_timestep = 0
        self.active_camera = False

        self.add_behavior(Approach(self))
        self.add_behavior(camera_behavior(self))
        self.add_behavior(IR_behavior(self))

        for behavior in self.behaviors:
            for sensob in behavior.sensobs:
                if sensob not in self.sensobs:
                    self.add_sensob(sensob)

        self.motobs = [Motob()]

    def add_behavior(self,behavior):
        self.behaviors.append(behavior)

    def add_sensob(self, sensob):
        self.sensobs.append(sensob)

    def activate_behavior(self, behavior): #legger til behavior i active listen
        if behavior not in self.active_behav:
            self.active_behav.append(behavior)

    def deactivate_behavior(self, behavior): #fjerner behavior fra inactive listen
        if behavior in self.active_behav:
            self.active_behav.remove(behavior)


    def run_one_timestep(self):
        for i in range(len(self.sensobs)):
            self.sensobs[i].update()
        for j in range(len(self.behaviors)):
            self.behaviors[j].update()
        self.motobs[0].update(self.arbitrator.choose_action().motor_rec)
        sleep(0.4)
        for sensob in self.sensobs:
            sensob.reset()
















class Arbitrator:

    def __init__(self, bbcon, stochastic):
        self.bbcon = bbcon #skulle ha pointer til bbcon
        self.stochastic = stochastic #boolean som velger om vi velger hoyest vekt eller random

    def choose_action(self):
        if self.stochastic:
            return self.stochastic()
        else:
            return self.highest_weight()

    def highest_weight(self):

        highest = self.bbcon.active_behav[0].weight
        vinner = self.bbcon.active_behav[0]
        for behavior in self.bbcon.active_behav:
            if behavior.weight > highest:
                highest = behavior.weight
                vinner = behavior
        return vinner

    def stochastic(self):

        sum = 0
        behaviors = {}

        #lager liste men intervaller. intervallene til hver behavior er like stpr som vekten, saann at sannsynligheten skal gjenspeiles i dette
        #[0, 0.5], [0.5, 1.3], [1.3, 2]
        for behavior in self.bbcon.active_behav:
            behaviors[behavior] = [sum, sum + behavior.weight]
            sum += behavior.weight

        rand_num = random.uniform(0, sum) #finner random tall
        vinner = None
    #har naa en dictionary med behavior og et tilsvaende intervall, saa henter ut hoyeste verdien i intervallet (value[1]) og sjekker opp mot random
        for behavior, interval in behaviors.items():
            if interval[1] < rand_num:
                vinner = behavior
        return vinner




class Sensob:

    def __init__(self):
        self.sensors = []
        self.value = None

    def update(self): #skal oppdateres en gang hver timestep. Tror det gjores i en annen klasse
        return

    def get_value(self):
        return self.value

    def reset(self):
        for sensor in self.sensors:
            sensor.reset()





class IR(Sensob):

    def __init__(self):
        self.sensors = [IRProximitySensor()]
        self.value = None

    def update(self):
        self.sensors[0].update()
        self.value = self.sensors[0].get_value()


    def get_value(self):
        #True betyr at noe er naert
        return self.value

    def reset(self):
        self.sensors[0].reset()




class LookAhead(Sensob):
    def __init__(self):
        self.sensors = [Ultrasonic()]

    def update(self):
        self.sensors[0].update()
        self.value = self.sensors[0].get_value()


    def get_value(self): #trenger jeg aa lage denne naar den arver?
        return self.value

    def reset(self):
        self.sensors[0].reset()








class CameraSensob(Sensob):

    def __init__(self, threshold=0.4, CR=(0.5, 0.25, 0, 0.25)):
        self.threshold = threshold  #tillatter saasaa mye slingringsmonn
        self.CR = CR  # cutratio, hvor mye av bilde som skal kuttes for analyseringa
        self.sensors = [Camera()]
        self.value = []


    def update(self): #tar bilde med Camera og analyserer fargeverdiene.
        image = self.sensors[0].update() #henter fra Camera
        width, height = image.size

        def wta(p): #get largest pixel, p er en RGB tuppel
            #x = max(p) #henter ut hvilken som har hoyest verdi
            liste = list(p) #gjor den om til en liste
            #print(liste)
            index = liste.index(max(p))
            rgb = [0,0,0]
            #Setter den korrekte til max og de andre til 0
            rgb[index] = 255
            return tuple(rgb) #maa vaere en tuppel, ikke en liste


        for h in range(height):
            for w in range(width):
                p = image.getpixel((w,h))
                pwta = wta(p)
                image.putpixel((w,h), pwta)
        #teller hvor mange vi har av hver farge
        color_count = [0, 0, 0]
        for h in range(height):
            for w in range(width):
                pixel = list(image.getpixel((w,h)))
                color_count[pixel.index(255)] +=1 #legger til 1 paa der det er 255 i pixel
        #maa endre det til hvor mye av det totale bildet det er
        of_total = [0.0, 0.0, 0.0]
        for i in range(len(color_count)):
            total = width*height
            of_total[i] = color_count[i]/total
        self.value = of_total


    def get_value(self):
        return self.value

    def reset(self):
        self.sensors[0].reset()













class Behavior:

    # priority = static predefined value

    def __init__(self, bbcon):
        self.bbcon = bbcon #pointer to controller that uses this behaviour
        self.sensobs = [] #list of sensobs this behavour uses
        self.motor_rec = []
        self.active_flag = False
        self.halt_request = False
        self.priority = 1.0
        self.match_degree = 0 #et tall som sier noen om hvor mye de naavaerende tilstandene garanterer behavioren
        self.weight = self.priority * self.match_degree

    def consider_deactivation(self):
        pass

    def consider_activation(self):
        pass

    def update(self):
        if self.active_flag:
            self.consider_deactivation()
        else:
            self.consider_activation()
        self.sense_and_act()
        self.update_weight()

    def sense_and_act(self): #calculate
        pass

    def update_weight(self):
        self.weight=self.priority * self.match_degree



class Approach(Behavior): #UV-behaviour
    def __init__(self, bbcon):
        super(bbcon).__init__()
        self.sensobs.append(LookAhead()) #UV
        self.active_flag=True
        self.bbcon.active_behav.append(self)


    def sense_and_act(self):

        distance=self.sensobs[0].get_value() #hvorfor to linjer?
        if distance >= 10:
            self.bbcon.active_camera = True
            self.match_degree=0.6
            self.motor_rec = [("F", 0.4, 0.6)]
            self.update_weight()
            print("kjor")
        else:
            self.bbcon.active_camera = False
            self.match_degree = 0.3
            self.motor_rec = [("S", 0, 0)]
            self.update_weight()
            print("stopp")

class camera_behavior(Behavior):

    def __init__(self, bbcon):
        super().__init__(bbcon)
        self.active_flag=True
        self.bbcon.active_behav.append(self)
        self.sensobs.append(CameraSensob())

    def concider_deactivation(self):
        if (self.bbcon.active_camera):
            self.active_flag=True
        else:
            self.active_flag=False
            index=self.bbcon.active_behav.index(self)
            self.bbcon.active_behav.pop(index)

    def consider_activation(self):
        if self.bbcon.active_camera:
            self.active_flag=True
            if self not in self.bbcon.active_behav:#trengs denne og neste linje
                self.bbcon.active_behav.append(self)
        else:
            self.active_flag=False

    def sense_and_act(self):
        if self.active_flag:
            self.concider_deactivation()
        else:
            self.consider_activation()

        if self.active_flag:
            piece=self.sensobs[0].get_value()
            index = piece.index(max(piece))
            if index==0: #red
                #print("ROD")
                #self.forward()
                self.match_degree = 0.5
                self.update_weight()
            elif index == 1:  # green
                print("GRONN")
                # self.motor_rec = [('R', 0.2, 1.0)]
                self.pull_back
                self.match_degree = 1.0
                self.update_weight()
            else:  # blue
                print("BLA")
                # self.motor_rec = [('L', 0.5, 1.0)]
                #self.turn
                self.match_degree = 1.0
                self.update_weight()
        else:
            self.motor_rec = [('B', 0.2, 0.5)]
            self.match_degree = 0.1
            self.update_weight()

    def forward(self):
        self.motor_rec = [("F", 0.7,1.0)]

    def pull_back(self):
        self.motor_rec = [('B', 0.2, 1.0)]

    def turn(self):
        self.motor_rec = [('R', 0.5, 1.0), ('F', 0.2, 1.0)]






class IR_behavior(Behavior):

    def __init__(self, bbcon):
        super().__init__(bbcon)
        self.sensobs.append(IR())
        self.active_flag=True
        self.bbcon.active_behav.append(self)

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
            self.match_degree = 0





class Motob:
    def __init__(self):
        self.motors = [Motors()]
        self.value = None

    def update(self, vals):
        self.value = vals
        self.operationalize()

    def operationalize(self):# convert motor reccomantation into one or more motor settings
        for i in range (len(self.value)):
            if (self.value[i][0] == "F" or self.value[i][0] == "f"):
                self.motors[0].forward(self.value[i][1], self.value[i][2])
            elif (self.value[i][0] == "B" or self.value[i][0]=="b"):
                self.motors[0].backward(self.value[i][1], self.value[i][2])
            elif (self.value[i][0] == "R" or self.value[i][0] == "r"):
                self.motors[0].right(self.value[i][1], self.value[i][2])
            elif (self.value[i][0] == "L" or self.value[i][0]=="l"):
                self.motors[0].left(self.value[i][1], self.value[i][2])
            elif (self.value[i][0]=="S" or self.value[i][0]=="s"):
                self.motors[0].stop()
            else:
                print("Something wrong")









def main():
    bbcon = BBCON()
    x = False
    ZumoButton().wait_for_press()
    while x == False:
        bbcon.run_one_timestep()


if __name__ == '__main__':
    main()
