import numpy as np

from v2i.src.core.common import sortListofList, getAgent
from v2i.src.core.constants import LANE_MAP_INDEX_MAPPING, IDM_CONSTS, SCENE_CONSTS

class agentPlanner:

    def __init__(self, simArgs):
        self.simArgs = simArgs
    
    def speed(self, speed, acc, tPeriod):
        return speed + (acc * tPeriod)
    
    def distTravelled(self, speed, acc, tPeriod):
        return (speed*tPeriod) + (0.5 * acc * tPeriod * tPeriod)
    
    def executeNothing(self, speed):
        return np.clip(self.speed(speed, 0.0, self.simArgs.getValue('t-period')), 0.0, self.simArgs.getValue('max-speed')), np.clip(self.distTravelled(speed, 0.0, self.simArgs.getValue('t-period')), 0.0, None)
    
    def executeDeceleration(self, speed):
        dec = None
        if speed <= 0.0:
            dec = 0.0
        else:
            dec = -IDM_CONSTS['DECELERATION_RATE']
        
        return np.clip(self.speed(speed, dec, self.simArgs.getValue('t-period')), 0.0, self.simArgs.getValue('max-speed')), np.clip(self.distTravelled(speed, dec, self.simArgs.getValue('t-period')), 0.0, None)
    
    def executeAcc(self, speed):
        acc = None
        if speed >= self.simArgs.getValue('max-speed'):
            acc = 0.0
        else:
            acc = IDM_CONSTS['MAX_ACC']
        return np.clip(self.speed(speed, acc, self.simArgs.getValue('t-period')), 0.0, self.simArgs.getValue('max-speed')), np.clip(self.distTravelled(speed, acc, self.simArgs.getValue('t-period')), 0.0, None)
    
    def checkCollision(self, laneMap, agentLane, agentIndex, dist):
        if agentIndex == 0:
            return False
        frontVehiclePosStart = laneMap[agentLane][agentIndex-1][LANE_MAP_INDEX_MAPPING['pos']]
        frontVehiclePosEnd = laneMap[agentLane][agentIndex-1][LANE_MAP_INDEX_MAPPING['pos']] + SCENE_CONSTS['CAR_LENGTH']
        agentNewPos = laneMap[agentLane][agentIndex][LANE_MAP_INDEX_MAPPING['pos']] - dist
        
        if agentNewPos >= frontVehiclePosStart and agentNewPos <= frontVehiclePosEnd:
            return True
        else:
            return False

    def step(self, laneMap, action):

        # Sort the list in-place by pos
        for lane in range(0, self.simArgs.getValue('lanes')):
            sortListofList(laneMap[lane], LANE_MAP_INDEX_MAPPING['pos'], reverse=False)
        
        # Find agent lane and postion
        agentLane, agentIndex = getAgent(laneMap)

        # Agent properties
        agentSpeed = laneMap[agentLane][agentIndex][LANE_MAP_INDEX_MAPPING['speed']]
        agentPos = laneMap[agentLane][agentIndex][LANE_MAP_INDEX_MAPPING['pos']]

        # Calculate agent new Speed, dist. travelled based upon the action selected
        if action == "acc":
            newSpeed, distTrav = self.executeAcc(agentSpeed)
        elif action == 'dec':
            newSpeed, distTrav = self.executeDeceleration(agentSpeed)
        elif action == 'do-nothing':
            newSpeed, distTrav = self.executeNothing(agentSpeed)
        
        # Check for collision
        result = self.checkCollision(laneMap, agentLane, agentIndex, distTrav)

        # If collision occurs - reset to previous place
        if result:
            newSpeed = 0.0
            distTrav = 0.0
        
        # Update agent speed
        laneMap[agentLane][agentIndex][LANE_MAP_INDEX_MAPPING['speed']] = newSpeed        

        return result, distTrav