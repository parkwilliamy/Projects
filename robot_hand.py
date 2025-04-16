import cv2
import mediapipe as mp
import numpy as np
import serial
import struct

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)

# Initialize Drawing Utils
mp_drawing = mp.solutions.drawing_utils

# Configure the serial port
ser = serial.Serial(
    port='COM6',                  # Use COM6
    baudrate=115200,              # Baud rate: 115200
    bytesize=serial.EIGHTBITS,    # 8 data bits
    parity=serial.PARITY_NONE,    # No parity bit
    stopbits=serial.STOPBITS_ONE, # 1 stop bit
    timeout=1                     # 1 second timeout for reads
)

# Open Webcam
cap = cv2.VideoCapture(0)

# Create a resizable window
cv2.namedWindow("Hand Tracking", cv2.WINDOW_NORMAL)

if ser.isOpen():
    print("Serial port COM6 opened successfully.")
else:
    ser.open()

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Flip the frame horizontally for a mirror effect
    frame = cv2.flip(frame, 1)

    # Convert frame to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process frame with Hand Tracking
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks: # Check if a hand is detected
        for hand_landmarks in results.multi_hand_landmarks: # Iterate through detected hands
            three = np.array([hand_landmarks.landmark[3].x, hand_landmarks.landmark[3].z])
            four = np.array([hand_landmarks.landmark[4].x, hand_landmarks.landmark[4].z])
            
            six = np.array([hand_landmarks.landmark[6].y, hand_landmarks.landmark[6].z])
            eight = np.array([hand_landmarks.landmark[8].y, hand_landmarks.landmark[8].z])
            
            ten = np.array([hand_landmarks.landmark[10].y, hand_landmarks.landmark[10].z])
            twelve = np.array([hand_landmarks.landmark[12].y, hand_landmarks.landmark[12].z])
            
            fourteen = np.array([hand_landmarks.landmark[14].y, hand_landmarks.landmark[14].z])
            sixteen = np.array([hand_landmarks.landmark[16].y, hand_landmarks.landmark[16].z])

            seventeen = np.array([hand_landmarks.landmark[17].y, hand_landmarks.landmark[17].z])
            twenty = np.array([hand_landmarks.landmark[20].y, hand_landmarks.landmark[20].z])
            
            # Create vectors for each finger
            thumb = four - three
            index = eight - six
            middle = twelve - ten
            ring = sixteen - fourteen
            pinky = twenty - seventeen

            # Calculate joint angles
            thumb_angle = abs(np.arctan2(thumb[1], thumb[0]) * 180 / np.pi)
            index_angle = np.arctan2(index[1], index[0]) * 180 / np.pi + 160
            middle_angle = np.arctan2(middle[1], middle[0]) * 180 / np.pi + 160
            ring_angle = np.arctan2(ring[1], ring[0]) * 180 / np.pi + 160
            pinky_angle = np.arctan2(pinky[1], pinky[0]) * 180 / np.pi + 160

            angles = [thumb_angle, index_angle, middle_angle, ring_angle, pinky_angle]
            pulse_widths = [100]  # Start marker

            for i in range(len(angles)):
                if angles[i] < 0:
                    angles[i] = 0
                if angles[i] > 180:
                    angles[i] = 180

            for angle in angles:
                pulse_widths.append(round(((angle / 18 + 2) / 100) * 4096))

            for i in range(1, len(pulse_widths)):
                if pulse_widths[i] > 511:
                    pulse_widths[i] = 511
                elif pulse_widths[i] < 103:
                    pulse_widths[i] = 103

            print(angles)

            packed_data = struct.pack('6i', *pulse_widths) # Pack the data as 6 integers
            ser.write(packed_data)

            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Show output in resizable window
    cv2.imshow("Hand Tracking", frame)

    # Close window on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
