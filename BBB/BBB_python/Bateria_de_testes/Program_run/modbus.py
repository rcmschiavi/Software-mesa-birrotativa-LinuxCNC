# coding: utf-8

''''
Código que fará a comunicação modbus, parseando os dados que são sempre em binário

Autor: Rodolfo Cavour Moretti Schiavi

'''

from pyModbusTCP.client import ModbusClient
import time

class Modbus:

    def __init__(self):
        self.c = None

        self.ADDR_BBB_ESTOP = 0
        self.ADDR_P_ESTOP = 1
        self.ADDR_UPDATE = 2
        self.ADDR_MODO_INSPEC = 3
        self.ADDR_ERRO_INSPECAO = 4
        self.ADDR_INSPECAO_OK = 5
        self.ADDR_MESA_START_OP = 6
        self.ADDR_MESA_END_OP = 7
        self.ADDR_FEED_BCKW = 13
        self.ADDR_FEED_FWRD = 14
        self.ADDR_BBB_WAITING = 15

        self.MESA_END_OP = None
        self.MESA_START_OP = None
        self.INSPECAO_OK = None
        self.ERRO_INSPECAO = None
        self.MODO_INSPECAO = None
        self.DATA_UPDATE = None
        self.PAINEL_ESTOP = None
        self.BBB_ESTOP = None

        self.CELL_CTRL_ADDR = 2

        self.host = "192.168.0.99"
        self.port = "502"
        self.connectModbus()


    def boolLstToBinary(self, bList):
        ''' Função que recebe uma lista de booleanos e retorna o correspondente binário '''
        binary = '0b' + ''.join(['1' if x else '0' for x in bList])
        return binary

    def boolLstToDecimal(self, bList):
        '''Função para converter binário em decimal'''
        decimal = int(self.boolLstToBinary(bList), 2)
        return decimal

    def decimalToLst(self, decimal):
        data_size = 16
        '''Função que converte Decimal em uma lista de booleanos'''
        binary = bin(decimal)
        binary = binary[2:]
        bList = []
        bList.append([True if x=='1' else False for x in binary])
        size_ctrl = len(bList[0])
        if size_ctrl < data_size:
            for i in range(data_size - size_ctrl):
                bList[0].insert(0,False)
        return bList[0]

    def readInspecParams(self):
        data = []
        data.append(self.c.read_holding_registers(0))
        data.append(self.c.read_holding_registers(1))
        data.append(self.c.read_holding_registers(2))
        return data

    def readCell_control(self):

        data = self.c.read_holding_registers(self.CELL_CTRL_ADDR)
        CELL_CONTROL = self.decimalToLst(data[0])

        self.MESA_END_OP = CELL_CONTROL[self.ADDR_MESA_END_OP]
        self.MESA_START_OP = CELL_CONTROL[self.ADDR_MESA_START_OP]
        self.INSPECAO_OK = CELL_CONTROL[self.ADDR_INSPECAO_OK]
        self.ERRO_INSPECAO = CELL_CONTROL[self.ADDR_ERRO_INSPECAO]
        self.MODO_INSPECAO = CELL_CONTROL[self.ADDR_MODO_INSPEC]
        self.DATA_UPDATE = CELL_CONTROL[self.ADDR_UPDATE]
        self.PAINEL_ESTOP = CELL_CONTROL[self.ADDR_P_ESTOP]
        self.BBB_ESTOP = CELL_CONTROL[self.ADDR_BBB_ESTOP]

        return CELL_CONTROL

    def writeActivateInspect(self):
        CELL_CONTROL = self.readCell_control()
        CELL_CONTROL[self.ADDR_MODO_INSPEC] = True
        value = self.boolLstToDecimal(CELL_CONTROL)
        op_succeed = self.c.write_multiple_registers(self.CELL_CTRL_ADDR, [value])
        return op_succeed

    def writeDeactivateInspect(self):
        CELL_CONTROL = self.readCell_control()
        CELL_CONTROL[self.ADDR_MODO_INSPEC] = False
        value = self.boolLstToDecimal(CELL_CONTROL)
        op_succeed = self.c.write_multiple_registers(self.CELL_CTRL_ADDR, [value])
        return op_succeed

    def readBBBWaiting(self):
        CELL_CONTROL = self.readCell_control()
        return CELL_CONTROL[self.ADDR_BBB_WAITING]


    def writeFwdWire(self):
        CELL_CONTROL = self.readCell_control()
        CELL_CONTROL[14] = True
        value = self.boolLstToDecimal(CELL_CONTROL)
        result1 = self.c.write_multiple_registers(self.CELL_CTRL_ADDR, [value])
        BBB_WAIT = self.readBBBWaiting()
        print "BBB wait"
        while BBB_WAIT:
            BBB_WAIT = self.readBBBWaiting()
        print "BBB ok"
        result2 = self.writeStopWire()
        return [result1,result2]

    def writeBackWire(self):
        CELL_CONTROL = self.readCell_control()
        CELL_CONTROL[13] = True
        value = self.boolLstToDecimal(CELL_CONTROL)
        result1 = self.c.write_multiple_registers(self.CELL_CTRL_ADDR, [value])
        BBB_WAIT = self.readBBBWaiting()
        print "BBB wait"
        while BBB_WAIT:
            BBB_WAIT = self.readBBBWaiting()
        print "BBB ok"
        result2 = self.writeStopWire()
        return [result1,result2]

    def setTimer(self,time):
        result = self.c.write_multiple_registers(1, [time])
        return result

    def writeStopWire(self):

        CELL_CONTROL = self.readCell_control()
        CELL_CONTROL[13] = False
        CELL_CONTROL[14] = False
        value = self.boolLstToDecimal(CELL_CONTROL)
        result = self.c.write_multiple_registers(self.CELL_CTRL_ADDR, [value])
        return result

    def writeESTOP(self, status):

        CELL_CONTROL = self.readCell_control()
        CELL_CONTROL[self.ADDR_BBB_ESTOP] = status
        value = self.boolLstToDecimal(CELL_CONTROL)
        op_succeed = self.c.write_multiple_registers(self.CELL_CTRL_ADDR, [value])
        return op_succeed

    def writeMesaEndOP(self):

        CELL_CONTROL = self.readCell_control()
        CELL_CONTROL[self.ADDR_MESA_END_OP] = True
        value = self.boolLstToDecimal(CELL_CONTROL)
        op_succeed = self.c.write_multiple_registers(self.CELL_CTRL_ADDR, [value])
        return op_succeed

    def getP_ESTOP(self):
        self.readCell_control()
        return self.PAINEL_ESTOP

    def getMESA_START_OP(self):

        self.readCell_control()
        return self.MESA_START_OP

    def connectModbus(self):

        self.c = ModbusClient()
        self.c.host(self.host)
        self.c.port(self.port)
        self.c.open()
        print "Conexão aberta"

    def closeConection(self):
        self.c.close()

