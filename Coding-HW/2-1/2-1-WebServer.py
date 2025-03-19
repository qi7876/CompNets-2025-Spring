from socket import *
import sys

# AF_INET is the address family for IPv4
# SOCK_STREAM is the socket type for TCP
serverSocket = socket(AF_INET, SOCK_STREAM)

# Prepare a sever socket
# Fill in start
serverSocket.bind(("", 7876))
serverSocket.listen(1)
# Fill in end

while True:
    # Establish the connection
    print("The server is ready to receive")

    # Set up a new connection from the client
    connectionSocket, addr = serverSocket.accept()

    try:
        # Receives the request message from the client
        message = connectionSocket.recv(1024).decode()

        # Extract the path of the requested object from the message
        # The path is the second part of HTTP header, identified by [1]
        filename = message.split()[1]

        # Because the extracted path of the HTTP request includes
        # a character '/', we read the path from the second character
        f = open(filename[1:])

        # Store the entire contenet of the requested file in a temporary buffer
        outputdata = f.read()

        # Send the HTTP response header line to the connection socket
        # Fill in start
        print("Find file:", filename[1:])
        connectionSocket.send("HTTP/1.1 200 OK\r\n".encode())
        connectionSocket.send("Content-Type: text/html\r\n".encode())
        connectionSocket.send("\r\n".encode())
        # Fill in end

        # Send the content of the requested file to the connection socket
        for i in range(0, len(outputdata)):
            connectionSocket.send(outputdata[i].encode())

        # Close the client connection socket
        connectionSocket.close()

    except IOError:
        # Send HTTP response message for file not found
        # Fill in start
        print("File not found:", filename[1:])
        connectionSocket.send("HTTP/1.1 404 Not Found\r\n".encode())
        connectionSocket.send("Content-Type: text/html\r\n".encode())
        connectionSocket.send("\r\n".encode())
        connectionSocket.send(
            "<html><body><h1>404 Not Found</h1></body></html>".encode()
        )
        # Fill in end

        # Close the client connection socket
        # Fill in start
        connectionSocket.close()
        # Fill in end

serverSocket.close()

# Terminate the program after sending the corresponding data
sys.exit()
