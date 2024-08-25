import asyncio
from mavsdk import System
from mavsdk.offboard import (PositionNedYaw, OffboardError)
from math import (sin, cos)

SPOT_HEIGHT = 0.5 #spot is 0.5m tall when lying down

async def run():


    heightToReach = int(input("Height to reach on takeoff in meters: ")) - SPOT_HEIGHT

    
    drone = System()
    await drone.connect(system_address="udp://:14540")

    await drone.action.set_takeoff_altitude(heightToReach)

    status_text_task = asyncio.ensure_future(print_status_text(drone))

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

    print("-- Taking off")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0.0))

    print("-- Starting offboard")
    try:
        await drone.offboard.start()
    except OffboardError as error:
        print(f"Starting offboard mode failed \
                with error code: {error._result.result}")
        print("-- Disarming")
        await drone.action.disarm()
        return
  
    await drone.offboard.set_position_ned(PositionNedYaw(0,0,heightToReach,0))

    print("-- Moving to Corner of room")
    #lidar data in form [[Angle, distance], ...]

    lidarData = [[2,5], [4,4], [6,4.5]]

    closestAngle = 0
    closestDistance = 0
    async for i in range(len(lidarData)):
        if(lidarData[i][1] > closestDistance):
            closestAngle = lidarData[i][0]
            closestDistance = lidarData[i][1]
    
    closestDistance-=1 #1 meter away from wall can change
    
    north = cos(closestAngle)*closestDistance
    east = sin(closestAngle)*closestDistance

    await drone.offboard.setposition_ned(PositionNedYaw(north, east, heightToReach, closestAngle))

    print("-- Reached closest wall --")

    wallToCornerLidarData = [[2,5], [4,4], [6,4.5]] ##test data

    firstAngle = closestAngle+90
    secondAngle = closestAngle+270
    firstDistance = 0
    secondDistance = 0


    async for i in range(len(wallToCornerLidarData)):
        if wallToCornerLidarData[i][1] == firstAngle:
            firstDistance = wallToCornerLidarData[i][0]
        elif wallToCornerLidarData[i][1] == secondAngle:
            secondDistance = wallToCornerLidarData[i][0]


    if firstDistance>secondDistance:
        angle=firstAngle
        distance = firstDistance
    else:
        angle=secondAngle
        distance = secondDistance
    
    north = north + (distance*cos(angle))
    east = east + (distance*cos(angle))

    await drone.offboard.set_position_ned(PositionNedYaw(north,east,heightToReach,angle))

    print(f"-- Reached {heightToReach}m and corner, entering photoTaking mode --")

    status_text_task.cancel()


async def print_status_text(drone):
    try:
        async for status_text in drone.telemetry.status_text():
            print(f"Status: {status_text.type}: {status_text.text}")
    except asyncio.CancelledError:
        return


if __name__ == "__main__":
    # Run the asyncio loop
    asyncio.run(run())

