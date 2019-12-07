# coding: utf-8
'''

Conexão que será usada na BBB

Exemplo que só recebe um dado e fecha a conexão
'''

import socket
import cv2
import sys
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('localhost', 8000)
sock.bind(server_address)

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
sock.listen(1)
connection, client_address = sock.accept()

try:
    img = cv2.imread('./image.jpg', 0)
    data = {    "mode": "IMAGE_INSPECTION", "params": img}
    while True:
        #Espera qualquer coisa e envia o dado
        data = connection.recv(16)
        if data:
            connection.sendall(data)
        else:
            break


finally:
    connection.close()
