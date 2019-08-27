from socket import *
import os
import sys
import struct
import time
import select
import binascii  

ICMP_ECHO_REQUEST = 8



def MyChecksum(hexlist):
    summ=0
    carry=0
    for i in range(0,len(hexlist),2):
        summ+=(hexlist[i]<< 8)  + hexlist[i+1]
        carry=summ>>16
        summ=(summ & 0xffff)  + carry

    while( summ != (summ & 0xffff)):
        carry=summ>>16
        summ=summ & 0xffffffff  + carry
    summ^=0xffff 
    return summ

    
def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout                  #Initialize variable to hold the time left before a timeout occurs.
    
    while 1:                            #Start continuous loop
        startedSelect = time.time()     #Check the socket and timeout
        whatReady = select.select(
            [mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:          #Loop exits if a timeout occurs.
            return "Request timed out..."
    
        timeReceived = time.time()      #Initialize variable to hold the time    
        recPacket, addr = mySocket.recvfrom(1024)
                                        #The ICMP header still starts at bit 160 or byte 20 however 
        icmp_header = recPacket[20:32]  #   due to the changes I had to make to how it's packed, the header
        rando, ty, checks, code, p_id, sequence = struct.unpack("hhHhHh", icmp_header) # is 12 bytes and thus extends to byte 32

        TS = struct.unpack("d",
                           recPacket[32:40]) #Since the data is saved as an 8 bit double variable and appended
        timeSent = TS[0]                #   to the end of the header it appears in bytes 32 to 40.
        
        if p_id == ID:                  #Since multiple processes can be pinging at once, this verifies that the data retrieved from the
            if code in range(1, 3):     #   socket has been retrieved by the proper process.
                return "Destination unreachable"
            elif code == 4:             #These internal if statements on the 'code' variable are used to detect and specify different errors.
                return "Fragmentation needed" 
            elif code == 5:
                return "Source route failed"
            else:
                ch = struct.pack("hxHhHh", ty, checks, 0, p_id,
                                 sequence) #Rebuilds the original data packet and sends it back into the socket.
                d = struct.pack("d", timeSent)
                pkt = ch + d
                mySocket.sendto(pkt, addr)
                return timeReceived - timeSent  #Returns the RTT

        timeLeft = timeLeft - howLongInSelect

        if timeLeft <= 0:
            return "Request timed out."
    
def sendOnePing(mySocket, destAddr, ID):
                                        #Packet header is type (8), code (8), checksum (16), id (16), sequence (16).
    myChecksum = 0                      #Initialize variable to hold checksum value.
    header = struct.pack("hxHhHh",
                         ICMP_ECHO_REQUEST,
                         myChecksum,
                         0, ID, 1)      #Packs together each item in the header (without checksum) with its specific byte structure.
    t = time.time()                     #Initializes a variable to hold the time before ping is sent.
    data = struct.pack("d", t)          #Initializes a variable to hold the byte value of the time given above.
    
    myChecksum =MyChecksum(
        [i for i in header] +
        [j for j in data])              #Calculate the correct checksum on the data and the dummy header.
    
   
    if sys.platform == 'darwin':        #Convert 16-bit integers from host to network byte order.
        myChecksum = htons(myChecksum) & 0xffff     
    else:
        myChecksum = htons(myChecksum)
    
    header = struct.pack("hxHhHh", ICMP_ECHO_REQUEST,
                         myChecksum,
                         0, ID, 1)      #Packs together each item in the header (with checksum) with its specific byte structure.
    
    packet = header + data              #Appends to header the byte value of the send time.
    print()                             #Done to ensure myChecksum is correctly recieved on other end of socket.
    mySocket.sendto(packet,
                    (destAddr, 1))      #Send data packet into socket, note AF_INET address must be tuple, not str.
            
    
    
def doOnePing(destAddr, timeout): 
    icmp = getprotobyname("icmp")       #Initialize variable and assign it the protocol value of ICMP.

    mySocket = socket(AF_INET,  
                      SOCK_RAW, icmp)   #Open up ICMP socket.
    
    myID = os.getpid() & 0xFFFF         #Initialize variable and assign it the clients current proccess ID
    sendOnePing(mySocket,
                destAddr, myID)         #Control transferred to sendOnePing( ) method.
    delay = receiveOnePing(mySocket,
                           myID,
                           timeout,
                           destAddr)    #Control transferred to recieveOnePing( ) method and save its return value to variable 'delay'.
    
    mySocket.close()                    #Close ICMP socket.
    return delay
    
def ping(num_pings, host, timeout=5):
                                        #The variable timeout is set to one so if one second goes by without a reply from the server,
                                        #   the client assumes that either the client's ping or the server's pong is lost.
    dest = gethostbyname(host)          #Initialize variable to hold the hosts IP address.
    L = []                              #Initialize list variable to hold all RTTs.
    start = time.time()                 #Time used to calculate Time Recieved.
    print("Pinging " + dest + " using Python:")
    num_sent = 0                        #Initialize variable to hold number of packets sent.
    num_lost = 0                        #Initialize variable to hold number of packets lost.
    print("")
                                        #Send ping requests to a server separated by approximately one second.
    while num_pings > 0:
        delay = doOnePing(dest, timeout) #Control transferred to doOnePing( ) method.
        num_sent += 1
        if isinstance(delay, str):      #If the return value of doOnePing( ) is a string that means that
            num_lost += 1               #   an error has occurred as each error/timeout returns a string. In the absence
            print(delay)                #   of a timeout or error a number is returned representing the RTT. 
        else:            
            L.append(delay)             #If the return value isn't a string then it's an RTT and will be appended to L
            print("Reply from", dest, ":  Time Received =",
                  round(time.time()-start, 3), "s   RTT =",
                  round(delay*1000, 3), "ms")
        num_pings -= 1                  #Decrement num_pings by 1 since 1 ping has been completed.
    avg = 0                             #Initialize variable to hold average RTT.
    minim = 100000000                   #Initialize variable to hold minimum RTT.
    maxim = 0                           #Initialize variable to hold maximum RTT.
    for i in L:                         #This loop calculates the avg, min and max RTT for the display at the bottom.
        avg += i
        if i < minim:
            minim = i
        if i > maxim:
            maxim = i
    if avg != 0:
        avg = avg/len(L)
    else:
        minim = 0
    print("\n\nPing statistics for", dest, ":")
    print("\t Packets: Sent =", num_sent, ", Received =", len(L),
          ", Lost =", num_lost ,"(", round((num_lost/num_sent), 2)*100, "% loss),")
    print("Approximate RTTs in milli-seconds:")
    print("\t Minimum =", round(minim*1000, 3), "ms, Maximum =",
          round(maxim*1000, 3), "ms, Average =", round(avg*1000, 3), "ms \n\n ") 
    return delay

def startUtility():
    while 1:
        host = input("Please enter the URL address you wish to ping or 'exit' if you wish to exit: ")
        
        if (host == "exit"):
            return 0
        else:
            num_pings = input("Please enter the number of pings you would like to send: ")
            ping(int(num_pings), host)

startUtility()

