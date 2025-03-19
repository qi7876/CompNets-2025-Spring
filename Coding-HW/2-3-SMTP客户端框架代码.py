from socket import *
import base64

# Mail content
subject = "I love computer networks!"
contenttype = "text/plain"
msg = "I love computer networks!"
endmsg = "\r\n.\r\n"

# Choose a mail server (e.g. Google mail server) and call it mailserver
mailserver =  #Fill-in-start  #Fill-in-end

# Sender and reciever
fromaddress =  #Fill-in-start  #Fill-in-end
toaddress =  #Fill-in-start  #Fill-in-end

# Auth information (Encode with base64)
username =   #Fill-in-start  #Fill-in-end
password =  #Fill-in-start  #Fill-in-end

# Create socket called clientSocket and establish a TCP connection with mailserver
#Fill-in-start
#Fill-in-end

recv = clientSocket.recv(1024) .decode()
print(recv)

# Send HELO command and print server response.
#Fill-in-start
#Fill-in-end

# Send AUTH LOGIN command and print server response.
clientSocket.sendall('AUTH LOGIN\r\n'.encode())
recv = clientSocket.recv(1024).decode()
print(recv)

clientSocket.sendall((username + '\r\n').encode())
recv = clientSocket.recv(1024).decode()
print(recv)

clientSocket.sendall((password + '\r\n').encode())
recv = clientSocket.recv(1024).decode()
print(recv)

# Send MAIL FROM command and print server response.
#Fill-in-start
#Fill-in-end

# Send RCPT TO command and print server response.
#Fill-in-start
#Fill-in-end

# Send DATA command and print server response.
#Fill-in-start
#Fill-in-end

# Send message data.
#Fill-in-start
#Fill-in-end

# Message ends with a single period and print server response.
#Fill-in-start
#Fill-in-end

# Send QUIT command and print server response.
#Fill-in-start
#Fill-in-end

# Close connection
clientSocket.close()
