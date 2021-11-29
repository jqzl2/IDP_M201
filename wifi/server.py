import socket
import keyboard

def set_up_server():
    HOST = '0.0.0.0'
    PORT = 8090

    s = socket.socket()

    s.bind((HOST, PORT))                                   # associate the socket with a specific network and port number
    s.listen(0)                                            # enable server to accept() connections
    conn, address = s.accept()                             # blocks and waits for incoming connection; returns a new socket object representing the connection and a tuple (host,port) holding the address of the client
    print('Connected by ', address)
    return conn

def receive_dummy_mode(conn):                              # receive dummy mode from Arduino 

    dummy_mode = conn.recv(32)                             # conn server receives data of buffer size 32 bytes,
    while (len(dummy_mode) == 0):
        print(len(dummy_mode))
        dummy_mode = conn.recv(32)
    print(dummy_mode) 
    return dummy_mode
 
def send_commands(commands, conn):                        # send commands to Arduino
    assert type(commands) == str
    print(commands)
    conn.send(commands.encode())
    print("sent")
    #arduino_response = conn.recv(32)
    #print(arduino_response)                               # print Arduino response if commands sent successfully


if __name__ == '__main__':
    conn = set_up_server()

    i=0
    while(i<5):
        i += 1
        commands = ""
        commands = "!0,005,015.0,005,015!"
        receive_dummy_mode(conn)
        send_commands(commands, conn) 



