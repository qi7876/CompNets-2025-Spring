from socket import *
import base64

# Mail content
subject = "I love computer networks!"
contenttype = "text/plain"
msg = "I love computer networks!"
endmsg = "\r\n.\r\n"

# Choose a mail server (e.g. Google mail server) and call it mailserver
mailserver = "mail.std.uestc.edu.cn"

# Sender and reciever
fromaddress = "2023010905015@std.uestc.edu.cn"
toaddress = "1181421250@qq.com"

# Auth information (Encode with base64)
username = base64.b64encode("2023010905015@std.uestc.edu.cn".encode()).decode()
password = base64.b64encode("tYjxiq-qimrat-8biqsu".encode()).decode()

# Create socket called clientSocket and establish a TCP connection with mailserver
# Fill-in-start
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((mailserver, 25))
# Fill-in-end

recv = clientSocket.recv(1024).decode()
print(recv)

# Send HELO command and print server response.
# Fill-in-start
clientSocket.sendall(f"HELO {mailserver}\r\n".encode())
recv = clientSocket.recv(1024).decode()
print(recv)
# Fill-in-end

# Send AUTH LOGIN command and print server response.
clientSocket.sendall("AUTH LOGIN\r\n".encode())
recv = clientSocket.recv(1024).decode()
print(recv)


clientSocket.sendall((username + "\r\n").encode())
recv = clientSocket.recv(1024).decode()
print(recv)

clientSocket.sendall((password + "\r\n").encode())
recv = clientSocket.recv(1024).decode()
print(recv)

# Send MAIL FROM command and print server response.
# Fill-in-start
clientSocket.sendall(("MAIL FROM: <" + fromaddress + ">\r\n").encode())
recv = clientSocket.recv(1024).decode()
print(recv)
# Fill-in-end

# Send RCPT TO command and print server response.
# Fill-in-start
clientSocket.sendall(("RCPT TO: <" + toaddress + ">\r\n").encode())
recv = clientSocket.recv(1024).decode()
print(recv)
# Fill-in-end

# Send DATA command and print server response.
# Fill-in-start
clientSocket.sendall("DATA\r\n".encode())
recv = clientSocket.recv(1024).decode()
print(recv)
# Fill-in-end

# Send message data.
# Fill-in-start
message_to_send = f"Subject: {subject}\r\nContent-Type: {contenttype}\r\n\r\n{msg}\r\n"
clientSocket.sendall(message_to_send.encode())
# Fill-in-end

# Message ends with a single period and print server response.
# Fill-in-start
clientSocket.sendall(endmsg.encode())
recv = clientSocket.recv(1024).decode()
print(recv)
# Fill-in-end

# Send QUIT command and print server response.
# Fill-in-start
clientSocket.sendall(("QUIT\r\n").encode())
recv = clientSocket.recv(1024).decode()
print(recv)
# Fill-in-end

# Close connection
clientSocket.close()
