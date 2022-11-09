import time

import cv2
from capture_hands import *
from functions import *

process = capture_movement_process(comms)


def draw_text_on_image(image, text: str):
    # if the text contains a newline, split it into multiple lines
    lines = text.splitlines()
    for i, line in enumerate(lines):
        image = cv2.putText(image, line, (150, 20 + i * 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
    return image


def gather_average_y_distance():
    fist_closed_data = {finger.name: [0] for finger in Communication.hand_object}
    start_time = time.time()

    @run_for(3)
    def data_gathering():
        for finger in Communication.hand_object:
            data_received = comms.communication_queue.get()
            finger_tip = data_received.landmark[finger.TIP].y
            wrist = data_received.landmark[0].y
            distance_finger = round(wrist - finger_tip, 2)
            fist_closed_data[finger.name].append(distance_finger)

        time_on_screen = str(round(time.time() - start_time, 2))
        comms.draw_queue.put({draw_text_on_image: ["Gathering hand data...\n" + time_on_screen]})

    data_gathering()
    # get the average of the data
    fist_closed_data = {finger: round(sum(data) / len(data), 5) for finger, data in fist_closed_data.items()}
    return fist_closed_data


@run_for(4)
def text_on_screen(text):
    if comms.draw_queue.empty():
        comms.draw_queue.put({draw_text_on_image: [f"{text}"]})
        time.sleep(1/60)


if __name__ == '__main__':
    process.start()
    # start a loop that will run for 3 seconds
    print("Gathering closed fist data...")
    text_on_screen("Close your fist!")
    fist_closed_data = gather_average_y_distance()
    print("Gathering open fist data...")
    text_on_screen("Now hand wide open!")
    hand_open_data = gather_average_y_distance()
    # get the difference between the two
    difference = {finger: round(hand_open_data[finger] - fist_closed_data[finger], 5) for finger in hand_open_data}
    increment = {finger: difference[finger] / 4 for finger in difference}
    # print the difference
    print(difference)
    print(increment)

    while True:
        if comms.communication_queue.empty(): continue

        data_received = comms.communication_queue.get()
        all_fingers_repr = []
        # get the tip of the index finger
        for finger in Communication.hand_object:
            finger_tip = data_received.landmark[finger.TIP].y
            finger_bottom = data_received.landmark[0].y
            distance_fingers = round(finger_bottom - finger_tip, finger.statuses) - difference[finger.name]
            status = distance_fingers // increment[finger.name]
            # limit the status to 0-5, do not use if statement because it will not work with negative numbers
            status = max(0, min(finger.statuses, status))
            # turn distance_fingers into a percentage from 0-100 using fist_closed_data and hand_open_data
            distance_fingers = (distance_fingers / difference[finger.name]) * 100
            # limit the distance_fingers to 0-100
            distance_fingers = max(0, min(100, distance_fingers))
            # get the inverse of the distance_fingers, so if the distance is 60, the inverse is 40
            inverse_distance_fingers = round(100 - distance_fingers)

            finger.set_status(status)

            all_fingers_repr.append(f"{finger.__repr__()} - {inverse_distance_fingers}% Bent")

        all_fingers = "\n".join([str(finger) for finger in all_fingers_repr])
        # print(all_fingers)
        # if comms.draw_queue.empty():
        comms.draw_queue.put({draw_text_on_image: [all_fingers]})
