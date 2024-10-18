import asyncio
import math
from mavsdk import System
from mavsdk.offboard import (PositionNedYaw, OffboardError)
from tests import getTestLidarData
import cv2 as cv
import matplotlib.pyplot as plt

camera = cv.VideoCapture(0)




TEST_INITIAL_LOCATION = [5, 6] # x,y
TEST_INITIAL_ORIENTATION = 0 #angle


async def inLidarRange(point, lidarData):
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
    if math.sqrt(point[0]**2 + point[1]**2) <= distance+0.3: #0.01 for rounding error in lidardata as for very edge cases when rounding the angle it can be less than the actual angle but with real data dont need to round so this is a non-issue
        return True
    else:
        return False


async def addPoints(point, pointsList, visited, testLidarData, photoDensity):
    j = 0
    while j<len(pointsList):
        point = pointsList[j]
        visited.append(point)
        for i in [math.radians(-90), math.radians(0), math.radians(90), math.radians(180)]: # four cardinal directions


            tmpPoint = [round(point[0] + photoDensity * math.cos(i), 3), round(point[1] + photoDensity * math.sin(i), 3)] # increases or decreases first and second points one at a time
            
            
            testBool = not(tmpPoint in visited or not inLidarRange(tmpPoint, testLidarData))
            
            if not(tmpPoint in pointsList or not inLidarRange(tmpPoint, testLidarData)):
                pointsList.append(tmpPoint)
        j+=1
    return pointsList


async def makePhotoPoints(photoDensity):
    testLidarData = getTestLidarData(TEST_INITIAL_LOCATION, TEST_INITIAL_ORIENTATION)
    photoPoints = addPoints([0,0], [[0,0]], [], testLidarData, photoDensity)
    return photoPoints





async def run(photoDensity):
    drone = System()
    await drone.connect(system_address="udp://:14540")

    

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            break

    print("-- Arming")
    await drone.action.arm()

    print("-- Setting initial setpoint")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0.0))

    print("-- Creating Photo Points")

    photoPoints = await makePhotoPoints(photoDensity)

    async for i in photoPoints:
        for angle in [0, 90, 180, 270]:
            await drone.offboard.set_position_ned(PositionNedYaw(photoPoints[i][1], photoPoints[i][0], 0, angle))
            result,image = await cv.cam.read()
            if result:
                cv.imwrite(f"pictures/{i[0]}{i[1]}{angle}.png", image)
            else:
                exit("Could not take photo")

    







if __name__ == "__main__":
    # Run the asyncio loop
    photoDensity = float(input("Photo Density> "))
    asyncio.run(run(photoDensity))



