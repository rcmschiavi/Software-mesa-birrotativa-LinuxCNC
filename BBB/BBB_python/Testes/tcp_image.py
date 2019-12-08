# coding: utf-8
'''

Conexão que será usada na BBB

Exemplo que só recebe um dado e fecha a conexão
'''

import socket
import json
import numpy
import time
import cv2
import sys
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('localhost', 8000)
sock.bind(server_address)

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
sock.listen(1)
connection, client_address = sock.accept()

try:
    img = cv2.imread('image.jpg', 0)
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    result, imgencode = cv2.imencode('.jpg', img, encode_param)
    data = numpy.array(imgencode)
    stringData = data.tostring()
    data = {"mode": "FRAME", "params": len(stringData)}
    print "enviando JSON"
    data = json.dumps(data)
    connection.sendall(str(data))
    connection.sendall(stringData)



finally:
    "conexão fechada"
    connection.close()
