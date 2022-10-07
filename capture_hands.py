import cv2
import mediapipe as mp
import multiprocessing
import atexit
# from functions import Communication

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
cap = cv2.VideoCapture(0)
communication_queue = multiprocessing.Queue()
draw_queue = multiprocessing.Queue()


def store_data_to_class(comm_queue, draw_on_image_queue):
    print("Starting process, data_queue:", communication_queue)
    atexit.register(cap.release)
    with mp_hands.Hands(
            model_complexity=1,
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6) as hands:
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

            if results.multi_hand_landmarks:
                # print("Sending data to queue")
                comm_queue.put(results.multi_hand_landmarks[0])
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            if not draw_on_image_queue.empty():
                draw_on_image = draw_on_image_queue.get()
                draw_on_image(image)

            cv2.imshow('MediaPipe Hands', image)

            if cv2.waitKey(5) & 0xFF == 27:
                break

    cap.release()


def capture_movement_process(comm_queue, draw_on_image_queue):
    return multiprocessing.Process(target=store_data_to_class, args=(comm_queue, draw_on_image_queue), daemon=True)