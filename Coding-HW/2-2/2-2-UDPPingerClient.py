"""
UDP Pinger Client

@auth: qi7876@outlook.com
"""

import socket
import statistics
import sys
import time


def UDPPingerClient(address: str, port: int, request_num: int):
    """
    UDP Pinger Client

    :param address: The address of the server to ping.
    :param port: The port of the server to ping.
    :param request_num: The number of requests to send.
    :return: None
    """
    lost_packet = 0
    rtt_value_list: list[float] = []

    # Create socket instance.
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Set timeout to 1 second.
    client_socket.settimeout(1)
    client_socket.connect((address, port))
    # Warm up the socket.
    while True:
        try:
            client_socket.send(f"Ping {0} {time.time()}".encode())
            response = client_socket.recv(1024)
            print("Warm up response:", response.decode())
            break
        except Exception as e:
            continue

    for sequence_number in range(request_num):
        send_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        request = f"Ping {sequence_number + 1} {send_time}"
        try:
            current_time = time.perf_counter()
            client_socket.send(request.encode())
            # UDP does not need a while loop to receive data.
            response = client_socket.recv(1024)
            rtt_value = (time.perf_counter() - current_time) * 1000
            rtt_value_list.append(rtt_value)
            response = response.decode()
            print(f"Reply from {address}: {response}, RTT={rtt_value:.3f} ms")
        except socket.timeout:
            lost_packet += 1
            print(f"Request timed out: PING {sequence_number + 1}")
        except Exception as e:
            print(f"Error: {e}")
            return

    if len(rtt_value_list):
        print(f"\n--- {address} ping statistics ---")
        print(f"{request_num} packets transmitted, {request_num - lost_packet} received, {(lost_packet / request_num):.2%} packet lost")
        print(
            f"RTT min/avg/max/stddev = {min(rtt_value_list):.3f}/{sum(rtt_value_list)/len(rtt_value_list):.3f}/{max(rtt_value_list):.3f}/{statistics.pstdev(rtt_value_list):.3f} ms"
        )
    else:
        print("\n--- {address} ping statistics ---")
        print(f"{request_num} packets transmitted, 0 received, 100% packet loss")
    client_socket.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python UDPPingerClient.py <address> <port>")
        sys.exit(1)

    address = sys.argv[1]
    port = int(sys.argv[2])
    request_num = 10

    UDPPingerClient(address, port, request_num)
