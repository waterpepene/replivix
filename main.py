import cv2
from capture_hands import *
from functions import *


process = capture_movement_process(comms)


def draw_text_on_image(image, text: str):
    # if the text contains a newline, split it into multiple lines
    lines = text.splitlines()
    for i, line in enumerate(lines):
        image = cv2.putText(image, line, (25, 20 + i * 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
    return image


def draw_line_on_image(image):
    return cv2.line(image, (100, 100), (100, 100), (0, 255, 0), 5)


if __name__ == '__main__':
    process.start()

    while True:
        if not comms.communication_queue.empty():
            data_received = comms.communication_queue.get()
            all_fingers_repr = []
            # get the tip of the index finger
            for finger in Communication.hand_object:
                index_finger_lowermost = data_received.landmark[finger.MCP]
                index_finger_tip = data_received.landmark[finger.TIP]
                ADJ = index_finger_tip.y - index_finger_lowermost.y
                OPP = index_finger_tip.x - index_finger_lowermost.x
                HYP = math.sqrt(ADJ ** 2 + OPP ** 2)
                # get the angle between the ADJ and HYP
                angle = math.degrees(math.acos(ADJ / HYP))
                finger.set_angle(angle)

                all_fingers_repr.append(finger.__repr__())
                # print(finger)

            all_fingers = "\n".join([str(finger) for finger in all_fingers_repr])
            comms.draw_queue.put({draw_text_on_image: [all_fingers]})
