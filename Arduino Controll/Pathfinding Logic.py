import random
from matplotlib import pyplot as plt

def goToPoint(robot , goal, path):
    if robot[1] != goal[1]:
        robot[1] = goal[1]
        path[0].append(robot[0])
        path[1].append(robot[1])
        return goToPoint(robot , goal , path)

    if robot[0] != goal[0]:
        robot[0] = goal[0]
        path[0].append(robot[0])
        path[1].append(robot[1])
        return goToPoint(robot , goal , path)
    
    robot[2] = goal[2]

    return path

def findPath(robot , dummie, path):

    print(dummie)

    if robot[2] != dummie[0][2]:
        if robot[2] == 0:
            goal = [230,10,1]
        else:
            goal = [10,230,0]
        return findPath(robot , dummie, goToPoint(robot, goal, path))

    path = goToPoint(robot, dummie[0], path)

    return path

def findPermuataion(dummies , goals):
    robot = [20,20,0]

    path = [[robot[0]],[robot[1]]]
    for i in range(3):
        path = findPath(robot, dummies[i], path)
        path = findPath(robot, goals[dummies[i][1]], path)

    path = findPath(robot , [[20,20,0] , 0], path)

    return path
    
        


dummies = [[[0,0,1] , 0] , [[0,0,1] , 1] , [[0,0,1] , 2]]
goals = [[[90,50,0] , 0] , [[50,90,0] , 1] , [[212,212,1] , 2]]
robot = [20,20,0]

for i in range(3):
    dummies[i][0][0] = random.randrange(1,240)
    dummies[i][0][1] = random.randrange(240 - dummies[i][0][0],240)
    dummies[i][0][-1] = 1
    print(dummies[i])
    plt.plot(dummies[i][0][0],dummies[i][0][1], 'ro')

path = [[robot[0]],[robot[1]]]
for i in range(3):
    path = findPath(robot, dummies[i], path)
    path = findPath(robot, goals[dummies[i][1]], path)

path = findPermuataion(dummies , goals)
    

plt.plot([15 , 225],[225,15])

plt.plot(path[0] , path[1])
plt.show()


print(dummies)
