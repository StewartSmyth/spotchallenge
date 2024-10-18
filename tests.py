import numpy as np
import math

import matplotlib.pyplot as plt


plt.style.use('_mpl-gallery')

# test takeoff logic #

# 5m by 5m by 3m room


# 6 by 6 room gets data with inputs of 5x5
ROOM_X = 10
ROOM_Y= 12
ROOM_HEIGHT = 3

ROOM_RADIUS = 5


INITIAL_LOCATION = [1.5, 3.3, 0.5] # Test initial location [X, Y, Height]

INITIAL_ORIENTATION = 0 #0 is facing +X, 90 facing +Y, 180 facing -X and 270 facing -Y 

DISTANCE_FROM_WALLS = 1 #1 meter from walls

class Drone:
    def __init__(self, xPos, yPos):
        self.xPos = xPos
        self.yPos = yPos
    def setDronePos(self, xChange, yChange):
        self.xPos+=xChange
        self.yPos+=yChange





def getTestLidarData(shape, location, initialAngle): #get all 360 degrees
    if shape == "Square":
        lidarData = [] #[distance, angle]
        for i in range(initialAngle, initialAngle+360):
            angle = i*(np.pi/180) #turn angle into radians

            lidarData.append([distance(location[0], location[1], angle),angle*180/np.pi-initialAngle]) # subtract initialAngle to get relative angle in comparison to initial orientation and return in degrees
    elif shape == "Circle":
        lidarData = []
        for i in range(initialAngle, initialAngle+360):
            angle = i*(np.pi/180) #turn angle into radians
            lidarData.append([ROOM_RADIUS,angle*180/np.pi-initialAngle])
    else:
        print("Not a valid shape")
        exit()
    return lidarData





##### new approach, scan on takeoff and get distances then 
##### create photopoints at beginning of phototaking
##### this means takeoff script only has to get up to height

# Once reached height: 
#   - take lidar data
#   - take photoDensity argument
#   - create points photoDensity meters apart, in x and y direction
#   - initial point is takeoff location
#   - create array by going in cardinal directions by photodensity meters and verifying they are in the distance
#   - repeat this for new locations until there are no new ones



def distance(x,y,angle):
    cos_angle, sin_angle = math.cos(angle), math.sin(angle)
    if cos_angle == 0:
        return y if sin_angle < 0 else ROOM_Y - y
    if sin_angle == 0:
        return x if cos_angle < 0 else ROOM_X - x
    distance_EW = (ROOM_X-x)/cos_angle if cos_angle>0 else -x/cos_angle
    distance_NS = (ROOM_Y-y)/sin_angle if sin_angle>0 else -y/sin_angle
    return min(distance_EW, distance_NS)




def inLidarRange(point, lidarData):
    distance = -1
    if point[0] == 0:
        if point[1] > 0:
            angle = 90
        else:
            angle = 270
    else:
        angle = math.degrees(math.atan(point[1]/point[0]))
    if point[0]<0:
        angle = angle+180

    for i in lidarData:
        if round(i[1]) in [round(angle), round(angle)+360]: # can be negataive
            distance = i[0]
            break
    if math.sqrt(point[0]**2 + point[1]**2) <= distance: #0.01 for rounding error in lidardata as for very edge cases when rounding the angle it can be less than the actual angle but with real data dont need to round so this is a non-issue
        return True
    else:
        return False



def addPoints(point, pointsList, visited, lidarData, photoDensity):
    flag = True
    j = 0
    while j<len(pointsList):
        flag = False
        point = pointsList[j]
        visited.append(point)
        for i in [math.radians(-90), math.radians(0), math.radians(90), math.radians(180)]: # four cardinal directions


            tmpPoint = [round(point[0] + photoDensity * math.cos(i), 3), round(point[1] + photoDensity * math.sin(i), 3)] # increases or decreases first and second points one at a time
            
            
            testBool = not(tmpPoint in visited or not inLidarRange(tmpPoint, lidarData))
            
            if not(tmpPoint in pointsList or not inLidarRange(tmpPoint, lidarData)):
                pointsList.append(tmpPoint)
        if visited == pointsList:
            flag == False
        
        j+=1
    return pointsList




def makePhotoPoints(drone, photoDensity, shape):
    lidarData = getTestLidarData(shape, [drone.xPos, drone.yPos], INITIAL_ORIENTATION)
    photoPoints = addPoints([0,0], [[0,0]], [], lidarData, photoDensity)
    return photoPoints



def run():
    drone = Drone(INITIAL_LOCATION[0], INITIAL_LOCATION[1])

    
    #relativeWallAngle = droneToWall(drone)
    #print(drone.xPos, " ", drone.yPos)
    #droneToCorner(drone, relativeWallAngle)
    #print(drone.xPos, " ", drone.yPos)
    # print(inLidarRange([5,1], getTestLidarData([drone.xPos, drone.yPos], INITIAL_ORIENTATION)))
    photoDensity = float(input("PhotoDensity>"))
    shape = input("Shape>")
    photoPoints = makePhotoPoints(drone, photoDensity, shape)
    photoPoints.sort()
    print(photoPoints, "FINAL PHOTOPOINTS")
    print(len(photoPoints))

    lidarData = getTestLidarData(shape, [drone.xPos, drone.yPos], INITIAL_ORIENTATION)

    fig, ax = plt.subplots()

    xs = [i[0] for i in photoPoints]
    ys = [i[1] for i in photoPoints]
    ax.scatter(xs, ys, s=1, c="red")
    ax.scatter(0, 0, c = "blue")
    
    lidarxs = [i[0] * math.cos(math.radians(i[1])) for i in lidarData]
    lidarys = [i[0] * math.sin(math.radians(i[1])) for i in lidarData]

    
    ax.scatter(lidarxs, lidarys, c="green", s=0.5)

    print(min(xs))
    ax.set(xlim = (min(lidarxs)-1, max(lidarxs)+1), xticks=np.arange(1, 8), ylim = (min(lidarys)-1, max(lidarys)+1), yticks=np.arange(1, 8))
    plt.grid(False)
    plt.show()






if __name__ == "__main__":
    run()