#!/usr/bin/python
import hal, time

class Machine_control:
    def __init__(self):
        self.h = hal.component("machine_controll")
        self.init_pins()
        self.roda()

    def init_pins(self):
        self.h.newpin("set_position_b", hal.HAL_FLOAT, hal.HAL_OUT)
        self.h.newpin("set_position_c", hal.HAL_FLOAT, hal.HAL_OUT)
        '''
        Não é possível alterar o parametro, devemos definir uma velocidade máxima e enviar a posição de modo 
        a gerar a velocidade
        self.h.newpin("set_speed_b", hal.HAL_FLOAT, hal.HAL_OUT)
        self.h.newpin("set_speed_c", hal.HAL_FLOAT, hal.HAL_OUT)
        self.h.newpin("set_accel_b", hal.HAL_FLOAT, hal.HAL_OUT)
        self.h.newpin("set_accel_c", hal.HAL_FLOAT, hal.HAL_OUT)
        '''
        self.h.newpin("dir_b", hal.HAL_BIT, hal.HAL_OUT)
        self.h.newpin("dir_c", hal.HAL_BIT, hal.HAL_OUT)
        self.h.newpin("enable_b", hal.HAL_BIT, hal.HAL_OUT)
        self.h.newpin("enable_c", hal.HAL_BIT, hal.HAL_OUT)
        self.h.newpin("sensor_b", hal.HAL_BIT, hal.HAL_IN)
        self.h.newpin("sensor_c", hal.HAL_BIT, hal.HAL_IN)
        self.h.newpin("get_position_b", hal.HAL_FLOAT, hal.HAL_IN)
        self.h.newpin("get_position_c", hal.HAL_FLOAT, hal.HAL_IN)

    def init_params(self):

        hal.set_p("stepgen.0.maxvel", "25") #Precisa ser uma string
        hal.set_p("stepgen.1.maxvel", "3")
        hal.set_p("stepgen.0.maxaccel", "10")
        hal.set_p("stepgen.1.maxaccel", "10")




    def setSpeed(self, speed):
        #Lógica para que a velocidade em cada eixo seja equivalente ao movimento
        self.h["set_speed_b"] = speed
        self.h["set_speed_b"] = speed

    def setPosition(self,position_b,position_c):
        self.h["set_position_b"] = position_b
        self.h["set_position_c"] = position_c

    def readSensor(self, i):
        if i==0:
            return self.h["sensor_b"]
        elif i==1:
            return self.h["sensor_c"]
        else: return None

    def roda(self):
        i=0
        while i<10:
            self.setSpeed(10+i*3)
            self.setPosition(5+3*i,7+3*i)
            time.sleep(5)
            i+=1

MC = Machine_control()

