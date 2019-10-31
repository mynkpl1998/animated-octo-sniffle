import time
import pygame
import numpy as np

from v2i.src.core.constants import UI_CONSTS, SCENE_CONSTS, LANE_MAP_INDEX_MAPPING
from v2i.src.core.common import raiseValueError, getAgentObject

class ui:

    def __init__(self, simArgs, startPoints):
        self.simArgs = simArgs
        self.startPointsPixels = startPoints * UI_CONSTS['SCALE']

        # Init graphics library - pygame
        pygame.init()
        pygame.font.init()

        # Init lanes coordinates
        self.initLaneCoordinates()

        # Init colors
        self.initColors()

        # Init clock
        self.initClock()

        # Init fonts
        self.initFonts()

        # Init screen
        self.initScreen()

        # Init images
        self.initImages()

        # Init construction board
        self.initBoard()
        
    def initColors(self):
        self.roadColor = (97, 106, 107)
        self.colorBG = (30, 132, 73)
        self.colorWhite = (255, 255, 255)
        self.colorRed = (236, 112, 99)
        self.colorDarkRed = (255, 0, 0)
        self.colorYellow = (247, 220, 111)
        self.colorGrey = (192, 192, 192, 80)
        self.colorLime = (128, 250, 0)
        self.colorDarkGreen = (0, 120, 0)
        self.colorBlack = (0, 0, 0)
    
    def initBoard(self):
        self.BoardX = (UI_CONSTS['LANE_WIDTH'] + UI_CONSTS['LANE_BOUNDARY_WIDTH']) * self.simArgs.getValue('lanes') + 20
        self.BoardY = 0.0
    
    def initImages(self):
        self.BoardImg = pygame.transform.scale(pygame.image.load('v2i/src/data/images/signBoard.png').convert_alpha(), (50, 50))
    
    def initLaneCoordinates(self):
        self.laneCoordinates = []
        if UI_CONSTS['CAR_WIDTH'] >= UI_CONSTS['LANE_WIDTH']:
            raiseValueError("car length can't be greater than lane width...")
        
        startPointX = UI_CONSTS['LANE_BOUNDARY_WIDTH']
        endPointX = startPointX + UI_CONSTS['LANE_WIDTH']
        for lane in range(0, self.simArgs.getValue("lanes")):
            diff = (endPointX - startPointX)
            point = int(startPointX +  (diff / 2.0) - (UI_CONSTS['CAR_WIDTH']/2.0))
            startPointX = endPointX + UI_CONSTS['LANE_BOUNDARY_WIDTH']
            endPointX = startPointX + UI_CONSTS['LANE_WIDTH']
            self.laneCoordinates.append(point)
    
    def initFonts(self):
        self.fontNormal = pygame.font.Font("v2i/src/data/fonts/RobotoSlab-Bold.ttf", UI_CONSTS['FONT_SIZE_NORMAL'])
        self.fontSmall = pygame.font.Font("v2i/src/data/fonts/RobotoSlab-Bold.ttf", UI_CONSTS['FONT_SIZE_SMALL'])
        
    def initClock(self):
        self.clock = pygame.time.Clock()
    
    def initScreen(self):
        self.dimX = int((UI_CONSTS['LANE_WIDTH'] * self.simArgs.getValue('lanes')) + UI_CONSTS['INFO_BOX_WIDTH'])
        self.dimY = int(UI_CONSTS['SCALE'] * SCENE_CONSTS['ROAD_LENGTH'])
        self.screen = pygame.display.set_mode((self.dimX, self.dimY))
        pygame.display.set_caption("V2I")
    
    def drawRoads(self):
        startPointX = UI_CONSTS['LANE_BOUNDARY_WIDTH']
        width = UI_CONSTS['LANE_WIDTH']
        height = self.dimY
        for lane in range(0, self.simArgs.getValue("lanes")):
            pos = (startPointX, 0)
            self.drawRect(self.screen, self.roadColor, pos, width, height, width=0)
            startPointX += UI_CONSTS['LANE_BOUNDARY_WIDTH'] + UI_CONSTS['LANE_WIDTH']

    def drawRect(self, screen, color, pos, Recwidth, height, width):
        return pygame.draw.rect(screen, color, [pos[0], pos[1], Recwidth, height], width)
    
    def drawLaneBoundaries(self):
        startPointX = 0
        for lane in range(0, self.simArgs.getValue("lanes") + 1):
            pos1 = (startPointX, 0)
            pos2 = (startPointX, self.dimY)
            self.drawLine(self.screen, pos1, pos2, self.colorWhite, width=UI_CONSTS['LANE_BOUNDARY_WIDTH'])
            startPointX += UI_CONSTS['LANE_BOUNDARY_WIDTH'] + UI_CONSTS['LANE_WIDTH']

    def drawLine(self, screen, pos1, pos2, color, width):
        return pygame.draw.line(screen, color, pos1, pos2, width)
    
    def str2font(self, msg, font, color):
        return font.render(msg, False, color)
    
    def writeLaneNumber(self):
        startPointX = UI_CONSTS['LANE_BOUNDARY_WIDTH'] + 4
        for lane in range(0, self.simArgs.getValue("lanes")):
            pos = (startPointX, 0)
            laneStr = 'lane : %d'%(lane)
            laneStrObject = self.str2font(laneStr, self.fontSmall, self.colorBlack)
            self.screen.blit(laneStrObject, pos)
            startPointX += UI_CONSTS['LANE_WIDTH'] + UI_CONSTS['LANE_BOUNDARY_WIDTH']
        
    def drawCircle(self, screen, color, center, radius, width):
        return pygame.draw.circle(screen, color, center, radius, width)
    
    def drawCars(self, laneMap):
        for lane in range(self.simArgs.getValue('lanes')):
            for veh in laneMap[lane]:
                lane = veh[LANE_MAP_INDEX_MAPPING['lane']]
                pos = veh[LANE_MAP_INDEX_MAPPING['pos']]
                agent = veh[LANE_MAP_INDEX_MAPPING['agent']]
                color = self.colorYellow
                if agent:
                    color = self.colorLime
                self.drawRect(self.screen, color, (self.laneCoordinates[lane], pos * UI_CONSTS['SCALE']), UI_CONSTS['CAR_WIDTH'] , SCENE_CONSTS['CAR_LENGTH'] * UI_CONSTS['SCALE'], width=0)
    
    def drawInfoBoard(self, vehicles):
        vehicle = getAgentObject(vehicles)
        
        if vehicle is None:
            raiseValueError("ego vehicle not found...")
    
        startPointX = (UI_CONSTS['LANE_WIDTH'] + UI_CONSTS['LANE_BOUNDARY_WIDTH']) * self.simArgs.getValue('lanes') + 90
        PointY = 10
        
        agentLaneStr = "1. Agent lane : %d"%(vehicle[LANE_MAP_INDEX_MAPPING['lane']])
        agentLaneStrText = self.str2font(agentLaneStr, self.fontNormal, self.colorBlack)
        self.screen.blit(agentLaneStrText, (startPointX, PointY))
        PointY += UI_CONSTS['INFO_BOARD_GAP']

        agentSpeedStr = "2. Agent speed : %.2f km/hr"%(vehicle[LANE_MAP_INDEX_MAPPING['speed']] * 3.6)
        agentSpeedStrText = self.str2font(agentSpeedStr, self.fontNormal, self.colorBlack)
        self.screen.blit(agentSpeedStrText, (startPointX, PointY))
        PointY += UI_CONSTS['INFO_BOARD_GAP']
    
    def drawBoard(self, distTravelled):
        self.BoardY += ((distTravelled * UI_CONSTS['SCALE']) % self.dimY)
        self.screen.blit(self.BoardImg, [self.BoardX,self.BoardY])

    
    def updateScreen(self, vehicles, distTravelled):
        
        # Clear screen
        self.screen.fill(self.colorBG)
        
        # Draw lane boundary
        self.drawLaneBoundaries()

        # Draw roads
        self.drawRoads()

        # Write lane numbers
        self.writeLaneNumber()

        # Draw Cars
        self.drawCars(vehicles)

        # Draw Information board
        self.drawInfoBoard(vehicles)

        # Draw Construction board
        self.drawBoard(distTravelled)

        # Draw all changes
        pygame.display.flip()
        
        # Fps clock
        self.clock.tick(self.simArgs.getValue("fps"))


    
    
    
