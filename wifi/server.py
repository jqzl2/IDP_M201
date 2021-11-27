import socket

HOST = ''
PORT = 65432

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # creates socket object specifying Internet address family for IPv4 and socket type for TCP

s.bind((HOST, PORT))                                   # associate the socket with a specific network and port number
s.listen()                                             # enable server to accept() connections
conn, address = s.accept()                             # blocks and waits for incoming connection; returns a new socket object representing the connection and a tuple (host,port) holding the address of the client
s.close()                                              # close socket object s

# use new socket object conn to communicate with client
print('Connected by ', address)
while True:
    data = conn.recv(3)                                # conn server receives data of buffer size 3 bytes, 
    if data == 0:                                       
        print('Invalid dummy mode')
        break
    else:
        print(data)
        conn.sendall("0,005,015.1,000,-01.0,005,015.1,000,-01.0,005,015.1,000,-01.0,005,025.1,000,-01.")
        break

conn.close()                                          # close socket object conn
