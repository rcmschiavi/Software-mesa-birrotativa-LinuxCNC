#coding: utf-8
'''
Classe que lida com a conexão TCP através de uma thread

Autor: Rodolfo Cavour Moretti Schiavi

Ainda não foi implementada a queue que fará a comunicação entre a thread principal e a de TCP

'''
from threading import Thread
import socket
import time



class Connection:

    def __init__(self):
        self.callback_latency = 5
        self.connection = None
        self.i = 0
        self.client_address = None
        self.a = 1
        self.sock = None
        self.server_address = None
        self.start_socket()
        self.data = None
        self.status = None

    def start_socket(self):
        # A conexão é iniciada e reiniciada sempre que se fecha por algum motivo
        while True:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_address = ('10.0.0.2', 8000)
            self.sock.bind(self.server_address)
            self.sock.listen(1)
            self.wait_connection()
            self.wait_message()
            time.sleep(1)
            self.connection.close()
            time.sleep(4)

    def wait_connection(self):
        print "Conectando"
        self.connection, self.client_address = self.sock.accept()
        self.connection.settimeout(self.callback_latency)


    def wait_message(self):
        try:
            while True:
                try:
                    self.data = self.connection.recv(512)
                    if self.data:
                        print self.data
                        self.i += 1
                    else:
                        #Caso a conexão seja perdida, finaliza esse laço e entra no laço de reconectar
                        break
                except:
                    print "except timeout"
                    self.callback("Há: " + str(self.i))
        except:
            print "error"
            pass

    def callback(self, data):
        self.connection.sendall(data)

    def run(self):
        print self.a


class Th(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.con = None

    def run(self):
        self.connect()

    def connect(self):
        self.con = Connection()



