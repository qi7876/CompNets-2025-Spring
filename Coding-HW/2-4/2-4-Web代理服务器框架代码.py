from socket import *
import threading
import os


# Define thread process
def Server(tcpClisock, addr):
    BUFSIZE = 1024
    print("Received a connection from:", addr)
    data = tcpClisock.recv(BUFSIZE).decode()
    print(data)

    if len(data):
        # Extract the filename from the received message
        getFile = data.split()[1]
        print("getFile:", getFile)

        # Form a legal filename
        filename = getFile.replace("/", "_")
        print("filename:", filename)

        # Check wether the file exist in the cache
        if os.path.exists(filename):
            print("File exist")
            # ProxyServer finds a cache hit and generates a response message
            f = open(filename, "r")
            CACHE_PAGE = f.read()
            # ProxyServer sends the cache to the client
            tcpClisock.send(CACHE_PAGE.encode())
            print("Send the cache to the client")
            tcpClisock.close()
        else:
            print("File not exist")
            # Handling for file not found in cache
            # Create a socket on the ProxyServer
            c = socket(AF_INET, SOCK_STREAM)
            try:
                # Connect to the WebServer socket to port 80
                hostn = getFile.partition("/")[2].partition("/")[0]
                c.connect((hostn, 80))
                print("Connect to", hostn)

                # Some information in client request must be replaced before it can be sent to the server
                new_file = "".join(getFile.partition("/")[2].partition("/")[1:])
                modified_request_lines = []
                modified_request_lines.append(f"GET {new_file} HTTP/1.1")
                modified_request_lines.append(f"Host: {hostn}")

                origin_request = data.split("\r\n")

                for i in range(len(origin_request) - 2):
                    if origin_request[i + 2] != "":
                        modified_request_lines.append(origin_request[i + 2])

                modified_request = "\r\n".join(modified_request_lines) + "\r\n\r\n"

                # Send the modified client request to the server
                c.send(modified_request.encode())

                # Read the response into buffer
                buff = c.recv(4096)
                print("recvbuff len:", len(buff))

                # Send the response in the buffer to client socket
                tcpClisock.send(buff)
                print("Send to client\r\n")
                # Create a new file to save the response in the cache for the requested file
                tmpFile = open("./" + filename, "w")
                tmpFile.write(buff.decode())
                tmpFile.close()
            except:
                print("Illegal request")
            tcpClisock.close()


# Main process of  ProxyServer
if __name__ == "__main__":
    # Create a server socket, bind it to a port and start listening
    tcpSersock = socket(AF_INET, SOCK_STREAM)
    tcpSersock.bind(("", 8888))
    tcpSersock.listen(5)

    print("Ready to serve......\n")
    while True:
        tcpClisock, addr = tcpSersock.accept()
        thread = threading.Thread(target=Server, args=(tcpClisock, addr))
        thread.start()
    tcpSersock.close()

