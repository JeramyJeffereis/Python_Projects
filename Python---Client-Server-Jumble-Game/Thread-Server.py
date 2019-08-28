"""
Server side: open a socket on a port, listen for a message from a client,
and send an echo reply; echoes lines until eof when client closes socket;
spawns a thread to handle each client connection; threads share global
memory space with main thread; this is more portable than fork: threads
work on standard Windows systems, but process forks do not;
"""
import Jumble
import time, _thread as thread           # or use threading.Thread().start()
from socket import *                     # get socket constructor and constants
myHost = ''                              # server machine, '' means local host
myPort = 50007                           # listen on a non-reserved port number

sockobj = socket(AF_INET, SOCK_STREAM)           # make a TCP socket object
sockobj.bind((myHost, myPort))                   # bind it to server port number
sockobj.listen(5)                                # allow up to 5 pending connects

def now():
    return time.ctime(time.time())               # current time on the server

def handleClient(connection):                    # in spawned thread: reply
    time.sleep(1)                                # simulate a blocking activity
    jum = Jumble.jumble()                        # instantiates jumble object
    while True:                                  # read, write a client socket
        reply = jum.give_word()                  # runs the give_word() method in jumble object,
        connection.send(reply.encode())          #  tencodes data returned and sends it to socket
        a = connection.recv(1024)                # recieves 1024 bits of data from socket
        answer = a.decode()                      # decodes data recieved from socket
        if answer == 'exit':                     # checks whether the user entered exit and breaks if so
            break
        reply = jum.get_word(answer)             # sends the users response to jum.get_word() method,
        connection.send(reply.encode())          #  saves the response, encodes it and sends it to socket.
    connection.close()                           # closes connections when loop ends

def dispatcher():                                # listen until process killed
    while True:                                  # wait for next connection,
        (connection, address) = sockobj.accept()   # pass to thread for service
        print('Server connected by', address, end=' ')
        print('at', now())
        thread.start_new_thread(handleClient, (connection,))

dispatcher()
