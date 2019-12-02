from pyModbusTCP.client import ModbusClient
import time

c = ModbusClient()
c.host("192.168.0.99")
c.port(502)
# managing TCP sessions with call to c.open()/c.close()
c.open()

print c
'''
if c.write_multiple_registers(40001, [15,9]):
    print("write ok")
else:
    print("write error")'''


for i in range (0,4):
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
'''
for i in range (510,531):
    for j in range(1):
        regs = c.read_input_registers(i)
    #print regs
        if regs:
            print(regs, i, j)
        else:
                    
            print("read error")
        time.sleep(0.1)

'''



       
if c.write_multiple_registers(3, [49152]):
    print("write ok")
else:
    print("write error")

'''

if c.write_multiple_registers(3, [16384]):
    print("write ok")
else:
    print("write error")
'''
#time.sleep(5)
c.close()
