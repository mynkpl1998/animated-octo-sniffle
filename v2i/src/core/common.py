import os
import yaml
import pickle
import numpy as np
from huepy import bad, bold, red

from v2i.src.core.constants import LANE_MAP_INDEX_MAPPING, SCENE_CONSTS

def getAgentObject(laneMap):
    for lane in laneMap.keys():
        for veh in laneMap[lane]:
            if veh[LANE_MAP_INDEX_MAPPING['agent']]:
                return veh
    return None

def checkFileExists(file):
    return os.path.isfile(file)

def readYaml(file):
    with open(file, "r") as handle:
        configDict = yaml.load(handle, Loader=yaml.FullLoader)
    return configDict

def raiseValueError(msg):
    raise ValueError(bad(bold(red(msg))))

def savePKL(data, filenamePath):
    '''

    Function : saves the data object in a serialized format at the given path
    
    Input Args : 
        1. data - the data object which needs to be serialized.
        2. filenamePath - the complete path to the location to save including file name

    Return Args:
        returns True if successfully saved else return False
    
    '''
    
    with open(filenamePath, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
        return True
    return False

def loadPKL(filenamePath):
    
    '''

    Function : load the serialized object from the given file.
    
    Input Args : 
        1. filenamePath - absolute path of the file to load

    Return Args:
        returns the loaded object if successfully loaded else raise value error with exception as the message.
    
    '''

    try:
        with open(filenamePath, "rb") as handle:
            trajecDict = pickle.load(handle)
        return trajecDict
    except Exception as e:
        raiseValueError(e)

def arcAngle(radius, arcLength):
    return np.rad2deg(arcLength/radius)

def getAgentID(laneMap, agentLane):
    agentID = np.where(laneMap[agentLane]['agent'] == 1)[0]
    return agentID[0]

def getTfID(laneMap, lane):
    TfID = np.where(laneMap[lane]['agent'] == 2)[0]
    return TfID[0]

def arcLength(radius, arcAngleDeg):
    return np.deg2rad(arcAngleDeg) * radius

def reverseDict(dictToReverse):
    return dict(map(reversed, dictToReverse.items()))

def buildDictWithKeys(keys, initValue):
    d = {}
    for key in keys:
        d[key] = initValue
    return d.copy()

def mergeDicts(d1, d2):
    d = {}
    for key in d1.keys():
        d[key] = d1[key]
    
    for key in d2.keys():
        d[key] = d2[key]
    
    assert len(d) == len(d1) + len(d2)
    
    return d

def sortListofList(laneMap, index, reverse=False):
    laneMap.sort(key = lambda laneMap: laneMap[index], reverse=reverse)

def removeVehicles(laneMap, low, high):
    for lane in laneMap.keys():
        newMap = []
        for veh in laneMap[lane]:
            if (veh[LANE_MAP_INDEX_MAPPING['pos']] >= (low - SCENE_CONSTS['CAR_LENGTH']) and veh[LANE_MAP_INDEX_MAPPING['pos']] <= high):
                newMap.append(veh)
        laneMap[lane] = newMap

def addFromTop(laneMap, randomizeProb, args):  
    # Check if any lane is empty. Add a vehicle from top.
    for lane in range(0, args.getValue('lanes')):
        if len(laneMap[lane]) == 0:
            if np.random.rand() <= randomizeProb:
                vehTup = [lane, False, 0.0 - SCENE_CONSTS['CAR_LENGTH'], 0.0, 0.0]
                laneMap[lane].append(vehTup)
        else:
            
            topVehicle = laneMap[lane][0]
            topVehicleReadBumperPosition = topVehicle[LANE_MAP_INDEX_MAPPING['pos']]
            distYBump = topVehicleReadBumperPosition - 0.0
            if distYBump > (0 + SCENE_CONSTS['MIN_CAR_DISTANCE']):
                if np.random.rand() <= randomizeProb:
                    veh = [lane, False, 0.0 - SCENE_CONSTS['CAR_LENGTH'], 0.0, 0.0]
                    laneMap[lane].append(veh)
            #pass

def addFromBottom(laneMap, randomizeProb, args):
    # Check if any lane is empty. Add a vehicle from bottom.
    # Useful when agent is not moving at all and all vehicles leaves the scenes. 
    for lane in range(0, args.getValue('lanes')):
        if len(laneMap[lane]) == 0:
            if np.random.rand() <= randomizeProb:
                vehTup = [lane, False, SCENE_CONSTS['ROAD_LENGTH'], 0.0, 0.0]
                laneMap[lane].append(vehTup)
        else:
            lastVehicle = laneMap[lane][-1]
            lastVehicleRearBumperPosition = lastVehicle[LANE_MAP_INDEX_MAPPING['pos']] + SCENE_CONSTS['CAR_LENGTH']
            distY2Bump = SCENE_CONSTS['ROAD_LENGTH'] - lastVehicleRearBumperPosition
            if distY2Bump > (0 + SCENE_CONSTS['MIN_CAR_DISTANCE']):
                if np.random.rand() <= randomizeProb:
                    veh = [lane, False, SCENE_CONSTS['ROAD_LENGTH'], 0.0, 0.0]
                    laneMap[lane].append(veh)


def addVehicles(laneMap, randomizeProb, args, dist):

    agentLane, agentIndex = getAgent(laneMap)
    agentSpeed = laneMap[agentLane][agentIndex][LANE_MAP_INDEX_MAPPING['speed']]
    ratio = agentSpeed / args.getValue('max-speed')
    randomizeProb *= ratio
    print(randomizeProb)
    # Sort the list first before adding vehicles
    for lane in range(0, args.getValue('lanes')):
        sortListofList(laneMap[lane], LANE_MAP_INDEX_MAPPING['pos'], reverse=False)

    if dist == 0:
        addFromBottom(laneMap, randomizeProb, args)
    else:
        addFromTop(laneMap, randomizeProb, args)    
    
def getAgent(laneMap, ):
    agentLane = None
    agentIndex = None

    for lane in laneMap.keys():
        for idx, veh in enumerate(laneMap[lane]):
            if veh[LANE_MAP_INDEX_MAPPING['agent']]:
                agentLane = lane
                agentIndex = idx
    return agentLane, agentIndex