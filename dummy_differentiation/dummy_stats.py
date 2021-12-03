#importing required libaries
import math
import numpy as np


#the dbscan code is used like a libary , and can be found at https://github.com/choffstein/dbscan/blob/master/dbscan/dbscan.py
# A Density-Based Algorithm for Discovering Clusters in Large Spatial Databases with Noise
# Martin Ester, Hans-Peter Kriegel, Jörg Sander, Xiaowei Xu
# dbscan: density based spatial clustering of applications with noise

UNCLASSIFIED = False
NOISE = None

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
        
#finds the positions of the dummies given a large amount of potential points
def avg_dummy_positions(p):
    #setting up storage lists
    dummy_xs = []
    dummy_ys = []
    metaDummies = []

    #extracting the points from the p and frame lists
    for frame in p:
        for i in range(len(frame)):
            dummy_xs.append(frame[i][0])
            dummy_ys.append(frame[i][1])

    #making a matrix out of the dummy positions, for passing into dbscan
    m = np.matrix([dummy_xs , dummy_ys])

    #sorts the dummies into groups which are seperated by no more than 15 pixels (approx 5cm)
    clusterIds = dbscan(m, 15, 0)

    #for every potential dummy
    for i in range(len(dummy_xs)):
        #assuming that dbscan has assigned the dummy a bucket
        if clusterIds[i] != None:   
            #if the bucket of this dummy has not yet been created create it and all lesser buckets
            while len(metaDummies) < clusterIds[i]:
                metaDummies.append([[],[]])

            #add a modified x and y position to the correct buckets list. The modification converts the point from image space to table space
            metaDummies[clusterIds[i]-1][0].append(240 - (dummy_xs[i] * (240 / (((201 - 878)**2 + (735 - 705)**2)**0.5))))
            metaDummies[clusterIds[i]-1][1].append(dummy_ys[i] * (240 / (((201 - 178)**2 + (735 - 76)**2)**0.5)))

    #sort the list by the number of potential dummies in the bucket. More potential dummies means more chance of being a dummy
    metaDummies.sort(key = lambda x: len(x[0]), reverse=True)

    #returns the avarge x and y position for the 3 most likley dummies
    dummy1 = [sum(metaDummies[0][0]) / len(metaDummies[0][0]) , sum(metaDummies[0][1]) / len(metaDummies[0][1])]
    dummy2 = [sum(metaDummies[1][0]) / len(metaDummies[1][0]) , sum(metaDummies[1][1]) / len(metaDummies[1][1])]
    dummy3 = [sum(metaDummies[2][0]) / len(metaDummies[2][0]) , sum(metaDummies[2][1]) / len(metaDummies[2][1])]
    
    #in testing these values are correct to within 2cm
    return dummy1, dummy2, dummy3
