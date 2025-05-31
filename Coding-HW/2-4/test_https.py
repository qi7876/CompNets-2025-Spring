import socket
import ssl
import time

def test_https_connect():
    """Test HTTPS CONNECT method"""
    print("Testing HTTPS CONNECT...")
    
    try:
        # Connect to proxy
        proxy_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy_sock.connect(('localhost', 8888))
        
        # Send CONNECT request
        connect_request = "CONNECT httpbin.org:443 HTTP/1.1\r\n"
        connect_request += "Host: httpbin.org:443\r\n"
        connect_request += "\r\n"
        
        proxy_sock.send(connect_request.encode())
        
        # Receive CONNECT response
        response = proxy_sock.recv(1024).decode()
        
        if "200 Connection Established" in response:
            print("✓ HTTPS CONNECT establishment successful")
            
            # Wrap socket with SSL
            ssl_context = ssl.create_default_context()
            ssl_sock = ssl_context.wrap_socket(proxy_sock, server_hostname='httpbin.org')
            
            # Send HTTPS request
            https_request = "GET /get HTTP/1.1\r\n"
            https_request += "Host: httpbin.org\r\n"
            https_request += "User-Agent: HTTPSTest/1.0\r\n"
            https_request += "\r\n"
            
            ssl_sock.send(https_request.encode())
            
            # Receive HTTPS response
            https_response = b""
            while True:
                try:
                    data = ssl_sock.recv(4096)
                    if not data:
                        break
                    https_response += data
                    if len(data) < 4096:
                        break
                except:
                    break
            
            ssl_sock.close()
            
            https_response_text = https_response.decode('utf-8', errors='ignore')
            if "200 OK" in https_response_text:
                print("✓ HTTPS request through proxy successful")
                return True
            else:
                print(f"✗ HTTPS request failed: {https_response_text[:100]}...")
                return False
        else:
            print(f"✗ CONNECT failed: {response}")
            return False
            
    except Exception as e:
        print(f"✗ HTTPS CONNECT test failed with error: {e}")
        return False

def test_https_tunneling():
    """Test HTTPS tunneling functionality"""
    print("Testing HTTPS tunneling...")
    
    try:
        # Connect to proxy
        proxy_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy_sock.connect(('localhost', 8888))
        
        # Send CONNECT request for a different HTTPS site
        connect_request = "CONNECT www.google.com:443 HTTP/1.1\r\n"
        connect_request += "Host: www.google.com:443\r\n"
        connect_request += "\r\n"
        
        proxy_sock.send(connect_request.encode())
        
        # Receive CONNECT response
        response = proxy_sock.recv(1024).decode()
        
        if "200 Connection Established" in response:
            # Create SSL context and wrap socket
            ssl_context = ssl.create_default_context()
            ssl_sock = ssl_context.wrap_socket(proxy_sock, server_hostname='www.google.com')
            
            # Send minimal HTTPS request
            https_request = "GET / HTTP/1.1\r\n"
            https_request += "Host: www.google.com\r\n"
            https_request += "User-Agent: TunnelTest/1.0\r\n"
            https_request += "\r\n"
            
            ssl_sock.send(https_request.encode())
            
            # Receive response (just check for any valid HTTP response)
            https_response = ssl_sock.recv(4096)
            ssl_sock.close()
            
            if https_response and (b"200 OK" in https_response or b"301" in https_response or b"302" in https_response):
                print("✓ HTTPS tunneling test passed")
                return True
            else:
                print("✗ HTTPS tunneling test failed - no valid response")
                return False
        else:
            print(f"✗ CONNECT for tunneling failed: {response}")
            return False
            
    except Exception as e:
        print(f"✗ HTTPS tunneling test failed with error: {e}")
        return False

if __name__ == "__main__":
    print("=== HTTPS Support Tests ===")
    
    test1 = test_https_connect()
    time.sleep(2)
    test2 = test_https_tunneling()
    
    if test1 and test2:
        print("✓ All HTTPS support tests passed!")
    else:
        print("✗ Some HTTPS support tests failed!")
