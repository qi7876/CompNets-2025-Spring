import os
import ssl
import threading
import time
from socket import *


# Define thread process
def Server(tcpClisock, addr):
    BUFSIZE = 4096
    print("Received a connection from:", addr)
    
    try:
        # Receive request data
        data = tcpClisock.recv(BUFSIZE).decode()
        print(data)

        if len(data) == 0:
            tcpClisock.close()
            return

        # Parse request
        request_lines = data.split('\r\n')
        first_line = request_lines[0]
        method = first_line.split()[0]
        url = first_line.split()[1]
        
        print(f"Method: {method}, URL: {url}")

        # Handle HTTPS CONNECT method
        if method == "CONNECT":
            handle_https_connect(tcpClisock, url, data)
            return

        # Handle HTTP GET and POST
        if method in ["GET", "POST"]:
            handle_http_request(tcpClisock, method, url, data)
        else:
            # Unsupported method
            response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n"
            tcpClisock.send(response.encode())
            
    except Exception as e:
        print(f"Error handling request: {e}")
    finally:
        tcpClisock.close()

def handle_https_connect(tcpClisock, url, data):
    """Handle HTTPS CONNECT method for SSL tunneling"""
    try:
        # Parse host and port
        if ':' in url:
            host, port = url.split(':')
            port = int(port)
        else:
            host = url
            port = 443
            
        # Create connection to target server
        server_sock = socket(AF_INET, SOCK_STREAM)
        server_sock.connect((host, port))
        
        # Send 200 Connection Established to client
        response = "HTTP/1.1 200 Connection Established\r\n\r\n"
        tcpClisock.send(response.encode())
        
        # Start bidirectional data forwarding
        def forward_data(src, dst):
            try:
                while True:
                    data = src.recv(4096)
                    if not data:
                        break
                    dst.send(data)
            except:
                pass
            finally:
                src.close()
                dst.close()
        
        # Create threads for bidirectional forwarding
        client_to_server = threading.Thread(target=forward_data, args=(tcpClisock, server_sock))
        server_to_client = threading.Thread(target=forward_data, args=(server_sock, tcpClisock))
        
        client_to_server.start()
        server_to_client.start()
        
        client_to_server.join()
        server_to_client.join()
        
    except Exception as e:
        print(f"HTTPS CONNECT error: {e}")
        tcpClisock.close()

def handle_http_request(tcpClisock, method, url, data):
    """Handle HTTP GET and POST requests"""
    try:
        # Extract hostname and path
        if url.startswith('http://'):
            url = url[7:]  # Remove http://
        
        if '/' in url:
            host = url.split('/')[0]
            path = '/' + '/'.join(url.split('/')[1:])
        else:
            host = url
            path = '/'
            
        # Form cache filename
        filename = (host + path).replace("/", "_").replace(":", "_")
        print(f"Cache filename: {filename}")
        
        # Parse original request headers
        request_lines = data.split('\r\n')
        headers = {}
        body = ""
        
        # Find headers and body
        body_start = -1
        for i, line in enumerate(request_lines):
            if line == "":
                body_start = i + 1
                break
            elif i > 0:  # Skip first line (request line)
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip().lower()] = value.strip()
        
        # Get request body for POST
        if method == "POST" and body_start != -1:
            body = '\r\n'.join(request_lines[body_start:])
        
        # Check cache validity
        cache_valid = False
        cached_last_modified = None
        
        if os.path.exists(filename):
            print("Cache file exists, checking validity...")
            cache_valid, cached_last_modified = check_cache_validity(filename, host, path, headers)
        
        if cache_valid:
            print("Cache is valid, serving from cache")
            serve_from_cache(tcpClisock, filename)
        else:
            print("Cache miss or invalid, fetching from server")
            fetch_and_cache(tcpClisock, method, host, path, headers, body, filename, cached_last_modified)
            
    except Exception as e:
        print(f"HTTP request error: {e}")

def check_cache_validity(filename, host, path, headers):
    """Check if cached file is still valid using Last-Modified"""
    try:
        # Read cached file to get Last-Modified header
        with open(filename, 'rb') as f:
            cached_content = f.read()
        
        cached_text = cached_content.decode('utf-8', errors='ignore')
        
        # Extract Last-Modified from cached response
        if 'Last-Modified:' in cached_text:
            lines = cached_text.split('\r\n')
            for line in lines:
                if line.startswith('Last-Modified:'):
                    last_modified = line.split(':', 1)[1].strip()
                    print(f"Found Last-Modified in cache: {last_modified}")
                    
                    # Send conditional request to server
                    is_valid = validate_with_server(host, path, last_modified)
                    return is_valid, last_modified
        
        # If no Last-Modified header, cache is considered invalid
        print("No Last-Modified header found in cache")
        return False, None
    except Exception as e:
        print(f"Error checking cache validity: {e}")
        return False, None

def validate_with_server(host, path, last_modified):
    """Send If-Modified-Since request to validate cache"""
    try:
        print(f"Validating cache with server for {host}{path}")
        validation_sock = socket(AF_INET, SOCK_STREAM)
        validation_sock.settimeout(10)  # Add timeout
        validation_sock.connect((host, 80))
        
        request = f"HEAD {path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        request += f"If-Modified-Since: {last_modified}\r\n"
        request += f"Connection: close\r\n"
        request += "\r\n"
        
        validation_sock.send(request.encode())
        response = validation_sock.recv(4096).decode()
        validation_sock.close()
        
        print(f"Validation response: {response.split()[1] if len(response.split()) > 1 else 'Unknown'}")
        
        # Check if response is 304 Not Modified
        if "304 Not Modified" in response:
            print("Server returned 304 - cache is valid")
            return True
        elif "200 OK" in response:
            print("Server returned 200 - cache is stale")
            return False
        else:
            print("Unexpected validation response")
            return False
            
    except Exception as e:
        print(f"Cache validation failed: {e}")
        return False

def serve_from_cache(tcpClisock, filename):
    """Serve content from cache"""
    try:
        print(f"Serving from cache: {filename}")
        with open(filename, 'rb') as f:
            content = f.read()
        tcpClisock.send(content)
        print(f"Served {len(content)} bytes from cache")
    except Exception as e:
        print(f"Error serving from cache: {e}")

def fetch_and_cache(tcpClisock, method, host, path, headers, body, filename, cached_last_modified):
    """Fetch content from server and cache it"""
    try:
        print(f"Fetching from server: {host}{path}")
        # Create connection to web server
        server_sock = socket(AF_INET, SOCK_STREAM)
        server_sock.settimeout(30)  # Add timeout
        server_sock.connect((host, 80))
        
        # Build request
        request = f"{method} {path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        
        # Add If-Modified-Since if we have cached version
        if cached_last_modified:
            request += f"If-Modified-Since: {cached_last_modified}\r\n"
            print(f"Added If-Modified-Since: {cached_last_modified}")
        
        # Add other headers (except Host which we already added)
        for key, value in headers.items():
            if key.lower() not in ['host', 'connection']:
                request += f"{key}: {value}\r\n"
        
        request += f"Connection: close\r\n"
        request += "\r\n"
        
        # Add body for POST requests
        if method == "POST" and body:
            request += body
        
        # Send request to server
        server_sock.send(request.encode())
        
        # Receive response with proper buffering for large files
        response_data = b""
        content_length = None
        headers_received = False
        
        while True:
            chunk = server_sock.recv(4096)
            if not chunk:
                break
                
            response_data += chunk
            
            # Parse headers to get Content-Length
            if not headers_received and b'\r\n\r\n' in response_data:
                headers_received = True
                header_end = response_data.find(b'\r\n\r\n')
                header_text = response_data[:header_end].decode('utf-8', errors='ignore')
                
                for line in header_text.split('\r\n'):
                    if line.lower().startswith('content-length:'):
                        content_length = int(line.split(':', 1)[1].strip())
                        break
            
            # Check if we have received all data
            if headers_received and content_length:
                header_end = response_data.find(b'\r\n\r\n') + 4
                body_received = len(response_data) - header_end
                if body_received >= content_length:
                    break
        
        server_sock.close()
        
        # Check if server returned 304 Not Modified
        response_text = response_data.decode('utf-8', errors='ignore')
        status_line = response_text.split('\r\n')[0] if response_text else ""
        print(f"Server response: {status_line}")
        
        if "304 Not Modified" in response_text:
            print("Server returned 304, serving from cache")
            serve_from_cache(tcpClisock, filename)
            return
        
        # Send response to client
        tcpClisock.send(response_data)
        print(f"Sent {len(response_data)} bytes to client")
        
        # Cache the response only if it's a successful response
        if "200 OK" in response_text:
            try:
                with open(filename, 'wb') as f:
                    f.write(response_data)
                print(f"Cached response to {filename} ({len(response_data)} bytes)")
            except Exception as e:
                print(f"Error caching response: {e}")
        else:
            print(f"Not caching non-200 response: {status_line}")
            
    except Exception as e:
        print(f"Error fetching from server: {e}")
        # Send error response
        error_response = "HTTP/1.1 502 Bad Gateway\r\n\r\n"
        tcpClisock.send(error_response.encode())

# Main process of ProxyServer
if __name__ == "__main__":
    # Create a server socket, bind it to a port and start listening
    tcpSersock = socket(AF_INET, SOCK_STREAM)
    tcpSersock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    tcpSersock.bind(("", 8888))
    tcpSersock.listen(5)

    print("Enhanced Proxy Server ready to serve on port 8888...")
    print("Supports: HTTP GET/POST, HTTPS CONNECT, Cache validation, Large files")
    
    try:
        while True:
            tcpClisock, addr = tcpSersock.accept()
            thread = threading.Thread(target=Server, args=(tcpClisock, addr))
            thread.daemon = True
            thread.start()
    except KeyboardInterrupt:
        print("\nShutting down proxy server...")
    finally:
        tcpSersock.close()

