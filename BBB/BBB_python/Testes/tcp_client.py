# coding: utf-8
import socket, json
import sys

# Create a tcp_folder/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
#Usando o ip do usb para testes
server_address = ('localhost', 8000)
sock.connect(server_address)

while True:
    key = input("Digite de 0 a 10")

    if key==0:
        data = {"mode": "HOME","params": 0}
        data = json.dumps(data)
        sock.sendall(data)

    elif key==1:
        data = {"mode": "ESTOP","params": 0}
        data = json.dumps(data)
        sock.sendall(data)

    elif key==2:
        data = {"mode": "EXTESTOP","params": 0}
        data = json.dumps(data)
        sock.sendall(data)

    elif key==3:
        data = {"mode": "CYCSTART","params": 0}
        data = json.dumps(data)
        sock.sendall(data)

    elif key==4:
        #Carregar programa na BBB
        data = {"mode": "PROGRAM","operation":0, "params": [[0.0,10.0,2.0,1,0],[10.0,20.0,5.0,1,0]]}
        data = json.dumps(data)
        sock.sendall(data)

    elif key==5:
        #Ler programa da BBB
        data = {"mode": "PROGRAM","operation":0, "params": 0}
        data = json.dumps(data)
        sock.sendall(data)

    elif key==6:
        #Deletar programa da BBB
        data = {"mode": "PROGRAM","operation":0, "params": 0}
        data = json.dumps(data)
        sock.sendall(data)

    elif key == 7:
        #Deletar programa da BBB
        data = {"mode": "JOG","params": [10.0,25.0,2.0]}
        data = json.dumps(data)
        sock.sendall(data)

    elif key == 8:
        #DBCP, TOL, Padrão Calib
        data = {"mode": "INSPECTION","params": [15.0,0.1,0]}
        data = json.dumps(data)
        sock.sendall(data)

    elif key == 'x':
        break

    data = sock.recv(512)
    print data
