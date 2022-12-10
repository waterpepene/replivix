import multiprocessing
import threading
import time
from collections import defaultdict
from typing import List
from numpy.lib import math
from dataclasses import dataclass


def get_euclidean_distance(point1, point2):
    return math.sqrt((point2.x - point1.x) ** 2 + (point2.y - point1.y) ** 2 + (point2.z - point1.z) ** 2)


@dataclass
class BaseHand:
    difference = increment = data_received = {}


# create an ENUM for all 5 fingers
class Hand:
    def __init__(self):
        self.__current_finger = 0
        self.THUMB = Finger(statuses_range=3, landmarks=[1, 2, 3, 4], name="Thumb")
        self.INDEX = Finger(statuses_range=4, landmarks=[5, 6, 7, 8], name="Index")
        self.MIDDLE = Finger(statuses_range=4, landmarks=[9, 10, 11, 12], name="Middle")
        self.RING = Finger(statuses_range=4, landmarks=[13, 14, 15, 16], name="Ring")
        self.PINKY = Finger(statuses_range=4, landmarks=[17, 18, 19, 20], name="Pinky")

    def __repr__(self):
        return f"{self.THUMB} \n {self.INDEX} \n {self.MIDDLE} \n {self.RING} \n {self.PINKY}"

    def __iter__(self):
        return self

    def __next__(self):
        if self.__current_finger == 5:
            self.__current_finger = 0
            raise StopIteration
        else:
            iterables = (self.THUMB, self.INDEX, self.MIDDLE, self.RING, self.PINKY)
            self.__current_finger += 1
            return iterables[self.__current_finger - 1]


class Finger:
    def __init__(self, statuses_range: int, landmarks: List[int], name: str = "Finger"):
        self.statuses = statuses_range
        self.current_status = 0
        self.MCP = landmarks[0]
        self.PIP = landmarks[1]
        self.DIP = landmarks[2]
        self.TIP = landmarks[3]
        self.name = name
        self.calculators = defaultdict(lambda: self.calculate_generic)
        # self.calculators = defaultdict(self.calculate_generic)
        self.calculators["Thumb"] = self.calculate_thumb

    def calculate_thumb(self) -> int:
        return 0

    def calculate_generic(self) -> int:
        finger_tip = BaseHand.data_received[self.TIP].y
        finger_bottom = BaseHand.data_received[0].y
        distance_fingers = round(finger_bottom - finger_tip, self.statuses) - BaseHand.difference[self.name]
        status = distance_fingers // BaseHand.increment[self.name]
        # limit the status to 0-5, do not use if statement because it will not work with negative numbers
        status = max(0, min(self.statuses, status))
        # turn distance_fingers into a percentage from 0-100 using fist_closed_data and hand_open_data
        distance_fingers = (distance_fingers / BaseHand.difference[self.name]) * 100
        # limit the distance_fingers to 0-100
        distance_fingers = max(0, min(100, distance_fingers))
        # get the inverse of the distance_fingers, so if the distance is 60, the inverse is 40
        inverse_distance_fingers = round(100 - distance_fingers)

        self.set_status(status)
        return inverse_distance_fingers

    # if the finger name is thumb, the method calculate_bent must call calculate_thumb instead
    def calculate_bent(self):
        return self.calculators[self.name]()

    def set_status(self, status: int):
        if status == self.current_status: return
        self.current_status = status

    def get_status(self):
        return self.current_status

    def __repr__(self):
        # print the name, status, angle, and all statuses of the finger
        return f"{self.name} - Status: {self.get_status()} - Statuses: {self.statuses}"


@dataclass
class Communication:
    communication_queue = multiprocessing.Queue()
    draw_queue = multiprocessing.Queue()
    hand_object = Hand()


# by default, exit all processes after 60 seconds
# this is to prevent the program from running forever
def kill_processes():
    # exit all processes under the main process
    children = multiprocessing.active_children()
    for child in children:
        child.terminate()
        child.join()
    exit("Processes killed")


# create a function decorator that will run the function for {x} seconds in a while loop
def run_for(seconds: int):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            while time.time() - start_time < seconds:
                func(*args, **kwargs)

        return wrapper

    return decorator


threading.Timer(60, kill_processes).start()
comms = Communication()
