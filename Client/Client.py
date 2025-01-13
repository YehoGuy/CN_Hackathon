import socket
import struct
import threading
import time
from Helpers import create_request_packet
from Helpers import is_payload_packet

_OFFER_PORT = 13117

def listen_for_offer(offer_port):
    """
    This function listens for UDP broadcast offer packets on the specified port (13117).
    When it receives an offer packet, it decodes returns it.
    Returns:
        a tuple of size 2: (address, packet)
        where addresses' structure is (ip, port) 
        and packet's structure is (magic_cookie, message_type, udp_port, tcp_port)
    """
    try:
        # Create a UDP socket
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # Allow address reuse
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind to the specified port and all network interfaces
        udp_socket.bind(("", offer_port))
        print(f"Listening for offer packets on port {offer_port}...")
        while True:
            # !!! recvfrom is blocking so No Busy Waiting !!!
            # Receive data from the UDP socket into a buffer of 1024 bytes
            # address format is (ip, port)
            data, address = udp_socket.recvfrom(1024)  
            try:
                # '!I B H H' means: ! - network byte order, I - unsigned int (4 bytes), 
                #                   B - unsigned char (1 byte), H - unsigned short (2 bytes)
                offer = struct.unpack('!I B H H', data)
                magic_cookie = offer[0] 
                message_type = offer[1]
                # Validate the magic cookie and message type
                if not(magic_cookie == 0xabcddcba and message_type == 0x2):
                    print(f"[ERROR] Invalid packet received from {address[0]}.")
                else:
                    return (address, offer)
            except struct.error as e:
                print(f"[ERROR] Error decoding packet from {address[0]}: {e}")
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
    finally: # finally always runs before return. for cleanup.
        udp_socket.close()



def start_tcp_connection(server_ip, tcp_port, file_size, id):
    """
    Start a TCP connection to download the specified file size.
    """
    try:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect((server_ip, tcp_port))

        size_message = f"{file_size}\n".encode() # bytes
        tcp_socket.send(size_message)
        bytes_received = 0

        # to measure time, we use time.perf_counter() 
        # which is designed for high resolution time measurements
        start_time = time.perf_counter()

        while bytes_received < file_size:
            data = tcp_socket.recv(4096)  # Receive 4KB chunks
            if not data:
                break
            bytes_received += len(data)

        end_time = time.perf_counter()

        total_time = end_time - start_time
        total_speed_bps = file_size*8 / total_time

        print(f"TCP transfer #{id} finished, total time: {total_time:.2f} seconds, total speed: {total_speed_bps:.2f} bits/second")

    except Exception as e:
        print(f"Error in TCP connection: {e}")
    finally:
        tcp_socket.close()


def start_udp_communication(server_ip, udp_port, file_size, id):
    """
    Start a UDP connection to download the specified file size.
    """
    try:
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # send size message
        request_packet = create_request_packet(file_size)
        udp_socket.sendto(request_packet, (server_ip, udp_port))
        bytes_received = 0

        # "The Client detects that the UDP transfer 
        # concludes after no data has been received for 1 second."
        udp_socket.settimeout(1)  
        # to measure time, we use time.perf_counter() 
        # which is designed for high resolution time measurements
        start_time = time.perf_counter()

        while bytes_received < file_size:
            try:
                data, address = udp_socket.recvfrom(1024)  # Receive one udp packet up to 1kB
                if(is_payload_packet(data)):
                    bytes_received += 512
            except socket.timeout:
                end_time = time.perf_counter()
                total_time = end_time - start_time
                total_speed_bps = file_size*8 / total_time
                succ_rate = 100 if bytes_received > file_size else bytes_received*100 / file_size
                print(f"UDP transfer #{id} finished, total time: {total_time:.2f} seconds, total speed: {total_speed_bps:.2f} bits/second, percentage of packets received successfully: {succ_rate:.2f}%")
                break
        
        end_time = time.perf_counter()

        total_time = end_time - start_time
        total_speed_bps = file_size*8 / total_time
        succ_rate = 100 if bytes_received > file_size else bytes_received*100 / file_size

        print(f"UDP transfer #{id} finished, total time: {total_time:.2f} seconds, total speed: {total_speed_bps:.2f} bits/second, percentage of packets received successfully: {succ_rate:.2f}%")

    except Exception as e:
        print(f"Error in UDP connection: {e}")
    finally:
        udp_socket.close()



def start(file_size, tcp_connections, udp_connections):
    address, offer = listen_for_offer(_OFFER_PORT)
    magic_cookie, message_type, udp_port, tcp_port = offer
    print(f"Received offer packet from {address[0]}:")
    print(f"  UDP Port: {udp_port}")
    print(f"  TCP Port: {tcp_port}")
    # Start TCP connections
    for i in range(tcp_connections):
        threading.Thread(target=start_tcp_connection, args=(address[0], tcp_port, file_size, i), daemon=True).start()
    # Start UDP connections
    for i in range(udp_connections):
        threading.Thread(target=start_udp_communication, args=(address[0], udp_port, file_size, i), daemon=True).start()


if __name__ == "__main__":
    while(True):
        # Prompt user for inputs
        # (in python 3, int can hold very large numbers)
        file_size = int(input("Enter file size in Bytes: "))
        tcp_connections = int(input("Enter the number of TCP connections: "))
        udp_connections = int(input("Enter the number of UDP connections: "))
        start(file_size, tcp_connections, udp_connections)
        print("Complete, ", end="")



