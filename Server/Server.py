import threading
import struct
import time
from scapy.all import * # type: ignore
import socket
from Helpers import get_local_ip
from Helpers import create_offer_packet
from Helpers import get_udp_socket
from Helpers import get_tcp_socket

class bcolors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RED = '\033[91m'




def broadcast_offer(udp_port, tcp_port):
    '''
        This Method is used to broadcast the offer packet every second.
    '''
    try:
        # create an IPv4, Datagram, UDP socket (AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # allow socket to broadcast
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        offer_packet = create_offer_packet(udp_port, tcp_port)
        # Broadcast the packet every second
        while True:
            broadcast_socket.sendto(offer_packet, ('255.255.255.255', 13117))
            time.sleep(1)  # Wait for 1 second before broadcasting again
    except Exception as e:
        raise Exception(f"an error occurred while trying to broadcast the offer packet: {e}")
    
###TODO CONTINUE
def handle_udp_messages(udp_socket):
    '''
        Handle incoming UDP messages on the given socket.
    '''
    print(f"{bcolors.OKGREEN} Listening for UDP messages... {bcolors.ENDC}")
    while True:
        try:
            message, address = udp_socket.recvfrom(1024)  # Buffer size is 1024 bytes
            print(f"[FROM UDP CLIENT] Received UDP message from {address}: {message.decode('utf-8')}")
        except Exception as e:
            print(f"[ERROR] Error receiving UDP message: {e}")

###TODO CONTINUE
def handle_tcp_connections(tcp_socket):
    '''
        Handle incoming TCP connections on the given socket.
    '''
    print(f"{bcolors.OKGREEN} Listening for TCP connections...{bcolors.ENDC}")
    tcp_socket.listen()
    while True:
        try:
            conn, addr = tcp_socket.accept()
            print(f"[FROM TCP CLIENT]Accepted TCP connection from {addr}")
            with conn:
                while True:
                    data = conn.recv(1024)  # Buffer size is 1024 bytes
                    if not data:
                        break
                    print(f"Received TCP message from {addr}: {data.decode('utf-8')}")
                    conn.sendall(data)  # Echo the received message
        except Exception as e:
            print(f"Error handling TCP connection: {e}")




# Main function to start the server
def main():
    try:
        print(f" {bcolors.UNDERLINE}{bcolors.HEADER} Server started. Listening on IP address {get_local_ip()}. {bcolors.ENDC}")
        udp_socket = get_udp_socket()
        tcp_socket = get_tcp_socket()
        print(f"Selected UDP Port: {udp_socket.getsockname()[1]}")
        print(f"Selected TDP Port: {tcp_socket.getsockname()[1]}")
        # Create and start a thread for broadcasting
        broadcast_thread = threading.Thread(target=broadcast_offer, args=(udp_socket.getsockname()[1], tcp_socket.getsockname()[1]), daemon=True)
        broadcast_thread.start()
        # Keep the server running
        while True:

            time.sleep(1)  

    except Exception as e:
        print(f"\n{bcolors.RED} [ERROR] Server shutting down. {bcolors.ENDC}")
        print(f"\n{bcolors.RED} [CAUSE] {bcolors.ENDC} {e}")
    except KeyboardInterrupt as e:
        print(f"\n{bcolors.RED} [ERROR] Server got KeyboardInterrupted. {bcolors.ENDC}")
        print(f"\n{bcolors.RED} [CAUSE] {bcolors.ENDC} {e}")

    
    

# Run the server
if __name__ == "__main__":
    main()
