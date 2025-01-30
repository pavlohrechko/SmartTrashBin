import base64
import cv2
import numpy as np
from edge_impulse_linux.image import ImageImpulseRunner
from gpiozero import Button, LED, Servo
from time import sleep
import bluetooth  # For Bluetooth communication

# GPIO Pins
BUTTON_PIN = 24
LED_PIN = 23
SERVO_LEFT_PIN = 17
SERVO_RIGHT_PIN = 27

# Servo configuration
myCorrection = 0.45
maxPW = (2.0 + myCorrection) / 1000
minPW = (1.0 - myCorrection) / 1000

# Initialize hardware
button = Button(BUTTON_PIN, pull_up=True)
led = LED(LED_PIN)
servo_left = Servo(17, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
servo_right = Servo(27, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
servo_left.detach()
servo_right.detach()

# State tracking
waiting_for_trash = True
waiting_for_confirmation = False

# Model file path
model_path = "./model.eim"
runner = ImageImpulseRunner(model_path)

# Class mappings
class_mapping = {
    "cardboard": 0,
    "metal": 1,
    "organic": 2,
    "paper": 0,
    "plastic": 3,
}

# Bluetooth settings
server_mac_address = "2C:CF:67:60:D2:BF"  # Replace with the server Pi's Bluetooth MAC address
port = 1


# Initialize Bluetooth socket
sock = None
def init_bluetooth_connection():
    global sock
    try:
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        print(f"Connecting to {server_mac_address} on port {port}...")
        sock.connect((server_mac_address, port))
        print("Bluetooth connection established.")
    except Exception as e:
        print(f"Failed to establish Bluetooth connection: {e}")
        sock = None

# Send data via Bluetooth and wait for a response
def send_bluetooth_data_and_wait(data):
    try:
        if sock:
            sock.send(data)
            print(f"Sent via Bluetooth: {data}")
            print("Waiting for response...")
            response = sock.recv(1024).decode("utf-8")  # Receive response from the server
            print(f"Response received: {response}")
            return response.strip() == "OK"
        else:
            print("Bluetooth socket is not connected.")
            return False
    except Exception as e:
        print(f"Error in Bluetooth communication: {e}")
        return False

# Resize function for classification
def resize2SquareKeepingAspectRatio(img, size, interpolation):
    h, w = img.shape[:2]
    c = None if len(img.shape) < 3 else img.shape[2]
    if h == w: return cv2.resize(img, (size, size), interpolation)
    dif = max(h, w)
    x_pos, y_pos = (dif - w) // 2, (dif - h) // 2
    if c is None:
        mask = np.zeros((dif, dif), dtype=img.dtype)
        mask[y_pos:y_pos+h, x_pos:x_pos+w] = img[:h, :w]
    else:
        mask = np.zeros((dif, dif, c), dtype=img.dtype)
        mask[y_pos:y_pos+h, x_pos:x_pos+w, :] = img[:h, :w, :]
    return cv2.resize(mask, (size, size), interpolation)

# Function to spin the servo
def spin_servo():
    servo_right.value = 1
    servo_left.value = 1
    sleep(2)
    servo_right.value = 0
    servo_left.value = 0
    sleep(1)
    servo_left.detach()
    servo_right.detach()
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not cap.isOpened():
        print("Error: Could not open the camera.")
        return None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    ret, frame = cap.read()
    cap.release()
    if ret:
        img_path = "captured_image.jpg"
        cv2.imwrite(img_path, frame)
        print(f"Image saved as {img_path}")
        return img_path
    else:
        print("Error: Could not capture an image.")
        return None


# Function to take a picture
def take_picture():
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not cap.isOpened():
        print("Error: Could not open the camera.")
        return None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    ret, frame = cap.read()
    cap.release()
    if ret:
        img_path = "captured_image.jpg"
        cv2.imwrite(img_path, frame)
        print(f"Image saved as {img_path}")
        return img_path
    else:
        print("Error: Could not capture an image.")
        return None

# Function to classify an image
def classify_image(image_path):
    try:
        model_info = runner.init()
        print("Model loaded: ", model_info)

        img = cv2.imread(image_path)
        if img is None:
            raise Exception("Failed to load image at " + image_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        resized = resize2SquareKeepingAspectRatio(img_rgb, 160, cv2.INTER_AREA)

        features, _ = runner.get_features_from_image(resized)
        res = runner.classify(features)
        print("Classification results:")
        for bb in res['result']['classification']:
            print(f"{bb}: {res['result']['classification'][bb]:.3f}")

        top_class = max(res['result']['classification'], key=res['result']['classification'].get)
        print(f"Top class: {top_class}")
        return top_class
    finally:
        if runner:
            runner.stop()

# Main loop
try:
    init_bluetooth_connection()
    while True:
        if waiting_for_trash:
            led.on()
            print("Waiting for trash to be placed.")
            if button.is_pressed:
                print("Trash detected. Turning off LED.")
                led.off()  # Turn off the LED immediately after the button is pressed
                print("Taking a picture.")
                image_path = take_picture()
                if image_path:
                    print("Classifying the image...")
                    detected_class = classify_image(image_path)
                    if detected_class in class_mapping:
                        data_to_send = str(class_mapping[detected_class])
                        proceed = send_bluetooth_data_and_wait(data_to_send)                

                        if proceed:
                            print("Response received. You can spin the servo.")
                            spin_servo()  # Spin the servo after a valid response
                        else:
                            print("No valid response received. Aborting servo spin.")
                waiting_for_trash = True  # Return to waiting state
                sleep(0.5)

        sleep(0.1)

except KeyboardInterrupt:
    print("Program terminated.")
finally:
    if sock:
        sock.close()
