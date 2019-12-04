# coding: utf-8
''''
Código que fará a comunicação modbus, parseando os dados que são sempre em binário

Por enquanto só está implementado as conversões de binário para lista que será interpretado posteriormente

Autor: Rodolfo Cavour Moretti Schiavi

'''
from pymodbus.client.sync import ModbusTcpClient

def BoolLstToBinString(list):
    ''' Função que recebe uma lista de booleanos e retorna o correspondente binário '''
    binary = '0b' + ''.join(['1' if x else '0' for x in list])
    return binary

def BinaryLstToDecimal(list):
    '''Função para converter binário em decimal'''
    decimal = int(BoolLstToBinString(list), 2)
    return decimal

def DecimalToLst(decimal):
    '''Função que converte Decimal em uma lista de booleanos'''
    binary = bin(decimal).strip("0b")
    list = []
    list.append([True if x=='1' else False for x in binary])
    return list[0]

print DecimalToLst(5)

#Variáveis do Registrador B
SETPOINT_ARAME = 20
ARAME_ATUAL = 10
TOL_ARAME = 0.5

#Lista do registrador B - Enviado da BBB para o CLP via modbus
REG_B = [SETPOINT_ARAME,ARAME_ATUAL,TOL_ARAME]

#Variáveis do registrador de controle
MESA_END_OP = 0
MESA_START_OP = 0
INSPECAO_OK = 0
ERRO_INSPECAO = 0
MODO_INSPECAO = 0
DATA_UPDATE = 0
PAINEL_ESTOP = 0
BBB_ESTOP = 0

#Lista de registradores de controle - Recebido do CLP e lido pela BBB
CELL_CONTROL = []
#
listRead = DecimalToLst(10)

print (len(listRead))
for i,item in enumerate(listRead):
    CELL_CONTROL.append(item)

size_ctrl = len(CELL_CONTROL)
if size_ctrl<7:
    for i in range(8-size_ctrl):
        CELL_CONTROL.append(False)

print len(CELL_CONTROL)


MESA_END_OP = CELL_CONTROL[0]
MESA_START_OP = CELL_CONTROL[1]
INSPECAO_OK = CELL_CONTROL[2]
ERRO_INSPECAO = CELL_CONTROL[3]
MODO_INSPECAO = CELL_CONTROL[4]
DATA_UPDATE = CELL_CONTROL[5]
PAINEL_ESTOP = CELL_CONTROL[6]
BBB_ESTOP = CELL_CONTROL[7]

CELL_CONTROL = [MESA_END_OP,MESA_START_OP,INSPECAO_OK,ERRO_INSPECAO,MODO_INSPECAO,DATA_UPDATE,PAINEL_ESTOP,BBB_ESTOP]

print ("LISTA FINAL: " + str(CELL_CONTROL))

from pyModbusTCP.client import ModbusClient
import time

c = ModbusClient()
c.host("192.168.0.99")
c.port(502)
# managing TCP sessions with call to c.open()/c.close()
c.open()

for i in range (0,3):
    for j in range(1):
        regs = c.read_holding_registers(i)
    #print regs
        if regs:
            print(regs, i, j)
        else:
            pass
            #print("read error")
        time.sleep(0.1)


print("input")

if c.write_multiple_registers(3, [49152]):
    print("write ok")
else:
    print("write error")

time.sleep(5)
c.close()

