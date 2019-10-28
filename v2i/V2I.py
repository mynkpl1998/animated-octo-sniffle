import os
import sys
import gym
import numpy as np

from v2i.src.core.utils import configParser
from v2i.src.core.constants import TRAFFIC_DENSITIES, SCENE_CONSTS, UI_CONSTS
from v2i.src.core.common import raiseValueError
from v2i.src.core.vehicle import vehicle
from v2i.src.core.idm import idm
from v2i.src.ui.ui import ui

class V2I(gym.Env):

    def __init__(self, config):

        # Parse config file and return the handle
        self.simArgs = configParser(config)
        
        # Set the seed of random generator for reproduciblity
        self.seed(self.simArgs.getValue("seed"))

        # traffic densities to simulate
        self.densities = np.array(TRAFFIC_DENSITIES)

        # Init scenario
        self.initScenario()
        
        # Init handlers
        self.init()
    
    def seed(self, value=0):
        np.random.seed(value)
    
    def init(self):

        # Initialize UI handler here
        if self.simArgs.getValue("render"):
            self.uiHandler = ui(self.simArgs, self.startPoints)
        
        # Intialize IDM handler here
        self.idmHandler = idm(self.simArgs)
    
    def initScenario(self):
        # Calculate maximum number of cars that can be accomodated in a lane
        self.maxCarsInLane = int(SCENE_CONSTS['ROAD_LENGTH'] / (SCENE_CONSTS['CAR_LENGTH'] + SCENE_CONSTS['MIN_CAR_DISTANCE']))
        if self.maxCarsInLane < 1:
            raiseValueError("A lane should have atleast one car...")
        
        # Check for valid number of lanes
        if self.simArgs.getValue("lanes") < 2:
            raiseValueError("number of lanes should be atleast two...")
        
        # Calculate initial postion of the cars
        startY = 5
        self.startPoints = []
        self.startPoints.append(startY)
        for i in range(0, self.maxCarsInLane - 1):
            startY += (SCENE_CONSTS['CAR_LENGTH'] + SCENE_CONSTS['MIN_CAR_DISTANCE']) 
            self.startPoints.append(startY)
        self.startPoints = np.array(self.startPoints)
        assert len(self.startPoints) == self.maxCarsInLane

        # Find the index for ego-vehicle
        self.egoMidIndex = int(len(self.startPoints)/2.0)
    
    def initVehicles(self, prob):
        self.vehicles = []

        # Init id count
        self.vehID = 0

        # Generate random lane for ego-vehicle
        randomLane = np.random.randint(0, self.simArgs.getValue("lanes"))
         
        # Add non-ego vehicles
        for lane in range(self.simArgs.getValue("lanes")):
            for idx, pos in enumerate(self.startPoints):
                if idx == self.egoMidIndex and lane == randomLane:
                    pass
                else:
                    if np.random.rand() <= prob:
                        veh = vehicle(lane, False, pos, self.vehID, 0.0, 0.0)
                        self.vehID += 1
                        self.vehicles.append(veh)
        
        # Add ego-vehicle to list
        self.vehicles.append(vehicle(randomLane, True, self.startPoints[self.egoMidIndex], self.vehID, 0.0, 0.0))
        self.vehID += 1
        assert self.vehicles[-1].vehID+1 == len(self.vehicles)
        
    def reset(self, prob=None):
        
        # Get episode density
        if prob is None:
            prob = np.random.choice(self.densities)
        
        # Get initial vehicles and thier positions
        self.initVehicles(prob)

        # Render to display
        if self.simArgs.getValue("render"):
            self.uiHandler.updateScreen(self.vehicles)


    def step(self):
        
        self.idmHandler.step(self.vehicles)
