from camera.video_capture import findDummies, start_video
from pathfinding.pathfinding import findPath, pathToInstructions
from wifi.python_wifi import send_data
import numpy as np

# ip = input("Input Arduino IP address")

robot = [20, 10, 0]
path = findPath(robot, dummy = [[50,240,1], 0] ,  path = [[robot[0]],[robot[1]]])
instructions = pathToInstructions(path, 1, [])

def get_dummy_positions(r):
    dummy1_xs = []
    dummy1_ys = []
    dummy2_xs = []
    dummy2_ys = []
    dummy3_xs = []
    dummy3_ys = []

    for frame in r:
        dummy1 = frame[0]
        dummy2 = frame[1]
        dummy1_xs.append(dummy1[0])
        dummy1_ys.append(dummy1[1])
        dummy2_xs.append(dummy2[0])
        dummy2_ys.append(dummy2[1])
        
        if len(frame) == 3:
            dummy3 = frame[2]
            dummy3_xs.append(dummy3[0])
            dummy3_ys.append(dummy3[1])
        
    dummy1_xs = np.array(dummy1_xs)
    dummy1_ys = np.array(dummy1_ys)
    dummy2_xs = np.array(dummy2_xs)
    dummy2_ys = np.array(dummy2_ys)
    dummy3_xs = np.array(dummy3_xs)
    dummy3_ys = np.array(dummy3_ys)

    dummy1 = (np.average(dummy1_xs), np.average(dummy1_ys))
    dummy2 = (np.average(dummy2_xs), np.average(dummy2_ys))
    dummy3 = (np.average(dummy3_xs), np.average(dummy3_ys))
    
    return dummy1, dummy2, dummy3

r = start_video(findDummies)
p = get_dummy_positions(r)









