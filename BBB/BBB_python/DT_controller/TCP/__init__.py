#coding: utf-8
'''
Package que lida com a conexão TCP através de uma thread

Autor: Rodolfo Cavour Moretti Schiavi

'''

from threading import Thread
import socket
import time, json, os
class Connection:



    def __init__(self, qRec, qSend):

        self.cur_path = os.path.dirname(__file__)
        self.qRec = qRec
        self.qSend = qSend
        self.callback_latency = 2
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
            time.sleep(1)
            self.wait_message()
            time.sleep(0.1)
            self.connection.close()
            self.qRec.put("Desconectado")
            time.sleep(0.1)



    def wait_connection(self):
        print "Conectando"
        self.connection, self.client_address = self.sock.accept()
        self.qRec.put("Conectado")
        self.connection.settimeout(self.callback_latency)
        print ("Conectado à: "+  str(self.client_address))

    def wait_message(self):
        try:
            while True:
                try:
                    self.data = self.connection.recv(512)
                    if self.data:
                        print self.data
                        self.i += 1
                        self.qRec.put(self.data)
                        self.callback("200")
                    else:
                        #Caso a conexão seja perdida, finaliza esse laço e entra no laço de reconectar
                        break
                except Exception as e:
                    print ("Erro 1 waitmessage: " + str(e))
                    if not self.qSend.empty():
                        self.data=self.qSend.get()
                        self.callback(self.data)
        except Exception as e:
            print ("Erro 2 waitmessage: " + str(e))

    def callback(self, data):
        self.connection.sendall(str(data)+"\n")


class Th(Thread):

    def __init__(self, qRec, qSend):
        Thread.__init__(self)
        self.con = None
        self.qRec = qRec
        self.qRec = qSend

    def run(self):

        self.connect()

    def connect(self):
        self.con = Connection(self.qRec, self.qSend)




