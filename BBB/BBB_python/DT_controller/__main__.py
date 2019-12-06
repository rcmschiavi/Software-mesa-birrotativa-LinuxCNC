#coding: utf-8
'''
Classe que realizará todo o fluxo principal do programa

Autor: Rodolfo Cavour Moretti Schiavi

Por hora só cria a thread secundária de comunicação TCP e a inicia

Testes como o Queue
'''

import TCP
import Queue, time, json
import jsonPatternArray
import modbus, MACHINE_CONTROLL


#print s.params
'''
p = save_status.params()

print s.save(p.list_params())

p.INSPECT = 150

print s.save(p.list_params())
'''


class Main:
    def __init__(self):
        self.i=0
        self.qRec = Queue.Queue()
        self.qSend = Queue.PriorityQueue()
        self.JPA = jsonPatternArray.JsonPatternArray()
        #self.c = TCP.Th(self.qRec, self.qSend)
        #self.c.start()
        #self.save_stat = TCP.save_status.Save_file()
        #self.params = TCP.save_status.params()
        self.state = "stoped"
        self.cycle()
        self.prg_point = 0
        self.jog_buffer = []
        self.is_moving = False
        #self.MB = modbus.Modbus()


    def cycle(self):
        self.qRec.put(json.dumps([{"modo": 1, "params": [0, 0, 1]}]))
        while True:
            time.sleep(2)

    def getMode(self):
        if not self.qRec.empty():
            data = json.loads(self.qRec.get())
            return [data[0]["mode"],data[0]["params"]]
            # print (self.parser.mode(data))
        else:
            return None

    def executa_estado(self, data):
        mode = data[0]
        params = data[1]
        P_ESTOP = self.MB.getP_ESTOP()
        if mode=="EXTESTOP":
            self.state = "EXETSTOP"
            self.MB.writeESTOP()
            return
        elif P_ESTOP:
            self.state = "EXTESTOP"
            data = self.JPA.EXTESTOP(1)
            self.qSend.put(1, data)
            return
        elif self.state == "EXTESTOP":
            # Pooling modbus para ler o estado e enviar EXTESTOP ok
            self.state = "stopped"
            data = self.JPA.EXTESTOP(0)
            self.qSend.put(1, data) #Envia o status da que a parada de emergência foi desativada
            return

        elif self.state=="stopped" and mode==None:
            self.JPA.EXEC_PGR = 0
            self.JPA.TASK_EXEC = 0
            data = self.JPA.STATUS()
            self.qSend.put(2, data)  # Envia o status

        elif (self.state=="jogging" or self.state=="exec_prog") and (mode=="ESTOP"):
            self.state = "stopped"
            return

        elif mode=="HOME":
                self.state = "HOMING"
                self.JPA.HOMING = 1
                data = self.JPA.STATUS()
                self.qSend.put(2, data)
                # TODO Chamar a função de HOME
        elif self.state=="HOMING":
            # TODO CHAMAR HOME EIXO, UM CICLO QUE FICA RODANDO ATÈ FINALIZAR O HOME, MAS VAI LER AS PARADAS DE EMERGÊNCIA
            #self.state ==
            pass

        elif self.state=="exec_prog" or mode=="exec_prog":
            if mode=="ESTOP":
                self.state="stopped"
                self.JPA.EXEC_PGR = 0
                self.JPA.TASK_EXEC = 0
                data = self.JPA.STATUS()
                self.qSend.put(2, data)

            elif mode=="cycStart":
                self.prg_point = 0
                self.JPA.EXEC_PGR=1
                data = self.JPA.STATUS()
                self.qSend.put(2, data)
                # executa_operação()

            else:
                # executa_operação() # o fim do programa alterará o estado para parado
                pass
        elif self.state=="jogging" or mode=="jog":
            if mode=="jog":
                self.jog_buffer.append(params)
                self.state="jogging"
            # check_movement()

            if len(self.jog_buffer):
                if not self.is_moving:
                    #exec_mov() #Exclui o item da lista
                    pass
            else:
                if not self.is_moving:
                    self.state="stoped"

        if mode=="program":
            #O modo gravar programa independe dos outros modos e estados
            pass
        #proximo estado é o prog

        time.sleep(5)

    def HOME_CYCLE(self):
        #Home do primeiro eixo
        self.HOME_AXIS(0)
        self.HOME_AXIS(1)
        self.JPA.HOMING = 0
        self.JPA.HOMED = 1


        pass

    def HOME_AXIS(self, axis):
        #Altera a velocidade dos eixos para uma velocidade razoável
        #FICA INCREMENTANDO O POSITION-CDM e lendo o fim de curso em um pooling até achar o fim de curso
        #RECUA NA MESMA VELOCIDADE ATÉ DETECTAR DE NOVO O SENSOR
        #DIMINUI AINDA MAIS A VELOCIDADE
        #AVANCA DE NOVO COM PULSOS MENORES E CONTINUA LENDO



        pass


    def IS_MOVING(self):
        #ANALISA OS PINOS DE MOVIMENTO SE COUNTS == POSITION-CMD E RETORNA
        MC = MACHINE_CONTROLL.Machine_control()
        MC.h

Main()