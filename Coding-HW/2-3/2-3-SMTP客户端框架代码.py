from socket import *
import base64
import os
import mimetypes

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
password = base64.b64encode("XXXXXXXXXXXXXXXXXXXX".encode()).decode()

# File attachments (add your file paths here)
attachments = [
    "test.txt",
    "image.png"
]

def encode_file_attachment(filepath):
    """Encode file as base64 attachment"""
    filename = os.path.basename(filepath)
    mime_type, _ = mimetypes.guess_type(filepath)
    if mime_type is None:
        mime_type = "application/octet-stream"
    
    with open(filepath, "rb") as f:
        file_data = f.read()
    
    encoded_data = base64.b64encode(file_data).decode()
    
    # Split into lines of 76 characters
    encoded_lines = [encoded_data[i:i+76] for i in range(0, len(encoded_data), 76)]
    encoded_content = "\r\n".join(encoded_lines)
    
    return filename, mime_type, encoded_content

def create_mime_message(subject, msg, attachments):
    """Create MIME multipart message"""
    boundary = "----=_NextPart_000_0000_01D00000.00000000"
    
    # MIME headers
    mime_headers = f"Subject: {subject}\r\n"
    mime_headers += f"MIME-Version: 1.0\r\n"
    mime_headers += f"Content-Type: multipart/mixed; boundary=\"{boundary}\"\r\n"
    mime_headers += "\r\n"
    
    # Text part
    message_body = f"--{boundary}\r\n"
    message_body += f"Content-Type: text/plain; charset=utf-8\r\n"
    message_body += f"Content-Transfer-Encoding: 7bit\r\n"
    message_body += f"\r\n"
    message_body += f"{msg}\r\n"
    
    # File attachments
    for filepath in attachments:
        if os.path.exists(filepath):
            filename, mime_type, encoded_content = encode_file_attachment(filepath)
            
            message_body += f"\r\n--{boundary}\r\n"
            message_body += f"Content-Type: {mime_type}; name=\"{filename}\"\r\n"
            message_body += f"Content-Transfer-Encoding: base64\r\n"
            message_body += f"Content-Disposition: attachment; filename=\"{filename}\"\r\n"
            message_body += f"\r\n"
            message_body += f"{encoded_content}\r\n"
    
    # End boundary
    message_body += f"\r\n--{boundary}--\r\n"
    
    return mime_headers + message_body

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
if attachments:
    message_to_send = create_mime_message(subject, msg, attachments)
else:
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
