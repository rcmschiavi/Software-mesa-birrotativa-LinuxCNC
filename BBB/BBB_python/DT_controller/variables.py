import json, os, pickle

cur_path = os.path.dirname(__file__)
file_address = cur_path + '/TCP/status_data.json'
data = None
with open(file_address, 'r+') as json_file:
    print type(json_file)
    data = json.load(json_file)
    print str(data)
    data = json.dumps(data[0], indent=4)
    print data
    #data = json.dumps(data[0])
    #print data
    #pick = pickle.dumps(data)
    #print type(pick)
    #print type(pick.encode())
