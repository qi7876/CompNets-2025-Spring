from socket import *
import os
import sys, getopt
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8
ICMP_DEST_UNREACHABLE = 3

# ICMP Destination Unreachable codes
ICMP_NET_UNREACHABLE = 0
ICMP_HOST_UNREACHABLE = 1
ICMP_PROTOCOL_UNREACHABLE = 2
ICMP_PORT_UNREACHABLE = 3
ICMP_FRAGMENTATION_NEEDED = 4
ICMP_SOURCE_ROUTE_FAILED = 5


def get_icmp_error_message(icmp_code):
    error_messages = {
        ICMP_NET_UNREACHABLE: "Destination network unreachable",
        ICMP_HOST_UNREACHABLE: "Destination host unreachable",
        ICMP_PROTOCOL_UNREACHABLE: "Destination protocol unreachable",
        ICMP_PORT_UNREACHABLE: "Destination port unreachable",
        ICMP_FRAGMENTATION_NEEDED: "Fragmentation needed and DF set",
        ICMP_SOURCE_ROUTE_FAILED: "Source route failed"
    }
    return error_messages.get(icmp_code, f"Unknown destination unreachable code: {icmp_code}")


def checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = string[count] * 256 + string[count + 1]
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
        if whatReady[0] == []:  # Timeout
            return None
        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        # Fill in start
        ipHeader = recPacket[:20]
        ipVerHlen, ipTos, ipTotalLen, ipId, ipFragOff, ipTTL, ipProto, ipChecksum, ipSrcIP, ipDestIP = struct.unpack(
            "!BBHHHBBHII", ipHeader)
        ipHeaderLength = (ipVerHlen & 0x0F) * 4
        # Fetch the ICMP header from the IP packet
        icmpHeader = recPacket[ipHeaderLength:ipHeaderLength + 8]
        icmpType, icmpCode, icmpChecksum, icmpID, icmpSequence = struct.unpack("!BBHHH", icmpHeader)

        # Handle ICMP Echo Reply
        if icmpType == 0 and icmpID == ID and icmpSequence == sequence:
            icmpData = recPacket[ipHeaderLength + 8:]
            data_bytes = len(icmpData)
            try:
                timeSent = struct.unpack("!d", icmpData[:struct.calcsize("!d")])[0]
                rtt = (timeReceived - timeSent) * 1000
                source_ip = addr[0]
                ttl_value = ipTTL
                return rtt, ttl_value, data_bytes, source_ip
            except struct.error:
                pass

        # Handle ICMP Destination Unreachable
        elif icmpType == ICMP_DEST_UNREACHABLE:
            # Extract the original IP header and ICMP header from the ICMP data
            originalIPHeader = recPacket[ipHeaderLength + 8:ipHeaderLength + 28]
            if len(originalIPHeader) >= 20:
                originalICMPHeader = recPacket[ipHeaderLength + 28:ipHeaderLength + 36]
                if len(originalICMPHeader) >= 8:
                    origIcmpType, origIcmpCode, origIcmpChecksum, origIcmpID, origIcmpSequence = struct.unpack("!BBHHH", originalICMPHeader)
                    # Check if this is a response to our ping
                    if origIcmpType == ICMP_ECHO_REQUEST and origIcmpID == ID and origIcmpSequence == sequence:
                        error_msg = get_icmp_error_message(icmpCode)
                        source_ip = addr[0]
                        return None, None, None, source_ip, error_msg
        # Fill in end

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

    mySocket.sendto(packet, (destAddr, 1))  # AF_INET address must be tuple, not str
    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object.


def doOnePing(destAddr, ID, sequence, timeout):
    icmp = getprotobyname("icmp")

    # SOCK_RAW is a powerful socket type. For more details:
    # http://sock-raw.org/papers/sock_raw
    # Fill in start
    try:
        mySocket = socket(AF_INET, SOCK_RAW, icmp)
    except Exception as e:
        print(f"Error creating socket: {e}")
        return None
    # Fill in end

    sendOnePing(mySocket, destAddr, ID, sequence)
    rtt = receiveOnePong(mySocket, destAddr, ID, sequence, timeout)

    mySocket.close()
    return rtt


def ping(dest, count):
    # timeout=1 means: If one second goes by without a reply from the server,
    # the client assumes that either the client's ping or the server's pong is lost
    timeout = 1

    myID = os.getpid() & 0xFFFF  # Return the current process i
    rtt_list = []
    loss = 0

    # Send ping requests to a server separated by approximately one second
    for i in range(count):
        result = doOnePing(dest, myID, i, timeout)

        # Fill in start
        # Print response information of each pong packet:
        # No pong packet, then display "Request timed out."
        # Receive pong packet, then display "Reply from host_ipaddr : bytes=… time=… TTL=…"
        if result:
            if len(result) == 4:  # Normal ping response
                rtt, ttl_value, data_bytes, ip_address = result
                rtt_list.append(rtt)
                print(f"Reply from {ip_address}: bytes={data_bytes} time={rtt:.3f}ms TTL={ttl_value}")
            elif len(result) == 5:  # ICMP error response
                _, _, _, ip_address, error_msg = result
                print(f"Reply from {ip_address}: {error_msg}")
                loss += 1
        else:
            print("Request timed out.")
            loss += 1

        # Fill in end

        time.sleep(1)  # one second

    # Fill in start

    # Print Ping statistics
    print(f"\n--- {dest} ping statistics ---:")
    loss_rate = (loss / count) * 100 if count > 0 else 0
    print(
        f"Sent = {count}, Received = {count - loss}, Lost = {loss} ({loss_rate:.1f}% loss),")

    if rtt_list:
        min_rtt = min(rtt_list)
        max_rtt = max(rtt_list)
        avg_rtt = sum(rtt_list) / len(rtt_list)
        print(f"RTT: Minimum = {min_rtt:.3f}ms, Maximum = {max_rtt:.3f}ms, Average = {avg_rtt:.3f}ms")
    else:
        print("RTT: Minimum = N/A, Maximum = N/A, Average = N/A")

    # Fill in end

    return


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('IcmpPing.py dest_host [-n <count>]')
        sys.exit()
    host = sys.argv[1]
    try:
        dest = gethostbyname(host)
    except:
        print('Can not find the host "%s". Please check your input, then try again.' % (host))
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
