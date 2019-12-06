# coding: utf-8

'''

Inicia a conexão recebe os pacotes e envia os callbacks

Vou ter que fazer threads pra conseguir executar os comandos e

'''
'''

import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('192.168.0.100', 8000)
sock.bind(server_address)

sock.listen(1)

'''

# import socket programming library
import socket

# import thread module
from _thread import *
import threading

print_lock = threading.Lock()


# thread fuction
def threaded(c):
    while True:

        # data received from client
        data = c.recv(1024)
        if not data:
            print('Bye')

            # lock released on exit
            print_lock.release()
            break

        # reverse the given string from client
        data = data[::-1]

        # send back reversed string to client
        c.send(data)

        # connection closed
    c.close()


def Main():
    host = "localhost"

    # reverse a port on your computer
    # in our case it is 12345 but it
    # can be anything
    port = 12345
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("socket binded to port", port)

    # put the socket into listening mode
    s.listen(5)
    print("socket is listening")

    # a forever loop until client wants to exit
    while True:
        # establish connection with client
        c, addr = s.accept()

        # lock acquired by client
        print_lock.acquire()
        print('Connected to :', addr[0], ':', addr[1])

        # Start a new thread and return its identifier
        threading.start_new_thread(threaded, (c,))
        break
    s.close()


if __name__ == '__main__':
    Main()