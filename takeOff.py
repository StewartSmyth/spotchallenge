import asyncio
from mavsdk import System
from mavsdk.offboard import (PositionNedYaw, OffboardError)
from math import (sin, cos)

SPOT_HEIGHT = 0.191 #spot is 0.5m tall when lying down
DISTANCE_FROM_ROOF = 0.5



async def run(heightToReach):

    
    drone = System()

    await drone.connect(system_address="udp://:14540")

    await drone.action.set_takeoff_altitude(heightToReach)


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


if __name__ == "__main__":
    location = input("Inside or Outside> ")
    height = -1
    if location == "Inside":
        height = float(input("Height of room in meters> ")) - DISTANCE_FROM_ROOF
    elif location == "Outside":
        height = float(input("At what height in meters> "))
    else:
        print("Not valid exiting ...")
        exit()
    # Run the asyncio loop
    asyncio.run(run(height))

