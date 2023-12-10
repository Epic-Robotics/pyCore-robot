import json
import socket
import subprocess

class UDPConnection:
    """
    A class for sending and receiving JSON messages over UDP.
    """
    def __init__(self, ip_address, port, buffer_size=2048):
        """
        Initialize the UDP connection.

        Args:
            ip_address (str): The IP address of the remote host.
            port (int): The port number to use for communication.
            buffer_size (int, optional): The buffer size for receiving messages. Defaults to 1024.
        """
        self.ip_address = ip_address
        self.port = port
        self.buffer_size = buffer_size
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            ip_address = subprocess.check_output(['hostname', '-I']).decode('utf-8').split(' ')[0]  # Get the WLAN IP address using the 'hostname -I' command
        except subprocess.CalledProcessError:
            print('Failed to retrieve WLAN IP address. Using default IP address.')
            raise Exception("Failed Connetion")

        print(f'MASTER IP address: {ip_address}')
        self.sock.bind((ip_address, self.port))  # Bind the socket to the retrieved WLAN IP and port
 
    def sendMessage(self, message):
        """
        Send a JSON message to the remote host in byte format.

        Args:
            message (dict): The message to send.
        """
        json_message = json.dumps(message)
        self.sock.sendto(json_message.encode('utf-8'), (self.ip_address, self.port))

    def receiveMessage(self):
        """
        Receive a JSON message from the remote host.

        Returns:
            (dict, tuple): The message and the sender's address.
        """
        try:
            data, addr = self.sock.recvfrom(self.buffer_size)
            # Check if data is empty before decoding
            if not data:
                return None, addr
            # Decode data
            json_data = json.loads(data.decode())
        except TypeError as e:
            print(f"Error receiving message: {e}")
            return None, addr
        except json.decoder.JSONDecodeError as e:
            print(f"Error decoding JSON message: {e}")
            return None, addr
        # Return the message and the sender's address
        return json_data, addr

    def __del__(self):
        """
        Destructor. Closes the socket.
        """
        self.sock.close()