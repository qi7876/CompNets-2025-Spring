import os
import socket
import sys
import threading
from datetime import datetime


class MultiThreadWebServer:
    def __init__(self, host="localhost", port=8080):
        self.host = host
        self.port = port
        self.server_socket = None

    def start_server(self):
        """启动服务器主线程"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"Multi-threaded Web Server started on {self.host}:{self.port}")

            while True:
                client_socket, client_address = self.server_socket.accept()
                print(f"Connection from {client_address}")

                # 为每个客户端创建独立线程
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.daemon = True
                client_thread.start()

        except KeyboardInterrupt:
            print("\nShutting down server...")
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.stop_server()

    def handle_client(self, client_socket, client_address):
        """处理单个客户端请求"""
        try:
            # 接收HTTP请求
            request_data = client_socket.recv(1024).decode("utf-8")
            if not request_data:
                return

            print(f"Thread {threading.current_thread().ident}: Handling request from {client_address}")

            # 解析HTTP请求
            request_lines = request_data.split("\r\n")
            if not request_lines:
                self.send_error_response(client_socket, 400, "Bad Request")
                return

            request_line = request_lines[0]
            parts = request_line.split()

            if len(parts) != 3:
                self.send_error_response(client_socket, 400, "Bad Request")
                return

            method, path, version = parts

            if method != "GET":
                self.send_error_response(client_socket, 405, "Method Not Allowed")
                return

            # 处理GET请求
            self.handle_get_request(client_socket, path)

        except Exception as e:
            print(f"Error handling client {client_address}: {e}")
            self.send_error_response(client_socket, 500, "Internal Server Error")
        finally:
            client_socket.close()
            print(f"Thread {threading.current_thread().ident}: Connection closed for {client_address}")

    def handle_get_request(self, client_socket, path):
        """处理GET请求"""
        # 移除路径开头的斜杠并处理根路径
        if path == "/":
            path = "/index.html"

        file_path = path.lstrip("/")

        try:
            # 检查文件是否存在
            if os.path.exists(file_path) and os.path.isfile(file_path):
                with open(file_path, "rb") as file:
                    content = file.read()

                # 确定内容类型
                content_type = self.get_content_type(file_path)

                # 发送成功响应
                self.send_success_response(client_socket, content, content_type)
            else:
                self.send_error_response(client_socket, 404, "Not Found")

        except IOError:
            self.send_error_response(client_socket, 500, "Internal Server Error")

    def send_success_response(self, client_socket, content, content_type):
        """发送成功响应"""
        response_headers = f"""HTTP/1.1 200 OK\r
Date: {datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")}\r
Server: MultiThreadWebServer/1.0\r
Content-Type: {content_type}\r
Content-Length: {len(content)}\r
Connection: close\r
\r
"""

        client_socket.sendall(response_headers.encode("utf-8"))
        client_socket.sendall(content)

    def send_error_response(self, client_socket, status_code, status_text):
        """发送错误响应"""
        error_content = f"""<html>
<head><title>{status_code} {status_text}</title></head>
<body>
<h1>{status_code} {status_text}</h1>
<p>The requested resource could not be found or accessed.</p>
<hr>
<em>MultiThreadWebServer/1.0</em>
</body>
</html>"""

        response_headers = f"""HTTP/1.1 {status_code} {status_text}\r
Date: {datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")}\r
Server: MultiThreadWebServer/1.0\r
Content-Type: text/html\r
Content-Length: {len(error_content)}\r
Connection: close\r
\r
"""

        client_socket.sendall(response_headers.encode("utf-8"))
        client_socket.sendall(error_content.encode("utf-8"))

    def get_content_type(self, file_path):
        """根据文件扩展名确定内容类型"""
        if file_path.endswith(".html") or file_path.endswith(".htm"):
            return "text/html"
        elif file_path.endswith(".css"):
            return "text/css"
        elif file_path.endswith(".js"):
            return "application/javascript"
        elif file_path.endswith(".jpg") or file_path.endswith(".jpeg"):
            return "image/jpeg"
        elif file_path.endswith(".png"):
            return "image/png"
        elif file_path.endswith(".gif"):
            return "image/gif"
        else:
            return "text/plain"

    def stop_server(self):
        """停止服务器"""
        if self.server_socket:
            self.server_socket.close()


if __name__ == "__main__":
    if len(sys.argv) == 3:
        host = sys.argv[1]
        port = int(sys.argv[2])
    elif len(sys.argv) == 2:
        host = "localhost"
        port = int(sys.argv[1])
    else:
        host = "localhost"
        port = 8080

    server = MultiThreadWebServer(host, port)
    server.start_server()
