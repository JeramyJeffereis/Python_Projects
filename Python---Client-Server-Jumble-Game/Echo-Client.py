"""
Client side: use sockets to send data to the server, and print server's
reply to each message line; 'localhost' means that the server is running
on the same machine as the client, which lets us test client and server
on one machine;  to test over the Internet, run a server on a remote
machine, and set serverHost or argv[1] to machine's domain name or IP addr;
Python sockets are a portable BSD socket interface, with object methods
for the standard socket calls available in the system's C library;
"""

import sys
from socket import *              # portable socket interface plus constants
serverHost = 'localhost'          # server name, or: 'starship.python.net'
serverPort = 50007                # non-reserved port used by the server

def contact_server():
    sockobj = socket(AF_INET, SOCK_STREAM)      # make a TCP/IP socket object
    sockobj.connect((serverHost, serverPort))   # connect to server machine + port
    while True:                                 # the while True loop will run until the break statement
        data = sockobj.recv(1024)               # the client recieves 1024 bits from socket
        print(data.decode())                    # the client then decodes recieved data and prints
        print('Type your Answer')               # the user is then prompted to enter an answer
        answer = input()                        # the data entered by the user is saved
        sockobj.send(answer.encode())           # user data is encoded and sent back to the socket
        if answer == 'exit':                    # if user enters exit we break the loop and the client exits  
            break                               #   and send the signal to the server.
        data = sockobj.recv(1024)               # the servers response to the clients entry is recieved
        print(data.decode(), '\n')              #   and then prints.
    sockobj.close()                             # close socket to send eof to server
contact_server()
