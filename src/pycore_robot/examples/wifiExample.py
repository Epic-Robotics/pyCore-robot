import json
import wifiConection

# Create a UDP connection object
udp_connection = wifiConection.UDPConnection('192.168.31.49', 44444)

while True:
    # Receive a message
    received_message, address = udp_connection.receive_message()
    if received_message:
        print(f"Received message from {address}: {json.dumps(received_message)}")
        # Send a message
        message = {'name': 'Alice', 'age': 25}
        udp_connection.send_message(message)