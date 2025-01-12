import socket
import struct

def listen_for_offer():
    """
    This function listens for UDP broadcast offer packets on a specific port.
    When it receives an offer packet, it decodes and prints the contents.
    """
    OFFER_PORT = 13117  # Port to listen for offer packets

    try:
        # Create a UDP socket
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # Allow address reuse
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind to the specified port and all network interfaces
        udp_socket.bind(("", OFFER_PORT))

        print(f"Listening for offer packets on port {OFFER_PORT}...")

        while True:
            # Receive data from the UDP socket
            data, addr = udp_socket.recvfrom(1024)  # Buffer size is 1024 bytes

            # Decode the offer packet using struct.unpack
            try:
                magic_cookie, message_type, udp_port, tcp_port = struct.unpack('!I B H H', data)

                # Validate the magic cookie and message type
                if magic_cookie == 0xabcddcba and message_type == 0x2:
                    print(f"Received offer packet from {addr[0]}:")
                    print(f"  UDP Port: {udp_port}")
                    print(f"  TCP Port: {tcp_port}")
                else:
                    print(f"Invalid packet received from {addr[0]}.")

            except struct.error as e:
                print(f"Error decoding packet from {addr[0]}: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        udp_socket.close()

# Run the client if this script is executed directly
if __name__ == "__main__":
    listen_for_offer()

