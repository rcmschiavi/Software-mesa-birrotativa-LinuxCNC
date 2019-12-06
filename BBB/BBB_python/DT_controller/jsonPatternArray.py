#coding: utf-8
import json


class JsonPatternArray:

    def __init__(self):
        self.HOMED = 0
        self.HOMING = 0
        self.TURNED_ON = 0
        self.ACTIVE_PGR = 0
        self.EXEC_PGR = 0
        self.TASK_EXEC = 0
        self.INSPECT = 0

    def EXTESTOP(self, op):
        #Parada de emergencia externa (1-Parada Emergencia, 0-Sistema OK)
        data = {"mode": "EXTESTOP","params": op}
        data = json.dumps(data)
        return data

    def STATUS(self):
        statusList = [self.HOMED,self.HOMING,self.TURNED_ON,self.ACTIVE_PGR,self.EXEC_PGR,self.TASK_EXEC,self.INSPECT]
        data = {"mode":"STATUS","params":statusList}
        data = json.dumps(data)
        return data

    def PROGRAM(self, program):
        data = {"mode": "PROGRAM","params": [program]}
        data = json.dumps(data)
        return data

    def INSPECT(self, param):
        #Array de inspeção, inspectionRESULT, 0-operando,1-ok, -1 erro
        data = {"mode": "INSPECTION","params": param}
        data = json.dumps(data)
        return data


