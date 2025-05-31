import socket
import time

def test_large_file():
    """Test handling of files larger than 4KB"""
    print("Testing large file handling...")
    
    try:
        # Connect to proxy
        proxy_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy_sock.connect(('localhost', 8888))
        
        # Request a large file (>4KB)
        request = "GET http://httpbin.org/bytes/8192 HTTP/1.1\r\n"
        request += "Host: httpbin.org\r\n"
        request += "User-Agent: LargeFileTest/1.0\r\n"
        request += "\r\n"
        
        proxy_sock.send(request.encode())
        
        # Receive response
        response = b""
        content_length = None
        headers_received = False
        
        while True:
            try:
                data = proxy_sock.recv(4096)
                if not data:
                    break
                response += data
                
                # Parse Content-Length from headers
                if not headers_received and b'\r\n\r\n' in response:
                    headers_received = True
                    header_end = response.find(b'\r\n\r\n')
                    header_text = response[:header_end].decode('utf-8', errors='ignore')
                    
                    for line in header_text.split('\r\n'):
                        if line.lower().startswith('content-length:'):
                            content_length = int(line.split(':', 1)[1].strip())
                            break
                
                # Check if we have all data
                if headers_received and content_length:
                    header_end = response.find(b'\r\n\r\n') + 4
                    body_received = len(response) - header_end
                    if body_received >= content_length:
                        break
                        
            except:
                break
        
        proxy_sock.close()
        
        # Verify response
        response_text = response.decode('utf-8', errors='ignore')
        if "200 OK" in response_text:
            # Check if we received the expected amount of data
            if content_length and len(response) >= content_length + 100:  # Headers + content
                print(f"✓ Large file test passed (received {len(response)} bytes, expected ~{content_length + 100})")
                return True
            else:
                print(f"✗ Large file test failed - incomplete data (received {len(response)} bytes)")
                return False
        else:
            print("✗ Large file test failed - no 200 OK response")
            return False
            
    except Exception as e:
        print(f"✗ Large file test failed with error: {e}")
        return False

def test_content_length_parsing():
    """Test Content-Length header parsing"""
    print("Testing Content-Length parsing...")
    
    try:
        # Connect to proxy
        proxy_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy_sock.connect(('localhost', 8888))
        
        # Request with known Content-Length
        request = "GET http://httpbin.org/bytes/1000 HTTP/1.1\r\n"
        request += "Host: httpbin.org\r\n"
        request += "User-Agent: ContentLengthTest/1.0\r\n"
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
                if len(data) < 4096:  # Likely end of response
                    break
            except:
                break
        
        proxy_sock.close()
        
        response_text = response.decode('utf-8', errors='ignore')
        
        # Check for Content-Length header
        if "Content-Length:" in response_text and "200 OK" in response_text:
            # Extract Content-Length value
            for line in response_text.split('\r\n'):
                if line.startswith('Content-Length:'):
                    content_length = int(line.split(':', 1)[1].strip())
                    if content_length == 1000:
                        print(f"✓ Content-Length parsing test passed (found {content_length})")
                        return True
                    else:
                        print(f"✗ Unexpected Content-Length: {content_length}")
                        return False
            
            print("✗ Content-Length header not found in response")
            return False
        else:
            print("✗ Content-Length parsing test failed")
            return False
            
    except Exception as e:
        print(f"✗ Content-Length parsing test failed with error: {e}")
        return False

if __name__ == "__main__":
    print("=== Large File Handling Tests ===")
    
    test1 = test_large_file()
    time.sleep(1)
    test2 = test_content_length_parsing()
    
    if test1 and test2:
        print("✓ All large file handling tests passed!")
    else:
        print("✗ Some large file handling tests failed!")
