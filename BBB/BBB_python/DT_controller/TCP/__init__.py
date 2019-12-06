#coding: utf-8
'''
Classe que lida com a conexão TCP através de uma thread

Autor: Rodolfo Cavour Moretti Schiavi

Ainda não foi implementada a queue que fará a comunicação entre a thread principal e a de TCP

'''
from threading import Thread
import socket
import time, json, os, sys, pickle
from collections import OrderedDict
import save_status

class Connection:

    def __init__(self, q):
        self.cur_path = os.path.dirname(__file__)
        self.q = q
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
        i=0
        # A conexão é iniciada e reiniciada sempre que se fecha por algum motivo
        while i<1:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_address = ('10.0.0.2', 8000)
            self.sock.bind(self.server_address)
            self.sock.listen(1)
            self.wait_connection()
            time.sleep(4)
            self.wait_message()
            #self.teste_call()
            time.sleep(1)
            self.connection.close()
            time.sleep(4)
            i+=1
        print "Fim da conexão"


    def wait_connection(self):
        print "Conectando"
        self.connection, self.client_address = self.sock.accept()
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
                        self.q.put(self.data)
                        self.callback("200")

                    else:
                        #Caso a conexão seja perdida, finaliza esse laço e entra no laço de reconectar
                        break
                except Exception as e:
                    print ("Erro 1 waitmessage: " + str(e))
                    self.data=""
                    self.callback(self.data)
        except Exception as e:
            print ("Erro 2 waitmessage: " + str(e))

    def callback(self, data):
        file_address = self.cur_path + '/status_data.json'
        if data == "":
            try:
                if os.stat(file_address).st_size!=0:
                    t_i = time.time()
                    with open(file_address, 'r+') as json_file:
                        data = json.load(json_file)
                        data = json.dumps(data[0]) #Decodifica para enviar
                    t_f = time.time()
                    self.connection.sendall(str(data))
                else:
                    print "File is empty"
            except Exception as e:
                print ("Erro callback: "+str(e))
        else:
            self.connection.sendall(str(data)+"\n")
    def teste_call(self):
        file_address = self.cur_path + '/status_data.json'
        with open(file_address, 'r') as json_file:
            data = json.load(json_file)

        self.connection.sendall(str(data))
        self.connection.sendall(data[0])
        data = json.dumps(data)
        self.connection.sendall(data)
        self.connection.sendall(data[0])
    def emergency(self):
        self.connection.sendall()


class Th(Thread):

    def __init__(self,q):
        Thread.__init__(self)
        self.con = None
        self.q = q

    def run(self):
        self.connect()

    def connect(self):
        self.con = Connection(self.q)



