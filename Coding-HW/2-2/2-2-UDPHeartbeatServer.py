"""
UDP Heartbeat Server

@auth: qi7876@outlook.com
"""

import socket
import threading
import time


class UDPHeartbeatServer:
    def __init__(self, port: int, timeout: float = 5.0):
        """
        Initialize UDP Heartbeat Server
        
        :param port: Port to listen on
        :param timeout: Timeout in seconds to consider client stopped
        """
        self.port = port
        self.timeout = timeout
        self.clients = {}  # {address: {'last_seq': int, 'last_time': float, 'expected_seq': int}}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = True
        
    def start_server(self):
        """Start the heartbeat server"""
        self.server_socket.bind(('', self.port))
        print(f"UDP Heartbeat Server listening on port {self.port}")
        print(f"Client timeout set to {self.timeout} seconds")
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_clients)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        try:
            while self.running:
                self.handle_heartbeat()
        except KeyboardInterrupt:
            print("\nServer shutting down...")
        finally:
            self.server_socket.close()
    
    def handle_heartbeat(self):
        """Handle incoming heartbeat messages"""
        try:
            message, client_address = self.server_socket.recvfrom(1024)
            receive_time = time.time()
            
            message_str = message.decode()
            parts = message_str.split()
            
            if len(parts) >= 3 and parts[0] == "Heartbeat":
                sequence_number = int(parts[1])
                send_time = float(parts[2])
                
                # Calculate time difference
                time_diff = receive_time - send_time
                
                # Update client info
                if client_address not in self.clients:
                    self.clients[client_address] = {
                        'last_seq': 0,
                        'last_time': receive_time,
                        'expected_seq': 1
                    }
                    print(f"New client connected: {client_address}")
                
                client_info = self.clients[client_address]
                
                # Check for packet loss
                if sequence_number != client_info['expected_seq']:
                    if sequence_number > client_info['expected_seq']:
                        lost_packets = sequence_number - client_info['expected_seq']
                        print(f"PACKET LOSS detected from {client_address}: "
                              f"Expected seq {client_info['expected_seq']}, got {sequence_number}. "
                              f"{lost_packets} packet(s) lost.")
                    else:
                        print(f"Out-of-order packet from {client_address}: "
                              f"Expected seq {client_info['expected_seq']}, got {sequence_number}")
                
                # Update client info
                client_info['last_seq'] = sequence_number
                client_info['last_time'] = receive_time
                client_info['expected_seq'] = max(sequence_number + 1, client_info['expected_seq'])
                
                print(f"Heartbeat from {client_address}: seq={sequence_number}, "
                      f"time_diff={time_diff*1000:.3f}ms, "
                      f"timestamp={time.strftime('%H:%M:%S', time.localtime(receive_time))}")
                
        except socket.timeout:
            pass
        except Exception as e:
            print(f"Error handling heartbeat: {e}")
    
    def monitor_clients(self):
        """Monitor clients for timeouts"""
        while self.running:
            current_time = time.time()
            disconnected_clients = []
            
            for client_address, client_info in self.clients.items():
                if current_time - client_info['last_time'] > self.timeout:
                    print(f"CLIENT TIMEOUT: {client_address} - No heartbeat for {self.timeout}s. "
                          f"Client application may have stopped.")
                    disconnected_clients.append(client_address)
            
            # Remove disconnected clients
            for client_address in disconnected_clients:
                del self.clients[client_address]
            
            time.sleep(1)  # Check every second


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python UDPHeartbeatServer.py <port> [timeout]")
        sys.exit(1)
    
    port = int(sys.argv[1])
    timeout = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
    
    server = UDPHeartbeatServer(port, timeout)
    server.start_server()
