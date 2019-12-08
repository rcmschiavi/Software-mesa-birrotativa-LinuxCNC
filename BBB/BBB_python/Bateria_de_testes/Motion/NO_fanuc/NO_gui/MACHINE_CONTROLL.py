#!/usr/bin/python
# coding: utf-8
import hal, time, math

class Machine_control:

    axisBasc = {
        "homeSpeed": 3,
        "homeSpeedFine": 1,
        "axisIndex": 1,
        "homePos": -180
    }
    axisRot = {
        "homeSpeed": 25,
        "homeSpeedFine": 10,
        "axisIndex": 0,
        "homePos": 360
    }

    def __init__(self):
        self.h = hal.component("machine_controll")
        self.maxvel_basc = 3 #Graus/s
        self.maxvel_rot = 25
        self.maxAccel_basc = 10 #Graus/s^2
        self.maxAccel_rot = 10
        self.BASC_AXIS = 1
        self.ROT_AXIS = 0
        self.init_pins()
        self.init_params()

    def init_pins(self):
        self.h.newpin("set_position_basc", hal.HAL_FLOAT, hal.HAL_OUT)
        self.h.newpin("set_position_rot", hal.HAL_FLOAT, hal.HAL_OUT)
        self.h.newpin("enable_basc", hal.HAL_BIT, hal.HAL_OUT)
        self.h.newpin("enable_rot", hal.HAL_BIT, hal.HAL_OUT)
        #Não peguei qual sensor é qual
        self.h.newpin("sensor_basc", hal.HAL_BIT, hal.HAL_IN)
        self.h.newpin("sensor_rot", hal.HAL_BIT, hal.HAL_IN)
        self.h.newpin("get_position_basc", hal.HAL_FLOAT, hal.HAL_IN)
        self.h.newpin("get_position_rot", hal.HAL_FLOAT, hal.HAL_IN)

    def init_params(self):
        hal.set_p("stepgen.0.maxvel", str(self.maxvel_basc)) #Precisa ser uma string
        hal.set_p("stepgen.1.maxvel", str(self.maxvel_rot))
        hal.set_p("stepgen.0.maxaccel", str(self.maxAccel_basc))
        hal.set_p("stepgen.1.maxaccel", str(self.maxAccel_rot))

    def calcSpeed(self,speed,position_basc,position_rot):
        #Lógica para que a velocidade em cada eixo seja equivalente ao movimento
        #A velocidade será calculada com base no tempo do que demoramais executar o movimento
        #A trajetória terá velocidade média igual a velocidade determinada e o movimento mais demorado terá essa velocidade
        pos_i_rot, pos_i_basc = self.getPosition()
        dif_pos_rot = abs(position_rot - pos_i_rot)
        dif_pos_basc = abs(position_basc - pos_i_basc)
        t_rot = dif_pos_rot/speed
        t_basc = dif_pos_basc/speed
        if dif_pos_rot==0:
            return [0, speed]
        elif dif_pos_basc==0:
            return [speed, 0]
        else:
            if t_basc>t_rot:
                #Velocidade de rotação será diminuida
                t_rot = t_basc
                speed_basc = speed
                speed_rot = dif_pos_rot/t_rot
                return [speed_rot, speed_basc]
            else:
                #Velocidade de bascula será diminuida
                t_basc = t_rot
                speed_rot = speed
                speed_basc = dif_pos_basc / t_basc
                return [speed_rot, speed_basc]


    def setSpeed(self, speed_rot, speed_basc):
        hal.set_p("stepgen.0.maxvel", str(speed_basc)) #Precisa ser uma string
        hal.set_p("stepgen.1.maxvel", str(speed_rot))

    def getPosition(self):
        pos_basc = self.h["get_position_basc"]
        pos_rot = self.h["get_position_rot"]
        return [pos_rot,pos_basc]

    def setMachinePos(self,position_rot,position_basc, speed):
        speed_rot, speed_basc = self.calcSpeed(speed, position_basc,position_rot)
        speed_reduction = 0
        if speed_rot>=self.maxvel_rot: speed_basc=self.maxvel_basc

        if speed_basc>=self.maxvel_basc: speed_basc=self.maxvel_basc

        self.setSpeed(speed_rot, speed_basc)
        self.h["set_position_basc"] = position_basc
        self.h["set_position_rot"] = position_rot
        self.h["enable_basc"] = True
        self.h["enable_rot"] = True
        return

    def setAxisPos(self,axis,pos,speed):
        if axis==0:
            self.h["set_position_rot"] = pos
            hal.set_p("stepgen.0.maxvel", str(speed))
        elif axis==1:
            self.h["set_position_basc"] = pos
            hal.set_p("stepgen.1.maxvel", str(speed))
        return

    def stopAxis(self, axis):
        if axis==self.ROT_AXIS:
            self.h["enable_rot"] = False
            self.h["set_position_rot"] = self.h["get_position_rot"]
        elif axis==self.BASC_AXIS:
            self.h["enable_basc"] = False
            self.h["set_position_basc"] = self.h["get_position_basc"]
        return

    def readSensor(self, sensor_number):
        if sensor_number==self.ROT_AXIS:
            return self.h["sensor_rot"]
        elif sensor_number==self.BASC_AXIS:
            return self.h["sensor_basc"]
        else:
            return None

    def isMoving(self):
        # Testa se a posição atual dos steps é igual a posição do count arredondado em 3 casas
        if round(self.h["get_position_rot"], 3) == self.h["set_position_rot"] and round(self.h["get_position_rot"],3) == self.h["set_position_rot"]:
            return False
        else:
            return True



