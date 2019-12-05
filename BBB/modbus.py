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
        self.MESA_END_OP = None
        self.MESA_START_OP = None
        self.INSPECAO_OK = None
        self.ERRO_INSPECAO = None
        self.MODO_INSPECAO = None
        self.DATA_UPDATE = None
        self.PAINEL_ESTOP = None
        self.BBB_ESTOP = None

        self.CELL_CTRL_ADDR = 3
        self.host = "192.168.0.99"
        self.port = "502"
        self.connectModbus()


    def boolLstToBinString(self, list):
        ''' Função que recebe uma lista de booleanos e retorna o correspondente binário '''
        binary = '0b' + ''.join(['1' if x else '0' for x in list])
        return binary

    def binaryLstToDecimal(self, list):
        '''Função para converter binário em decimal'''
        decimal = int(self.BoolLstToBinString(list), 2)
        return decimal

    def decimalToLst(self, decimal):
        data_size = 16
        '''Função que converte Decimal em uma lista de booleanos'''
        binary = bin(decimal).strip("0b")
        list = []
        list.append([True if x=='1' else False for x in binary])
        size_ctrl = len(list[0])
        print list[0]
        print(size_ctrl)
        if size_ctrl < data_size:
            for i in range(data_size - size_ctrl):
                list[0].append(False)
        print len(list[0])
        return list[0]

    def readCell_control(self):

        data = self.c.read_holding_registers(self.CELL_CTRL_ADDR)

        CELL_CONTROL = self.DecimalToLst(data)

        self.MESA_END_OP = CELL_CONTROL[0]
        self.MESA_START_OP = CELL_CONTROL[1]
        self.INSPECAO_OK = CELL_CONTROL[2]
        self.ERRO_INSPECAO = CELL_CONTROL[3]
        self.MODO_INSPECAO = CELL_CONTROL[4]
        self.DATA_UPDATE = CELL_CONTROL[5]
        self.PAINEL_ESTOP = CELL_CONTROL[6]
        self.BBB_ESTOP = CELL_CONTROL[7]

        # CELL_CONTROL = [MESA_END_OP, MESA_START_OP, INSPECAO_OK, ERRO_INSPECAO, MODO_INSPECAO, DATA_UPDATE, PAINEL_ESTOP,BBB_ESTOP]
        return CELL_CONTROL

    def writeInspectionParams(self, c, data):
        SETPOINT_ARAME = data[0]
        ARAME_ATUAL = data[1]
        TOL_ARAME = data[2]
        REGs_INSP = [SETPOINT_ARAME,ARAME_ATUAL,TOL_ARAME]

        for REG,REG_VALUE in enumerate(REGs_INSP):
            if self.c.write_multiple_registers(REG, [REG_VALUE]):
                print("write ok on register: " + str(REG))
            else:
                print("Error writing on register: " + str(REG))

    def writeActivateInspect(self):
        activ_insp_address = 2

        CELL_CONTROL = self.readCell_control()
        CELL_CONTROL[activ_insp_address] = True
        CELL_CONTROL.reverse()
        self.c.write_multiple_registers(3, CELL_CONTROL)


    def writeESTOP(self, ):
        ESTOP_address = 7
        CELL_CONTROL = self.readCell_control()
        CELL_CONTROL[ESTOP_address] = True
        self.c.write_multiple_registers(self.CELL_CTRL_ADDR, CELL_CONTROL)

    def connectModbus(self):
        self.c = ModbusClient()
        self.c.host(self.host)
        self.c.port(self.port)
        self.c.open()

    def closeConection(self):
        self.c.close()


M = Modbus()

print M.decimalToLst(10)
