import socket
import sys


def http_get(host: str, port: int, file_path: str):
    socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        socket_connection.connect((host, port))
        request = (
            f"GET {file_path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        )
        socket_connection.sendall(request.encode())
        response = b""

        while True:
            data = socket_connection.recv(1024)
            if not data:
                break
            response += data

        return response.decode()
    except Exception as e:
        return f"Error: {e}"
    finally:
        socket_connection.close()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python client.py <host> <port> <file_path>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    file_path = sys.argv[3]

    response = http_get(host, port, file_path)
    print(response)

