import numpy as np

from v2i.src.core.constants import SCENE_CONSTS, IDM_CONSTS

class idm:

    def __init__(self, simArgs):
        self.simArgs = simArgs

        #----- Vectorized functions -----#
        self.vecBumpBumpDistance = np.vectorize(self.BumpBumpDist)
        self.vecidmAcc = np.vectorize(self.idmAcc)
        #----- Vectorized functions -----#
    
    def extractVehiclesByLane(self, vehicles):
        laneMap = {}
        for lane in range(0, self.simArgs.getValue("lanes")):
            laneMap[lane] = []
        
        for vehicle in vehicles:
            vehLane = vehicle.lane
            laneMap[vehLane].append(vehicle)
        return laneMap
    
    def getObjectsPos(self, laneMap):
        pos = []
        for vehicle in laneMap:
            pos.append(vehicle.pos)
        return np.array(pos)
    
    def getObjectsSpeed(self, laneMap):
        speeds = []
        for vehicle in laneMap:
            speeds.append(vehicle.speed)
        return np.array(speeds)
    
    def posDiff(self, laneMap):
        a = self.getObjectsPos(laneMap)
        b = np.zeros(a.shape)
        b[1:] = a[0:-1]
        diff = a - b
        diff[0] = 100.0
        return diff
    
    def relativeSpeed(self, laneMap):
        a = self.getObjectsSpeed(laneMap)
        b = np.zeros(a.shape)
        b[1:] = a[0:-1]
        diff = a - b
        diff[0] = 0.0
        return diff
    
    def BumpBumpDist(self, gap):
        return gap - SCENE_CONSTS['CAR_LENGTH']
    
    def idmAcc(self, sAlpha, speedDiff, speed):
        sStar = IDM_CONSTS['MIN_SPACING'] + (speed * IDM_CONSTS['HEADWAY_TIME']) + ((speed * speedDiff)/(2 * np.sqrt(IDM_CONSTS['MAX_ACC'] * IDM_CONSTS['DECELERATION_RATE'])))
        acc = IDM_CONSTS['MAX_ACC'] * (1 - ((speed / self.simArgs.getValue('max-speed'))**IDM_CONSTS['DELTA']) - ((sStar/sAlpha)**2))
        return acc
        
    
    def step(self, vehicles):
        
        # Extract vehicles object - lane by lane
        laneMap = self.extractVehiclesByLane(vehicles)

        # Sort the list in-place by post
        
        for lane in range(0, self.simArgs.getValue("lanes")):
            laneMap[lane].sort(key=lambda veh: veh.pos, reverse=False)

        for lane in range(0, self.simArgs.getValue('lanes')):
            oldPos = self.getObjectsPos(laneMap[lane])
            posDiff = self.posDiff(laneMap[lane])
            speedDiff = self.relativeSpeed(laneMap[lane])
            speed = self.getObjectsSpeed(laneMap[lane])
            sAlpha = self.vecBumpBumpDistance(posDiff)
            acc = self.vecidmAcc(sAlpha, speedDiff, speed)
            print(acc)
        
        '''
        for lane in range(0, self.simArgs.getValue('lanes')):
            print("lane %d : "%(lane))
            for vehicle in laneMap[lane]:
                print(vehicle.pos)
        '''