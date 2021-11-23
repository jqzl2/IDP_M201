from keyboard import send
from camera.video_capture import findDummies, start_video
from pathfinding.pathfinding import findPath, generateInstructions
import numpy as np
import urllib3

def avg_dummy_positions(p):
    dummy1_xs = []
    dummy1_ys = []
    dummy2_xs = []
    dummy2_ys = []
    dummy3_xs = []
    dummy3_ys = []

    for frame in p:
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

robot = [20, 10, 0]
direction =1

# p = start_video(findDummies)
# print(p)
# dummy1, dummy2, dummy3 = avg_dummy_positions(p)
# path = findPath(robot, dummy = [[dummy1[0], dummy1[1], 0], 0], path = [[robot[0]],[robot[1]]])
instructions, robot, direction = generateInstructions(robot, direction, [100,220,1])
print(instructions)


arduino1 = urllib3.PoolManager()
arduino1.request('GET', 'http://192.168.137.14/?lol=' + instructions[0] + '.' + instructions[1])







