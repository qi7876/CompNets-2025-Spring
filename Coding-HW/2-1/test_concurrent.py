import threading
import time
import socket

def send_request(host, port, path, thread_id):
    """发送HTTP请求"""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        
        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        
        start_time = time.time()
        client_socket.sendall(request.encode())
        
        response = b""
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            response += data
        
        end_time = time.time()
        
        print(f"Thread {thread_id}: Request completed in {end_time - start_time:.2f} seconds")
        print(f"Thread {thread_id}: Response length: {len(response)} bytes")
        
        client_socket.close()
        
    except Exception as e:
        print(f"Thread {thread_id}: Error - {e}")

def test_concurrent_requests(host='localhost', port=8080, num_threads=5):
    """测试并发请求"""
    print(f"Testing {num_threads} concurrent requests to {host}:{port}")
    
    threads = []
    start_time = time.time()
    
    for i in range(num_threads):
        thread = threading.Thread(
            target=send_request,
            args=(host, port, '/index.html', i+1)
        )
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    print(f"\nAll {num_threads} requests completed in {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    test_concurrent_requests()
