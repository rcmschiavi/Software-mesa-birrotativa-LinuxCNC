#!/usr/bin/python
import hal, time

class Machine_control:
    def __init__(self):
        self.h = hal.component("machine_controll")
        self.maxvel_basc = 25 #Graus/s
        self.maxvel_rot = 3
        self.maxAccel_basc = 10 #Graus/s^2
        self.maxAccel_rot = 10
        self.init_pins()
        self.init_params()
        self.roda()

    def init_pins(self):
        self.h.newpin("set_position_basc", hal.HAL_FLOAT, hal.HAL_OUT)
        self.h.newpin("set_position_rot", hal.HAL_FLOAT, hal.HAL_OUT)
        self.h.newpin("enable_basc", hal.HAL_BIT, hal.HAL_OUT)
        self.h.newpin("enable_rot", hal.HAL_BIT, hal.HAL_OUT)
        self.h.newpin("sensor_basc", hal.HAL_BIT, hal.HAL_IN)
        self.h.newpin("sensor_rot", hal.HAL_BIT, hal.HAL_IN)
        self.h.newpin("get_position_basc", hal.HAL_FLOAT, hal.HAL_IN)
        self.h.newpin("get_position_rot", hal.HAL_FLOAT, hal.HAL_IN)

    def init_params(self):
        hal.set_p("stepgen.0.maxvel", self.maxvel_basc) #Precisa ser uma string
        hal.set_p("stepgen.1.maxvel", self.maxvel_rot)
        hal.set_p("stepgen.0.maxaccel", self.maxAccel_basc)
        hal.set_p("stepgen.1.maxaccel", self.maxAccel_rot)

    def setSpeed(self, speed_basc, speed_rot):
        #Lógica para que a velocidade em cada eixo seja equivalente ao movimento
        hal.set_p("stepgen.0.maxvel", speed_basc) #Precisa ser uma string
        hal.set_p("stepgen.1.maxvel", speed_rot)

    def getPosition(self):
        basc_pos = self.h["get_position_basc"]
        rot_pos = self.h["get_position_rot"]
        return [basc_pos,rot_pos]

    def setMachinePos(self,position_basc,position_rot, speed):
        self.h["set_position_basc"] = position_basc
        self.h["set_position_rot"] = position_rot
        return

    def setAxisPos(self,axis,pos,speed):
        #Seria interessante ter a velocidade aqui
        if axis==0:
            self.h["set_position_basc"] = pos
            hal.set_p("stepgen.1.maxvel", speed)
        elif axis==1:
            self.h["set_position_rot"] = pos
            hal.set_p("stepgen.0.maxvel", speed)
        return


    def readSensor(self, i):
        if i==0:
            return self.h["sensor_b"]
        elif i==1:
            return self.h["sensor_c"]
        else:
            return None


MC = Machine_control()


