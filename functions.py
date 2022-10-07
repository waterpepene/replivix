import multiprocessing
import threading
import time
from typing import List
from numpy.lib import math
from dataclasses import dataclass


class Finger:
    def __init__(self, statuses_range: int, landmarks: List[int]):
        self.statuses = range(1, statuses_range)
        self.current_status = 0
        self.MCP = landmarks[0]
        self.PIP = landmarks[1]
        self.DIP = landmarks[2]
        self.TIP = landmarks[3]


# create an ENUM for all 5 fingers
class Hand:
    THUMB = Finger(statuses_range=4, landmarks=[1, 2, 3, 4])
    INDEX = Finger(statuses_range=5, landmarks=[5, 6, 7, 8])
    MIDDLE = Finger(statuses_range=5, landmarks=[9, 10, 11, 12])
    RING = Finger(statuses_range=5, landmarks=[13, 14, 15, 16])
    PINKY = Finger(statuses_range=5, landmarks=[17, 18, 19, 20])


# @dataclass
# class Communication:
#     communication_queue = multiprocessing.Queue()
#     capture_movement_process = None
#     video = None


# by default, exit all processes after 60 seconds
# this is to prevent the program from running forever
def kill_processes():
    # exit all processes under the main process
    children = multiprocessing.active_children()
    for child in children:
        child.terminate()
        child.join()
    exit("Processes killed")


threading.Timer(60, kill_processes).start()


def get_euclidean_distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
