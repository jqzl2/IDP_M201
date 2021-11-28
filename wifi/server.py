import socket
import time

def path_finder_server():
    HOST = '0.0.0.0'
    PORT = 8090

    s = socket.socket()

    s.bind((HOST, PORT))                                   # associate the socket with a specific network and port number
    s.listen(0)                                             # enable server to accept() connections
    conn, address = s.accept()                             # blocks and waits for incoming connection; returns a new socket object representing the connection and a tuple (host,port) holding the address of the client
                                        

    # use new socket object conn to communicate with client
    print('Connected by ', address)

    dummy_mode = conn.recv(32)                                # conn server receives data of buffer size 32 bytes,
    print(type(dummy_mode)) 
    commands = 'hello$'
    conn.send(commands.encode())

    conn.close()                                          # close socket object conn

