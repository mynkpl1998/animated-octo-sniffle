TRAFFIC_DENSITIES = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

# UI Related constants
UI_CONSTS = {
    'SCALE': 6.0, # x pixesl = 1m
    'FONT_SIZE_NORMAL' : 17,
    'FONT_SIZE_SMALL' : 12,
    'LANE_WIDTH': 50,
    'INFO_BOX_WIDTH': 380,
    'LANE_BOUNDARY_WIDTH': 2,
    'CAR_WIDTH': 20,
    'INFO_BOARD_GAP': 30
}

# Scenario Settings
SCENE_CONSTS = {
    'ROAD_LENGTH': 100, # in metres
    'CAR_LENGTH': 4.5, # in metres
    'MIN_CAR_DISTANCE': 2.0 # in metres
}

# Intelligent Driver Model constants
IDM_CONSTS = {
    'MAX_ACC': 0.73,
    'HEADWAY_TIME': 1.5,
    'DECELERATION_RATE': 1.67,
    'MIN_SPACING': 2.0,
    'DELTA': 4 
}

# Index mapping for laneMap
LANE_MAP_INDEX_MAPPING = {
    'lane': 0,
    'agent': 1,
    'pos': 2,
    'id': 3,
    'speed': 4,
    'acc':5
}