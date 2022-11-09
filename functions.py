import multiprocessing
import threading
import time
from typing import List
from numpy.lib import math
from dataclasses import dataclass


def get_euclidean_distance(point1, point2):
    return math.sqrt((point2.x - point1.x) ** 2 + (point2.y - point1.y) ** 2 + (point2.z - point1.z) ** 2)


class Finger:
    def __init__(self, statuses_range: int, landmarks: List[int], name: str = "Finger"):
        self.statuses = statuses_range
        self.current_status = 0
        self.MCP = landmarks[0]
        self.PIP = landmarks[1]
        self.DIP = landmarks[2]
        self.TIP = landmarks[3]
        self.name = name

    def set_status(self, status: int):
        if status == self.current_status: return
        self.current_status = status

    def get_status(self):
        # limit the angle to be between 0 and 90 rather than 0 and 180
        # angle_new = self.__angle if self.__angle < 90 else 180 - self.__angle
        return self.current_status

    def __repr__(self):
        # print the name, status, angle, and all statuses of the finger
        return f"{self.name} - Status: {self.get_status()} - Statuses: {self.statuses}"


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