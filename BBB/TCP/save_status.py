#coding: utf-8
'''
Salva os paramêtros de status em um arquivo em formato JSON
No processo de comunicação o server espera um comando do cliente, caso estoure o timeout é enviado ao cliente os
parâmetros de status da máquina
Foi optado por esse método para não sobrecarregar a memória da BBB utilizando uma FIFO na memória. Não há necessidade
de enviar os status sempre

Autor: Rodolfo Cavour Moretti Schiavi

'''

import json, os


class Save_file:

    def __init__(self):
        self.list_params = []

    def save(self, list_params):
        data = []
        data.append({
            "mode": "STATUS",
            "params": [list_params]
        })

        cur_path = os.path.dirname(__file__)
        with open(cur_path + '/status_data.json', 'w') as outfile:
            json.dump(data, outfile,sort_keys=True)

class params():

    def __init__(self):
        self.HOMED = 7
        self.HOMING = 6
        self.TURNED_ON = 5
        self.ACTIVE_PGR = 4
        self.EXEC_PGR = 3
        self.TASK_EXEC = 2
        self.INSPECT = 1
        self.list = []

    def list_params(self):
        return [self.HOMED,self.HOMING,self.TURNED_ON,self.ACTIVE_PGR,self.EXEC_PGR,self.TASK_EXEC,self.INSPECT]


'''
    def save_json(self, params):
        data = []
        data.append({
            'EMERGENCY': params[0],
            'ON': params[1],
            'HOMED': params[2],
            'ACTIVE_PROG': params[3],
            'RUNNING_TASK': params[4],
            'RUNNING_INSPECTION': params[5]
        })

        cur_path = os.path.dirname(__file__)
        with open(cur_path + '/status_data.json', 'w') as outfile:
            json.dump(data, outfile)
'''





