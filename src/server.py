import socket
from src.store import process
from src.parser import parser
from pathlib import Path

def serve(host:str, port:int, imh:dict, storage:Path):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host,port))
        s.listen(1) #backlog is set to 1
        conn, addr = s.accept()
        with conn:
            print('Connect by', addr)
            while True:
                data = conn.recv(1024)
                if not data: break
                action, key, value = parser(data)
                res = process(storage,imh,action,key,value)
                check = f"Result: {res}\n"
                conn.sendall(check.encode("utf-8"))
