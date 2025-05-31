import socket
import time

def test_http_get():
    """Test HTTP GET through proxy"""
    print("Testing HTTP GET...")
    
    try:
        # Connect to proxy
        proxy_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy_sock.connect(('localhost', 8888))
        
        # Send GET request
        request = "GET http://httpbin.org/get HTTP/1.1\r\n"
        request += "Host: httpbin.org\r\n"
        request += "User-Agent: ProxyTest/1.0\r\n"
        request += "\r\n"
        
        proxy_sock.send(request.encode())
        
        # Receive response
        response = b""
        while True:
            try:
                data = proxy_sock.recv(4096)
                if not data:
                    break
                response += data
                if b"\r\n\r\n" in response and len(data) < 4096:
                    break
            except:
                break
        
        proxy_sock.close()
        
        response_text = response.decode('utf-8', errors='ignore')
        if "200 OK" in response_text:
            print("✓ HTTP GET test passed")
            return True
        else:
            print("✗ HTTP GET test failed")
            print(f"Response: {response_text[:200]}...")
            return False
            
    except Exception as e:
        print(f"✗ HTTP GET test failed with error: {e}")
        return False

def test_http_post():
    """Test HTTP POST through proxy"""
    print("Testing HTTP POST...")
    
    try:
        # Connect to proxy
        proxy_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy_sock.connect(('localhost', 8888))
        
        # POST data
        post_data = '{"test": "data", "proxy": "verification"}'
        
        # Send POST request
        request = "POST http://httpbin.org/post HTTP/1.1\r\n"
        request += "Host: httpbin.org\r\n"
        request += "Content-Type: application/json\r\n"
        request += f"Content-Length: {len(post_data)}\r\n"
        request += "User-Agent: ProxyTest/1.0\r\n"
        request += "\r\n"
        request += post_data
        
        proxy_sock.send(request.encode())
        
        # Receive response
        response = b""
        while True:
            try:
                data = proxy_sock.recv(4096)
                if not data:
                    break
                response += data
                if b"\r\n\r\n" in response and len(data) < 4096:
                    break
            except:
                break
        
        proxy_sock.close()
        
        response_text = response.decode('utf-8', errors='ignore')
        if "200 OK" in response_text and "test" in response_text and "data" in response_text:
            print("✓ HTTP POST test passed")
            return True
        else:
            print("✗ HTTP POST test failed")
            print(f"Response: {response_text[:200]}...")
            return False
            
    except Exception as e:
        print(f"✗ HTTP POST test failed with error: {e}")
        return False

if __name__ == "__main__":
    print("=== Basic HTTP Tests ===")
    get_result = test_http_get()
    time.sleep(1)
    post_result = test_http_post()
    
    if get_result and post_result:
        print("✓ All basic HTTP tests passed!")
    else:
        print("✗ Some basic HTTP tests failed!")
