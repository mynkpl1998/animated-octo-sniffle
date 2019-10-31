import numpy as np

from v2i.src.core.constants import SCENE_CONSTS, IDM_CONSTS, LANE_MAP_INDEX_MAPPING
from v2i.src.core.common import sortListofList

class idm:

    def __init__(self, simArgs):
        self.simArgs = simArgs

        #----- Vectorized functions -----#
        self.vecBumpBumpDistance = np.vectorize(self.BumpBumpDist)
        self.vecidmAcc = np.vectorize(self.idmAcc)
        self.vecDistTravelled = np.vectorize(self.distanceTravelled)
        self.vecNewSpeed = np.vectorize(self.newSpeed)
        self.vecUpdateKey = np.vectorize(self.updateKey)
        #----- Vectorized functions -----#
    
    def getElementsbyKey(self, laneMap, key):
        prop = []
        for veh in laneMap:
            prop.append(veh[LANE_MAP_INDEX_MAPPING[key]])
        return np.array(prop)
    
    def posDiff(self, laneMap):
        a = self.getElementsbyKey(laneMap, 'pos')
        b = np.zeros(a.shape)
        b[1:] = a[0:-1]
        diff = a - b
        diff[0] = 100.0
        return diff
    
    def relativeSpeed(self, laneMap):
        a = self.getElementsbyKey(laneMap, 'speed')
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
    
    def distanceTravelled(self, speed, acc, tPeriod):
        dist = (speed * tPeriod) + (0.5 * acc * tPeriod * tPeriod)
        return dist
    
    def newSpeed(self, speed, acc, tPeriod):
        v = speed + (acc * tPeriod)
        return v
    
    def newPosition(self, oldPos, distTravelled):
        return oldPos - distTravelled
    
    def updateKey(self, laneMap, key, values):
        for idx, veh in enumerate(laneMap):
            if not veh[LANE_MAP_INDEX_MAPPING['agent']]:
                veh[LANE_MAP_INDEX_MAPPING[key]] = values[idx]
    
    def step(self, laneMap, agentDistTravelled):
        
        # Sort the list in-place by pos
        for lane in range(0, self.simArgs.getValue('lanes')):
            sortListofList(laneMap[lane], LANE_MAP_INDEX_MAPPING['pos'], reverse=False)
        
        for lane in range(0, self.simArgs.getValue('lanes')):
            oldPos = self.getElementsbyKey(laneMap[lane], 'pos')
            possDiff = self.posDiff(laneMap[lane])
            speedDiff = self.relativeSpeed(laneMap[lane])
            sAlpha = self.vecBumpBumpDistance(possDiff)
            speed = self.getElementsbyKey(laneMap[lane], 'speed')
            idmAcc = self.vecidmAcc(sAlpha, speedDiff, speed)

            distTravelledVec = self.vecDistTravelled(speed, idmAcc, self.simArgs.getValue('t-period'))
            newSpeedVec = self.vecNewSpeed(speed, idmAcc, self.simArgs.getValue('t-period'))
            
            # ---- Failsafe ---- #
            distTravelledVec[distTravelledVec < 0] = 0.0
            newSpeedVec[newSpeedVec < 0] = 0.0
            # ---- Failsafe ---- #

            distTravelledVec =  distTravelledVec - agentDistTravelled            

            newPosVec = self.newPosition(oldPos, distTravelledVec)

            self.updateKey(laneMap[lane], 'pos', newPosVec)
            self.updateKey(laneMap[lane], 'speed', newSpeedVec)
        