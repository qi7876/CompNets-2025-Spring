"""
UDP Heartbeat Client

@auth: qi7876@outlook.com
"""

import socket
import sys
import time


def UDPHeartbeatClient(address: str, port: int, interval: float = 1.0, total_heartbeats: int = 20):
    """
    UDP Heartbeat Client

    :param address: The address of the server to send heartbeats to.
    :param port: The port of the server to send heartbeats to.
    :param interval: The interval between heartbeats in seconds.
    :param total_heartbeats: Total number of heartbeats to send.
    :return: None
    """
    # Create socket instance.
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    print(f"Starting UDP Heartbeat Client to {address}:{port}")
    print(f"Sending {total_heartbeats} heartbeats with {interval}s interval")
    
    for sequence_number in range(1, total_heartbeats + 1):
        current_time = time.time()
        heartbeat_message = f"Heartbeat {sequence_number} {current_time}"
        
        try:
            client_socket.sendto(heartbeat_message.encode(), (address, port))
            print(f"Sent heartbeat {sequence_number} at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}")
        except Exception as e:
            print(f"Error sending heartbeat {sequence_number}: {e}")
        
        time.sleep(interval)
    
    print("Heartbeat client finished")
    client_socket.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python UDPHeartbeatClient.py <address> <port> [interval] [total_heartbeats]")
        sys.exit(1)

    address = sys.argv[1]
    port = int(sys.argv[2])
    interval = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    total_heartbeats = int(sys.argv[4]) if len(sys.argv) > 4 else 20

    UDPHeartbeatClient(address, port, interval, total_heartbeats)
