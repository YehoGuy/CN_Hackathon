import struct
import socket



def get_local_ip():
    '''
        This Method is used to Get the local IP address of the server.
        Returns:
            local_ip (str): The local IP address of the server.
        Notes:
            I Tried to use socket.gethostbyname(socket.gethostname())
            but it returns loaclhost (127.0.0.1).
            So we use socket.connect(), which creates a udp 'connection' 
            (just removes the effort of writing to and from)
            which allows us to get the local IP address.

    '''
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        # Connect to an external server (Google's public DNS)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    return local_ip


def get_udp_socket():
    '''
        This Method is used to create and bind a UDP socket.
        Returns:
            udp_socket (socket.socket): The created and bound UDP socket.
        Raises:
            OSError: If the socket creation or binding fails.
    '''
    try:
        # Create a UDP socket
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # Allow the socket to broadcast
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # Bind to an available port on all interfaces
        udp_socket.bind(('', 0))
        return udp_socket
    except OSError as e:
        print(f"Error creating or binding UDP socket: {e}")
        if 'udp_socket' in locals():  # Ensure the socket is closed if partially created
            udp_socket.close()
        raise

def get_tcp_socket():
    """
    Create and bind a TCP socket.

    This method creates a TCP socket using IPv4 and binds it to an available port
    chosen by the operating system.

    Returns:
        socket.socket: The created and bound TCP socket.

    Raises:
        OSError: If the socket creation or binding fails.
    
    Example:
        >>> tcp_socket = get_tcp_socket()
        >>> print(tcp_socket.getsockname())
    """
    try:
        # Create a TCP socket
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind to an available port
        tcp_socket.bind(('', 0))
        return tcp_socket
    except OSError as e:
        print(f"Error creating or binding TCP socket: {e}")
        # Ensure the socket is closed if partially created
        if 'tcp_socket' in locals():  
            tcp_socket.close()
        raise