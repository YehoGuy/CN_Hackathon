import threading
import struct
import time
import socket
from Helpers import get_local_ip
from EncoderDecoder import create_offer_packet
from Helpers import get_udp_socket
from Helpers import get_tcp_socket
from EncoderDecoder import decode_request_packet
from EncoderDecoder import create_payload_packet
from EncoderDecoder import PAYLOAD_SIZE

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
    
    
    
def listen_for_udp_requests(udp_socket):
    '''
        Handle incoming UDP messages on the given socket.
    '''
    print(f"{bcolors.OKGREEN} Listening for UDP messages... {bcolors.ENDC}")
    while True:
        try:
            # !!! recvfrom is blocking so No Busy Waiting !!!
            message, address = udp_socket.recvfrom(1024)  #recvfrom brings one packet at a time
            threading.Thread(target=handle_udp_client, args=(message, address), daemon=True).start()
        except Exception as e:
            print(f"[ERROR] Error receiving UDP message: {e}")

def handle_udp_client(message, address):
    file_size = decode_request_packet(message)
    if file_size is not None:
        print(f"[UDP client {address}] Received UDP message: {file_size} bytes")
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        with udp_socket:
            number_of_segments = file_size//PAYLOAD_SIZE if file_size % PAYLOAD_SIZE == 0 else file_size//PAYLOAD_SIZE+1
            # send size message
            for i in range(number_of_segments):
                payload_packet = create_payload_packet(number_of_segments, i+1)
                udp_socket.sendto(payload_packet, address)
        print(f"[UDP client {address}] sent {file_size} bytes in {number_of_segments} segments")



def listen_for_tcp_requests(tcp_socket):
    '''
        Handle incoming TCP connections on the given socket.
    '''
    print(f"{bcolors.OKGREEN} Listening for TCP connections...{bcolors.ENDC}")
    tcp_socket.listen()
    while True:
        try:
            # !! BLOCKING no busy-waiting !!
            conn, addr = tcp_socket.accept()
            threading.Thread(target=handle_tcp_client, args=(conn, addr), daemon=True).start()
        except Exception as e:
            print(f"Error handling TCP connection: {e}")


def handle_tcp_client(conn, addr):
    '''
        Handle incoming TCP connections on the given socket.
    '''
    try:
        print(f"[TCP CLIENT {addr}] Accepted TCP connection")
        with conn:
            data = b""
            while True:
                byte = conn.recv(1)
                if not byte:  # Client disconnected
                    raise Exception("illegal byte from client")
                if byte == b'\n':  # Stop when newline is found
                    break
                data += byte
            file_size = (int)(data.decode('utf-8'))
            demi_file = ('A'*file_size).encode('utf-8')
            conn.sendall(demi_file)
            print(f"[TCP CLIENT {addr}] Sent {file_size} bytes to client")
    except Exception as e:
        print(f"[FROM TCP CLIENT {addr}] Error handling TCP connection: {e}")



# Main function to start the server
def main():
    try:
        print(f" {bcolors.UNDERLINE}{bcolors.HEADER} Server started. Listening on IP address {get_local_ip()}. {bcolors.ENDC}")
        udp_socket = get_udp_socket()
        tcp_socket = get_tcp_socket()
        print(f"Selected UDP Port: {udp_socket.getsockname()[1]}")
        print(f"Selected TCP Port: {tcp_socket.getsockname()[1]}")
        # Create and start a thread for broadcasting. daemon = True to stop the thread when the main thread stops
        broadcast_thread = threading.Thread(target=broadcast_offer, args=(udp_socket.getsockname()[1], tcp_socket.getsockname()[1]), daemon=True)
        broadcast_thread.start()
        udp_handling_thread = threading.Thread(target=listen_for_udp_requests, args=(udp_socket,), daemon=True)
        udp_handling_thread.start()
        tcp_handling_thread = threading.Thread(target=listen_for_tcp_requests, args=(tcp_socket,), daemon=True)
        tcp_handling_thread.start()
        # Keep the server running
        while True:
            time.sleep(1)  

    except Exception as e:
        print(f"\n{bcolors.RED} [ERROR] Server shutting down. {bcolors.ENDC}")
        print(f"\n{bcolors.RED} [CAUSE] {bcolors.ENDC} {e}")
    except KeyboardInterrupt as e:
        print(f"\n{bcolors.RED} [QUIT] Server got KeyboardInterrupted. {bcolors.ENDC}")

    
    

# Run the server
if __name__ == "__main__":
    main()
