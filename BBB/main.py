#coding: utf-8
'''
Classe que realizará todo o fluxo principal do programa

Autor: Rodolfo Cavour Moretti Schiavi

Por hora só cria a thread secundária de comunicação TCP e a inicia 

Testes como o Queue 
'''

from TCP import tcp
import Queue, time

i=0
q = Queue.Queue()
q.put(76)
c = tcp.Th(q)
c.start()

for i in range(100):
    q.put(25 + i*10)
    time.sleep(10)

