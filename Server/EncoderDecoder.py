import struct

PAYLOAD_SIZE = 512

def create_payload_packet(total_segments, segment_number):
    '''
        This Method is used to create the payload packet.
        Args:
            payload_size (int): The size of the payload to be sent in the payload packet.
        Returns:
            payload_packet (bytes): The payload packet in binary format.
    '''
    # Packet fields
    magic_cookie = 0xabcddcba  # 4 bytes
    message_type = 0x4         # 1 byte
    # this method of demi payload creating is the 
    # most optimized and time efficient way in python
    payload = ('A' * PAYLOAD_SIZE).encode('utf-8')
    # Pack the data into binary format using struct
    # '!I B I' means: ! - network byte order, I - unsigned int (4 bytes), 
    #                   B - unsigned char (1 byte), <num>s - <num> length String (<num> bytes)
    #                   Q - unsigned long long (8 bytes)
    payload_packet = struct.pack(f'!I B Q Q {PAYLOAD_SIZE}s', magic_cookie, message_type, total_segments, segment_number, payload)
    return payload_packet

def create_offer_packet(udp_port, tcp_port):
    '''
        This Method is used to create the offer packet.
        Args:
            udp_port (int): The UDP port to be sent in the offer packet.
            tcp_port (int): The TCP port to be sent in the offer packet.
        Returns:
            offer_packet (bytes): The offer packet in binary format.
    '''
    # Packet fields
    magic_cookie = 0xabcddcba  # 4 bytes
    message_type = 0x2         # 1 byte
    
    # Pack the data into binary format using struct
    # '!I B H H' means: ! - network byte order, I - unsigned int (4 bytes), 
    #                   B - unsigned char (1 byte), H - unsigned short (2 bytes)
    offer_packet = struct.pack('!I B H H', magic_cookie, message_type, udp_port, tcp_port)
    return offer_packet


def create_request_packet(file_size):
    '''
        This Method is used to create a request packet.
        Args:
            file_size: requested file size in bytes
        Returns:
            request_packet (bytes): The request packet in binary format.
    '''
    # Packet fields
    magic_cookie = 0xabcddcba  # 4 bytes
    message_type = 0x3         # 1 byte
    
    # Pack the data into binary format using struct
    # '!I B H H' means: ! - network byte order, I - unsigned int (4 bytes), 
    #                   B - unsigned char (1 byte), Q - unsigned long long (8 bytes)
    offer_packet = struct.pack('!I B Q', magic_cookie, message_type, file_size)
    return offer_packet

def decode_request_packet(request_packet):
    '''
        This Method is used to decode the request packet.
        Args:
            request_packet (bytes): The request packet in binary format.
        Returns:
            file_size (int): The requested file size in bytes.
    '''
    try:
        # Unpack the data from binary format using struct
        # '!I B Q' means: ! - network byte order, I - unsigned int (4 bytes), 
        #                   B - unsigned char (1 byte), Q - unsigned long long (8 bytes)
        magic_cookie, message_type, file_size = struct.unpack('!I B Q', request_packet)
        if magic_cookie!=0xabcddcba or message_type != 0x3:
            return None
        return file_size
    except Exception as e:
        return None