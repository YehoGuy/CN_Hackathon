import struct


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

def is_payload_packet(data):
    '''
        This Method is used to check if the received packet is a valid payload packet.
        Args:
            data (bytes): The received packet.
        Returns:
            bool: True if the packet is a payload packet, False otherwise.
    '''
    try:
        # '!I B Q Q 512s' means: ! - network byte order, I - unsigned int (4 bytes), 
        #                   B - unsigned char (1 byte), Q - unsigned long long (8 bytes)
        #                   512s - 512 length String (512 bytes)
        type = struct.unpack('!I B Q Q 512s', data)[1]
        return type == 0x4
    except struct.error:
        return False