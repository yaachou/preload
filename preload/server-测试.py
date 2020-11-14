from socket import *
import json
 
host = '127.0.0.1'
port = 10240
size = 1024
addr = (host, port)

server = socket(AF_INET,SOCK_STREAM)
server.bind((host, port)) 
server.listen(5)

while True:
    link, addr = server.accept()
    data = link.recv(size).decode()
    data = eval(data)
    print(data)
    back = {'type':'preload','msg':{'temperature': '20','velocity':'3','pmv':0.111,'apmv':0.333,'times':'3','mode':'cold','direction':'3'}}
    back = str(back)
    print(back)
    link.send(back.encode())
    link.close()