import os
import sys
import gym
import numpy as np

from v2i.src.core.utils import configParser
from v2i.src.core.constants import TRAFFIC_DENSITIES, SCENE_CONSTS, UI_CONSTS
from v2i.src.core.common import raiseValueError
from v2i.src.core.vehicle import vehicle
from v2i.src.core.idm import idm
from v2i.src.core.agentPlanner import agentPlanner
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

        # Initialize agent handler here
        self.agentPlannerhandler = agentPlanner(self.simArgs)
    
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
        # create empty map
        self.laneMap = {}
        for lane in range(0, self.simArgs.getValue("lanes")):
            self.laneMap[lane] = []

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
                        # (lane, agent, position, vehicleID, speed, acceleration)
                        veh = [lane, False, pos, self.vehID, 0.0, 0.0]
                        self.vehID += 1
                        self.laneMap[lane].append(veh)
        
        # Add ego-vehicle to list
        veh = [randomLane, True, self.startPoints[self.egoMidIndex], self.vehID, 0.0, 0.0]
        self.laneMap[randomLane].append(veh)
        self.vehID += 1

        # Assert the vehID and total number of vehicles in lane Map
        count = 0
        for lane in range(0, self.simArgs.getValue('lanes')):
            count += len(self.laneMap[lane])
        assert count == self.vehID

    def reset(self, prob=None):
        
        # Get episode density
        if prob is None:
            prob = np.random.choice(self.densities)
        
        # Get initial vehicles and thier positions
        self.initVehicles(prob)
        
        # Render to display
        if self.simArgs.getValue("render"):
            self.uiHandler.initBoard()
            self.uiHandler.updateScreen(self.laneMap, 0.0, None, None)


    def step(self, action):
        
        # Agent planner
        collision, distTravelled = self.agentPlannerhandler.step(self.laneMap, action)

        self.idmHandler.step(self.laneMap, distTravelled)

        # Render to display
        if self.simArgs.getValue("render"):
            self.uiHandler.updateScreen(self.laneMap, distTravelled, action, None)
        
        return collision