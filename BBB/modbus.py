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
    return list

print DecimalToLst(5)