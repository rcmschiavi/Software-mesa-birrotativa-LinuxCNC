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
        print bList[0]
        print(size_ctrl)
        if size_ctrl < data_size:
            for i in range(data_size - size_ctrl):
                bList[0].insert(0,False)
        print len(bList[0])
        return bList[0]
    def readInspecParams(self):
        data = []
        data.append(self.c.read_holding_registers(0))
        data.append(self.c.read_holding_registers(1))
        data.append(self.c.read_holding_registers(2))
        return data

    def readCell_control(self):

        data = self.c.read_holding_registers(self.CELL_CTRL_ADDR)
        print data
        CELL_CONTROL = self.decimalToLst(data[0])

        self.MESA_END_OP = CELL_CONTROL[7]
        self.MESA_START_OP = CELL_CONTROL[6]
        self.INSPECAO_OK = CELL_CONTROL[5]
        self.ERRO_INSPECAO = CELL_CONTROL[4]
        self.MODO_INSPECAO = CELL_CONTROL[3]
        self.DATA_UPDATE = CELL_CONTROL[2]
        self.PAINEL_ESTOP = CELL_CONTROL[1]
        self.BBB_ESTOP = CELL_CONTROL[0]

        return CELL_CONTROL

    def writeInspectionParams(self, data):
        ''' Escreve o valor nos registradores de parâmetros de inspeção. Todas as variáveis já vem tratadas'''
        SETPOINT_ARAME = data[0]
        ARAME_ATUAL = data[1]
        TOL_ARAME = data[2]
        REGs_INSP = [SETPOINT_ARAME,ARAME_ATUAL,TOL_ARAME]
        i_writen = 0
        for REG,REG_VALUE in enumerate(REGs_INSP):
            if self.c.write_multiple_registers(REG, [REG_VALUE]):
                print("write ok on register: " + str(REG))
                i_writen+=1
            else:
                print("Error writing on register: " + str(REG))
        if i_writen==3:
            return True
        else:
            return False

    def writeUpdateWireLenght(self,wireLenght):
        op_succeed = self.c.write_multiple_registers(1, [wireLenght])
        return op_succeed


    def writeActivateInspect(self):
        activ_insp_address = 3

        CELL_CONTROL = self.readCell_control()
        CELL_CONTROL[activ_insp_address] = True
        value = self.boolLstToDecimal(CELL_CONTROL)
        print value
        op_succeed = self.c.write_multiple_registers(3, [value])
        return op_succeed

    def readBBBWainting(self):
        CELL_CONTROL = self.readCell_control()
        return CELL_CONTROL[15]

    def writeFwdWire(self):
        CELL_CONTROL = self.readCell_control()
        CELL_CONTROL[14] = True
        value = self.boolLstToDecimal(CELL_CONTROL)
        result = self.c.write_multiple_registers(3, [value])
        return result

    def writeBackWire(self):
        CELL_CONTROL = self.readCell_control()
        CELL_CONTROL[13] = True
        value = self.boolLstToDecimal(CELL_CONTROL)
        result = self.c.write_multiple_registers(3, [value])
        return result

    def writeDeactivateInspect(self):
        activ_insp_address = 3

        CELL_CONTROL = self.readCell_control()
        CELL_CONTROL[activ_insp_address] = False
        value = self.boolLstToDecimal(CELL_CONTROL)
        print value
        op_succeed = self.c.write_multiple_registers(3, [value])
        return op_succeed

    def writeESTOP(self, ):
        ESTOP_address = 7
        CELL_CONTROL = self.readCell_control()
        CELL_CONTROL[ESTOP_address] = True
        op_succeed = self.c.write_multiple_registers(self.CELL_CTRL_ADDR, CELL_CONTROL)
        return op_succeed

    def connectModbus(self):
        self.c = ModbusClient()
        self.c.host(self.host)
        self.c.port(self.port)
        self.c.open()
        print "Conexão aberta"

    def closeConection(self):
        self.c.close()


mb = Modbus()
print mb.readCell_control()