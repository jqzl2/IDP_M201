import keyboard
from camera.video_capture import findDummies, start_video
from pathfinding.pathfinding import findPath, generateInstructions, sortDummies
import numpy as np
import math
from wifi.server import set_up_server, receive_dummy_mode, send_commands


# -*- coding: utf-8 -*-

# A Density-Based Algorithm for Discovering Clusters in Large Spatial Databases with Noise
# Martin Ester, Hans-Peter Kriegel, Jörg Sander, Xiaowei Xu
# dbscan: density based spatial clustering of applications with noise

UNCLASSIFIED = False
NOISE = None

def _dist(p,q):
	return math.sqrt(np.power(p-q,2).sum())

def _eps_neighborhood(p,q,eps):
	return _dist(p,q) < eps

def _region_query(m, point_id, eps):
    n_points = m.shape[1]
    seeds = []
    for i in range(0, n_points):
        if _eps_neighborhood(m[:,point_id], m[:,i], eps):
            seeds.append(i)
    return seeds

def _expand_cluster(m, classifications, point_id, cluster_id, eps, min_points):
    seeds = _region_query(m, point_id, eps)
    if len(seeds) < min_points:
        classifications[point_id] = NOISE
        return False
    else:
        classifications[point_id] = cluster_id
        for seed_id in seeds:
            classifications[seed_id] = cluster_id
            
        while len(seeds) > 0:
            current_point = seeds[0]
            results = _region_query(m, current_point, eps)
            if len(results) >= min_points:
                for i in range(0, len(results)):
                    result_point = results[i]
                    if classifications[result_point] == UNCLASSIFIED or \
                       classifications[result_point] == NOISE:
                        if classifications[result_point] == UNCLASSIFIED:
                            seeds.append(result_point)
                        classifications[result_point] = cluster_id
            seeds = seeds[1:]
        return True
        
def dbscan(m, eps, min_points):
    """Implementation of Density Based Spatial Clustering of Applications with Noise
    See https://en.wikipedia.org/wiki/DBSCAN
    
    scikit-learn probably has a better implementation
    
    Uses Euclidean Distance as the measure
    
    Inputs:
    m - A matrix whose columns are feature vectors
    eps - Maximum distance two points can be to be regionally related
    min_points - The minimum number of points to make a cluster
    
    Outputs:
    An array with either a cluster id number or dbscan.NOISE (None) for each
    column vector in m.
    """
    cluster_id = 1
    n_points = m.shape[1]
    classifications = [UNCLASSIFIED] * n_points
    for point_id in range(0, n_points):
        point = m[:,point_id]
        if classifications[point_id] == UNCLASSIFIED:
            if _expand_cluster(m, classifications, point_id, cluster_id, eps, min_points):
                cluster_id = cluster_id + 1
    return classifications

def avg_dummy_positions(p):

    dummy_xs = []
    dummy_ys = []

    for frame in p:
        # dummy1 = frame[0]
        # dummy2 = frame[1]

        # dummy_xs.append(dummy1[0])
        # dummy_ys.append(dummy1[1])
        # dummy_xs.append(dummy2[0])
        # dummy_ys.append(dummy2[1])

        for i in range(len(frame)):
            dummy_xs.append(frame[i][0])
            dummy_ys.append(frame[i][1])
        
        # if len(frame) == 3:
        #     dummy3 = frame[2]
        #     dummy_xs.append(dummy3[0])
        #     dummy_ys.append(dummy3[1])

    m = np.matrix([dummy_xs , dummy_ys])
    print(m)
    print("")
    clusterIds = dbscan(m, 15, 0)

    metaDummies = []

    for i in range(len(dummy_xs)):
        if clusterIds[i] != None:
            while len(metaDummies) < clusterIds[i]:
                metaDummies.append([[],[]])

            metaDummies[clusterIds[i]-1][0].append(240 - (dummy_xs[i] * (240 / (((201 - 878)**2 + (735 - 705)**2)**0.5))))
            metaDummies[clusterIds[i]-1][1].append(dummy_ys[i] * (240 / (((201 - 178)**2 + (735 - 76)**2)**0.5)))

    metaDummies.sort(key = lambda x: len(x[0]), reverse=True)

    dummy1 = [sum(metaDummies[0][0]) / len(metaDummies[0][0]) , sum(metaDummies[0][1]) / len(metaDummies[0][1])]
    dummy2 = [sum(metaDummies[1][0]) / len(metaDummies[1][0]) , sum(metaDummies[1][1]) / len(metaDummies[1][1])]
    dummy3 = [sum(metaDummies[2][0]) / len(metaDummies[2][0]) , sum(metaDummies[2][1]) / len(metaDummies[2][1])]
    
    return dummy1, dummy2, dummy3

def run():
    conn = set_up_server()
    robot = [20, 10, 0]
    direction = 1
    p = start_video(findDummies)
    dummy1, dummy2, dummy3 = avg_dummy_positions(p)
    dummies = [dummy1, dummy2, dummy3]

    print(dummies)

    dummies = [[50,200,1]]

    # dummies = [[50,200,1]]

    dummies = [[50,200,1]]
    dummies = sortDummies(dummies)
    instructString = ""
    count = len(dummies)

    for i in range(count):
        instructions, robot, direction = generateInstructions(robot, direction, dummies[i], dummies[i:])
        for struct in instructions:
            instructString+=struct + "."

        #string get sent
        #mode is recived

    #     for struct in instructions:
    #         instructString+=struct + "."
    while True:
        if keyboard.is_pressed('s'):
            # instructString = "!" + instructString + "!"
            instructString = "hi!0,005,015.1,001,000.!$"
            mode = receive_dummy_mode(conn)
            send_commands(instructString, conn)

    #     if mode != 1:#
    #         instructions, robot, direction = generateInstructions(robot , direction , mode , dummies[i:])
    #         for struct in instructions:
    #             instructString+=struct + "."
    #     else:
    #         dummies.append(dummies[i])

    # if len(dummies) != count:
    #     instructions, robot, direction = generateInstructions(robot, direction, dummies[count], [])
    #     for struct in instructions:
    #         instructString+=struct + "."

    #     mode = receive_dummy_mode(conn)
    #     send_commands(instructString, conn)

    #     instructString = ""

    #     instructions, robot, direction = generateInstructions(robot , direction , 1 , [])
    #     for struct in instructions:
    #         instructString+=struct + "."

    # instructions, robot, direction = generateInstructions(robot , direction , 0 , [])
    # for struct in instructions:
    #     instructString+=struct + "."

    #     mode = receive_dummy_mode(conn)
    #     send_commands(instructString, conn)



if __name__ == "__main__":
    print("*** WacMan Program ***")
    run()










