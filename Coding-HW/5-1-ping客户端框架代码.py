from socket import *
import os
import sys, getopt
import struct
import time
import select
import binascii  

ICMP_ECHO_REQUEST = 8

def checksum(string): 
    csum = 0
    countTo = (len(string) // 2) * 2  
    count = 0

    while count < countTo:
        thisVal = string[count] * 256 + string[count+1]
        csum = csum + thisVal 
        csum = csum & 0xffffffff  
        count = count + 2
        
    if countTo < len(string):
        csum = csum + string[len(string) - 1]
        csum = csum & 0xffffffff 
        
    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum 
    answer = answer & 0xffff 
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer 

def receiveOnePong(mySocket, destAddr, ID, sequence, timeout):
    timeLeft = timeout
    
    while 1: 
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []: # Timeout
            return None
        timeReceived = time.time() 
        recPacket, addr = mySocket.recvfrom(1024)
                
        #Fill in start

        #Fetch the ICMP header from the IP packet
        
        #Fill in end
        
        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return None


def sendOnePing(mySocket, destAddr, ID, sequence):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)

    myChecksum = 0
    # Make a dummy header with a 0 checksum
    # struct -- Interpret strings as packed binary data
    header = struct.pack("!BBHHH", ICMP_ECHO_REQUEST, 0, myChecksum, ID, sequence)
    data = struct.pack("!d", time.time())

    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)
    
    # Get the right checksum, and put in the header
    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network byte order
        myChecksum = htons(myChecksum) & 0xffff         
    else:
        myChecksum = htons(myChecksum)
        
    header = struct.pack("!BBHHH", ICMP_ECHO_REQUEST, 0, myChecksum, ID, sequence)
    packet = header + data
    
    mySocket.sendto(packet, (destAddr, 1)) # AF_INET address must be tuple, not str
    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object.

def doOnePing(destAddr, ID, sequence, timeout): 
    icmp = getprotobyname("icmp")

    # SOCK_RAW is a powerful socket type. For more details: 
    #http://sock-raw.org/papers/sock_raw
    #Fill in start

    #Create Socket here

    #Fill in end
        
    sendOnePing(mySocket, destAddr, ID, sequence)
    rtt = receiveOnePong(mySocket, destAddr, ID, sequence, timeout)
    
    mySocket.close()
    return rtt
    
def ping(dest, count):
    # timeout=1 means: If one second goes by without a reply from the server,
    # the client assumes that either the client's ping or the server's pong is lost
    timeout = 1

    myID = os.getpid() & 0xFFFF  # Return the current process i
    loss = 0

    # Send ping requests to a server separated by approximately one second
    for i in range(count) :  
        result = doOnePing(dest, myID, i, timeout)

        #Fill in start

        #Print response information of each pong packet:
        #No pong packet, then display "Request timed out."
        #Receive pong packet, then display "Reply from host_ipaddr : bytes=… time=… TTL=…"

        #Fill in end

        time.sleep(1)# one second

    #Fill in start

    #Print Ping statistics

    #Fill in end

    return

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('IcmpPing.py dest_host [-n <count>]')
        sys.exit()
    host = sys.argv[1]
    try:
        dest = gethostbyname(host)
    except:
        print('Can not find the host "%s". Please check your input, then try again.'%(host))
        exit()
    
    count = 4
    try:
        opts, args = getopt.getopt(sys.argv[2:], "n:")
    except getopt.GetoptError:
        print('IcmpPing.py dest_host [-n <count>]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-n':
            count = int(arg)

    print("Pinging " + host + " [" + dest + "] using Python:")
    print("")
    ping(dest, count)
