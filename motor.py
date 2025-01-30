import bluetooth
import time
import serial

# Arduino Serial Port Configuration
arduino_port = "/dev/ttyACM0"  # Replace with the actual port for your Arduino
baud_rate = 9600  # Match the Arduino's baud rate
arduino = None

# Initialize Arduino Serial Connection
def init_arduino_connection():
    global arduino
    try:
        arduino = serial.Serial(arduino_port, baud_rate, timeout=2)
        time.sleep(2)  # Allow time for the Arduino to initialize
        print(f"Connected to Arduino on {arduino_port}")
    except Exception as e:
        print(f"Failed to connect to Arduino: {e}")
        arduino = None

# Create a Bluetooth socket
server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

# Bind the socket to a port
port = 1  # Commonly used port for Bluetooth communication
server_socket.bind(("", port))

# Listen for connections
server_socket.listen(1)
print("Waiting for Bluetooth connection...")

try:
    # Initialize Arduino connection
    init_arduino_connection()
    
    # Wait for a client to connect via Bluetooth
    client_socket, address = server_socket.accept()
    print(f"Connected to Bluetooth client: {address}")
    
    while True:
        try:
            # Receive data from the Bluetooth client
            data = client_socket.recv(1024).decode("utf-8").strip()  # Adjust buffer size as needed
            if data:
                print(f"Received number from Bluetooth client: {data}")
                
                # Validate and send the data to Arduino via serial
                if arduino:
                    if data in ["0", "1", "2", "3"]:
                        arduino.write(f"{data}\n".encode())  # Send the data followed by newline
                        print(f"Sent to Arduino: {data}")
                        
                        # Wait to receive confirmation ('1') from Arduino
                        while True:
                            arduino_response = arduino.readline().decode("utf-8").strip()

                            print(f"Raw Arduino Response: '{arduino_response}'")
                            if arduino_response == "1":
                                print("Received '1' from Arduino. Motor movement complete.")
                                break
                            time.sleep(0.1)  # Prevent busy waiting
                    else:
                        print(f"Invalid data received: {data}. Expected 0, 1, 2, or 3.")
                else:
                    print("Arduino is not connected.")

                # Send back confirmation via Bluetooth
                response = "OK"
                client_socket.send(response.encode())
                print(f"Sent back confirmation: {response}")
        except bluetooth.BluetoothError as e:
            print(f"Bluetooth error occurred: {e}")
            break  # Exit the loop if the connection is lost
except KeyboardInterrupt:
    print("Program terminated.")
finally:
    # Clean up sockets and serial connection
    if arduino:
        arduino.close()
    client_socket.close()
    server_socket.close()
