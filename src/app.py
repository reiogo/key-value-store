import socket
import re
from processer import parser, process

HOST = ''
PORT = 50007

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST,PORT))
    s.listen(1) #backlog is set to 1
    conn, addr = s.accept()
    with conn:
        print('Connect by', addr)
        while True:
            data = conn.recv(1024)
            if not data: break
            action, key, value = parser(data)
            res = process(action,key,value)
            check = f"Result: {res}\n"
            conn.sendall(check.encode("utf-8"))




