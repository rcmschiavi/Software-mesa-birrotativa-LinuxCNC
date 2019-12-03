#coding: utf-8
'''
Classe que realizará todo o fluxo principal do programa

Autor: Rodolfo Cavour Moretti Schiavi

Por hora só cria a thread secundária de comunicação TCP e a inicia

Testes como o Queue
'''

from TCP import tcp
import command_parser
import Queue, time

from TCP import save_status

'''

s = save_status.Save_file()
#print s.params

p = save_status.params()

print s.save(p.list_params())

p.INSPECT = 150

print s.save(p.list_params())'''

class Main():
    def __init__(self):
        self.i=0
        self.q = Queue.Queue()
        self.c = tcp.Th(self.q)
        self.c.start()
        self.save_stat = save_status.Save_file()
        self.params = save_status.params()
        self.state = "stoped"
        self.cycle()
        self.prg_point = 0
        self.jog_buffer = []
        self.is_moving = False

    def cycle(self):
        while True:

            if not self.q.empty():
                data = str(self.q.get())
                print ("Queue: " + data)
                #print (self.parser.mode(data))

            else:
                print "Lista vazia"

    def executa_estado(self, data):
        mode = data[0]["mode"]
        if self.state=="stoped" and mode==None:
            self.params.EXEC_PGR = 0
            self.params.TASK_EXEC = 0
            self.save_stat.save(self.params.list_params())  # Salva o status no json para enviar
            #return
        elif (self.state=="jogging" or self.state=="exec_prog") and (mode=="ESTOP"):
            #prioridade para o ESTOP
            #Envia modbus
            self.state = "stoped"
            #return
        elif self.params.HOMED==0 or mode=="HOME":
            if mode=="HOME":
                self.params.HOMING = 1
                self.save_stat.save(self.params.list_params()) #Salva o status no json para enviar
                #Executa_home  ## No final do homing ele vai alterar o valor de homed para 1 e homing para 0
            else:
                pass
        elif self.state=="exec_prog" or mode=="exec_prog":
            if mode=="STOP":
                self.state="stoped"
                self.params.EXEC_PGR = 0
                self.params.TASK_EXEC = 0
            elif mode=="cycStart":
                self.prg_point = 0
                self.params.EXEC_PGR=1
                self.save_stat.save(self.params.list_params())  # Salva o status no json para enviar
                # executa_operação()
            else:
                # executa_operação() # o fim do programa alterará o estado para parado

        elif self.state=="jogging" or mode=="jog":
            if mode=="jog":
                self.jog_buffer.append(data[0]["params"])
                self.state="jogging"
            # check_movement()
            if len(self.jog_buffer):
                if not self.is_moving:
                    #exec_mov() #Exclui o item da lista
            else:
                if not self.is_moving:
                    self.state="stoped"
        if mode=="program":
            #O modo gravar programa independe dos outros modos e estados
        #proximo estado é o prog

        time.sleep(5)







