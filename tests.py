import numpy as np
import math

# test takeoff logic #

# 5m by 5m by 3m room

ROOM_X = 5
ROOM_Y= 5
ROOM_HEIGHT = 3

INITIAL_LOCATION = [1.5,2,0.5] # Test initial location [X, Y, Height]

INITIAL_ORIENTATION = 90 #0 is facing +X, 90 facing +Y, 180 facing -X and 270 facing -Y 

def distance(x,y,angle):
    cos_angle, sin_angle = math.cos(angle), math.sin(angle)
    if cos_angle == 0:
        return y if sin_angle < 0 else ROOM_Y - y
    if sin_angle == 0:
        return x if cos_angle < 0 else ROOM_X - x
    distance_EW = (ROOM_X-x)/cos_angle if cos_angle>0 else -x/cos_angle
    distance_NS = (ROOM_Y-y)/sin_angle if sin_angle>0 else -y/sin_angle
    return min(distance_EW, distance_NS)


def getTestLidarData(location, initialAngle): #get all 360 degrees
    lidarData = [] #[distance, angle]
    for i in range(initialAngle, initialAngle+360):
        angle = i*(np.pi/180)
        print(f"Angle: {angle}")
        print(f"Distance:{distance(location[0], location[1], angle)}")
        lidarData.append([distance(location[0], location[1], angle),angle-initialAngle*(np.pi/180)]) # subtract initialAngle to get relative angle in comparison to initial orientation 
    return lidarData


def getLowestDistance(lidarData): # type: ignore
    lowestDistance = 10000000
    angle = 0
    for i in lidarData:
        if i[0] < lowestDistance:
            lowestDistance = i[0]
            angle = i[1]
    return [lowestDistance, angle]




print(getLowestDistance(getTestLidarData(INITIAL_LOCATION, INITIAL_ORIENTATION)))