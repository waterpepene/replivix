import cv2
from capture_hands import *
from functions import *


process = capture_movement_process(communication_queue, draw_queue)


def draw_lines_on_image(image):
    return cv2.line(image, (100, 100), (100, 100), (0, 255, 0), 5)


if __name__ == '__main__':
    process.start()

    while True:
        if not communication_queue.empty():
            data_received = communication_queue.get()
            # get the tip of the index finger
            wrist = data_received.landmark[Hand.INDEX.MCP]
            index_finger_tip = data_received.landmark[Hand.INDEX.TIP]
            ADJ = index_finger_tip.y - wrist.y
            OPP = index_finger_tip.x - wrist.x
            HYP = math.sqrt(ADJ ** 2 + OPP ** 2)
            # get the angle between the ADJ and HYP
            angle = math.degrees(math.acos(ADJ / HYP))
            print(angle)
            draw_queue.put(draw_lines_on_image)
