from keyboard import send
from camera.video_capture import findDummies, start_video
from pathfinding.pathfinding import findPath, pathToInstructions
from wifi.python_wifi import send_data
import numpy as np
import math

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

def test_dbscan():
    m = np.matrix('1 1.2 0.8 3.7 3.9 3.6 10; 1.1 0.8 1 4 3.9 4.1 10')
    eps = 0.5
    min_points = 2
    assert dbscan(m, eps, min_points) == [1, 1, 1, 2, 2, 2, None]

def avg_dummy_positions(p):
    dummy1_xs = []
    dummy1_ys = []
    dummy2_xs = []
    dummy2_ys = []
    dummy3_xs = []
    dummy3_ys = []

    dummy_xs = []
    dummy_ys = []

    for frame in p:
        dummy1 = frame[0]
        dummy2 = frame[1]
        dummy1_xs.append(dummy1[0])
        dummy1_ys.append(dummy1[1])
        dummy2_xs.append(dummy2[0])
        dummy2_ys.append(dummy2[1])

        dummy_xs.append(dummy1[0])
        dummy_ys.append(dummy1[1])
        dummy_xs.append(dummy2[0])
        dummy_ys.append(dummy2[1])
        
        if len(frame) == 3:
            dummy3 = frame[2]
            dummy3_xs.append(dummy3[0])
            dummy3_ys.append(dummy3[1])

            dummy_xs.append(dummy3[0])
            dummy_ys.append(dummy3[1])
        
    dummy1_xs = np.array(dummy1_xs)
    dummy1_ys = np.array(dummy1_ys)
    dummy2_xs = np.array(dummy2_xs)
    dummy2_ys = np.array(dummy2_ys)
    dummy3_xs = np.array(dummy3_xs)
    dummy3_ys = np.array(dummy3_ys)

    m = np.matrix([dummy_xs , dummy_ys])
    print(m)
    print("")
    clusterIds = dbscan(m, 5, 2)

    metaDummies = []

    for i in range(len(dummy_xs)):
        if clusterIds[i] != None:
            while len(metaDummies) < clusterIds[i]:
                metaDummies.append([[],[]])

            metaDummies[clusterIds[i]-1][0].append(dummy_xs[i])
            metaDummies[clusterIds[i]-1][1].append(dummy_ys[i])

    metaDummies.sort(key = lambda x: len(x[0]), reverse=True)

    dummy1 = [sum(metaDummies[0][0]) / len(metaDummies[0][0]) , sum(metaDummies[0][1]) / len(metaDummies[0][1])]
    dummy2 = [sum(metaDummies[1][0]) / len(metaDummies[1][0]) , sum(metaDummies[1][1]) / len(metaDummies[1][1])]
    dummy3 = [sum(metaDummies[2][0]) / len(metaDummies[2][0]) , sum(metaDummies[2][1]) / len(metaDummies[2][1])]
    
    return dummy1, dummy2, dummy3

# ip = input('Input Arduino IP address')

robot = [20, 10, 0]

p = start_video(findDummies)
dummy1, dummy2, dummy3 = avg_dummy_positions(p)

print(dummy1 , dummy2, dummy3)


# path = findPath(robot, dummy = [[dummy1[0], dummy1[1], 0], 0], path = [[robot[0]],[robot[1]]])
# instructions = pathToInstructions(path, 1, [])
# r = send_data(ip, instructions)
# print(instructions)







