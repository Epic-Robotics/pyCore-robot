import json
import pycore_robot

# Create a UDP connection object
udp_connection = pycore_robot.wifiConection.UDPConnection('192.168.1.102', 44444)

while True:
    # Receive a message
    received_message, address = udp_connection.receiveMessage()
    if received_message:
        print(f"Received message from {address}: {json.dumps(received_message)}")
        # Send a message
        message = {'name': 'Alice', 'age': 25}
        udp_connection.sendMessage(message)