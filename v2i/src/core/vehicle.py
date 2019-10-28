import numpy as np

class vehicle:
    def __init__(self, lane, agent, pos, vehID, speed, acc):
        self.lane = lane
        self.agent = agent
        self.pos = pos
        self.vehID = vehID
        self.speed = speed
        self.acc = acc