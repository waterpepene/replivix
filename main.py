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
    fist_closed_data = {finger.name: [0] for finger in comms.hand_object}
    start_time = time.time()

    @run_for(1)
    def data_gathering():
        for finger in comms.hand_object:
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


@run_for(2)
def text_on_screen(text):
    if comms.draw_queue.empty():
        comms.draw_queue.put({draw_text_on_image: [f"{text}"]})
        time.sleep(1 / 60)


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
    BaseHand.difference = {finger: round(hand_open_data[finger] - fist_closed_data[finger], 5)
                           for finger in hand_open_data}

    BaseHand.increment = {finger: BaseHand.difference[finger] / 4
                          for finger in BaseHand.difference}

    while True:
        if comms.communication_queue.empty(): continue
        data_received = comms.communication_queue.get()
        BaseHand.data_received = data_received.landmark
        all_fingers_repr = []

        for finger in comms.hand_object:
            bent_level = finger.calculate_bent()
            all_fingers_repr.append(f"{finger.__repr__()} - {bent_level}% Bent")

        all_fingers = "\n".join([str(finger) for finger in all_fingers_repr])

        # if comms.draw_queue.empty():
        comms.draw_queue.put({draw_text_on_image: [all_fingers]})
