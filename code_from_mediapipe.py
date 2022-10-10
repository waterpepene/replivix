import cv2
import mediapipe as mp
from numpy.lib import math

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# For webcam input:
cap = cv2.VideoCapture(0)
with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_world_landmarks:
            for hand_landmarks in results.multi_hand_world_landmarks:
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                index_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                # get the euclidean distance between the two points
                distance = math.sqrt((index_finger_tip.x - index_finger_mcp.x) ** 2 + (index_finger_tip.y - index_finger_mcp.y) ** 2 + (index_finger_tip.z - index_finger_mcp.z) ** 2)
                # round the distance to 2 decimal places
                distance = round(distance, 2)
                # draw the distance on the screen
                cv2.putText(image, f"Distance: {distance}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                if distance >= 0.17:
                    mp_drawing.plot_landmarks(hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,)
                # print(angle)
        # Flip the image horizontally for a selfie-view display.
        cv2.imshow('MediaPipe Hands', image)
        if cv2.waitKey(5) & 0xFF == 27:
            break
cap.release()
