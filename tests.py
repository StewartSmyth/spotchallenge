import numpy as np
import math

# test takeoff logic #

# 5m by 5m by 3m room

ROOM_X = 5
ROOM_Y= 5
ROOM_HEIGHT = 3

INITIAL_LOCATION = [2, 2.1,0.5] # Test initial location [X, Y, Height]

INITIAL_ORIENTATION = 22 #0 is facing +X, 90 facing +Y, 180 facing -X and 270 facing -Y 

DISTANCE_FROM_WALLS = 1 #1 meter from walls

class Drone:
    def __init__(self, xPos, yPos):
        self.xPos = xPos
        self.yPos = yPos
    def setDronePos(self, xChange, yChange):
        self.xPos+=xChange
        self.yPos+=yChange


def distance(x,y,angle):
    cos_angle, sin_angle = math.cos(angle), math.sin(angle)
    if cos_angle == 0:
        return y if sin_angle < 0 else ROOM_Y - y
    if sin_angle == 0:
        return x if cos_angle < 0 else ROOM_X - x
    distance_EW = (ROOM_X-x)/cos_angle if cos_angle>0 else -x/cos_angle
    distance_NS = (ROOM_Y-y)/sin_angle if sin_angle>0 else -y/sin_angle
    return min(distance_EW, distance_NS)-DISTANCE_FROM_WALLS


def getTestLidarData(location, initialAngle): #get all 360 degrees
    lidarData = [] #[distance, angle]
    initialAngle=int(initialAngle)
    for i in range(initialAngle, initialAngle+360):
        angle = i*(np.pi/180) #turn angle into radians

        lidarData.append([distance(location[0], location[1], angle),angle*180/np.pi-initialAngle]) # subtract initialAngle to get relative angle in comparison to initial orientation and return in degrees
    return lidarData


def getLowestDistance(lidarData): # type: ignore
    lowestDistance = 10000000
    angle = 0
    for i in lidarData:
        if i[0] < lowestDistance:
            lowestDistance = i[0]
            angle = i[1]

    print(angle)
    return [lowestDistance, angle]



def droneToWall(drone):
    lidarData = getTestLidarData(INITIAL_LOCATION, INITIAL_ORIENTATION)
    lowestDistance = getLowestDistance(lidarData)
    xChange = lowestDistance[0] * np.cos((INITIAL_ORIENTATION+lowestDistance[1])*np.pi/180)
    yChange = lowestDistance[0] * np.sin((INITIAL_ORIENTATION+lowestDistance[1])*np.pi/180)
    drone.setDronePos(xChange, yChange)
    return(lowestDistance[1]) #return the angle

def droneToCorner(drone, relAngle):
    lidarData = getTestLidarData([drone.xPos, drone.yPos], relAngle)

    #always coming into corner perpendicular so only need to check angles at 90 degrees 
    print(relAngle)

    for i in lidarData:
        if int(i[1]) == relAngle+90 or int(i[1]) == relAngle-270:
            plusNinty=i
        elif int(i[1]) == relAngle-90 or int(i[1]) == relAngle+270:
            plusTwoSeventy=i





    closestCorner = plusNinty if(plusNinty[0] < plusTwoSeventy[0]) else plusTwoSeventy


    xChange = closestCorner[0] * np.cos((relAngle+closestCorner[1])*np.pi/180)
    yChange = closestCorner[0] * np.sin((relAngle+closestCorner[1])*np.pi/180)


    drone.setDronePos(xChange, yChange)





def run():
    drone = Drone(INITIAL_LOCATION[0], INITIAL_LOCATION[1])
    relativeWallAngle = droneToWall(drone)
    print(drone.xPos, " ", drone.yPos)
    
    droneToCorner(drone, relativeWallAngle)
    
    print(drone.xPos, " ", drone.yPos)
    

if __name__ == "__main__":
    run()