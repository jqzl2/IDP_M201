import random
from matplotlib import pyplot as plt
from matplotlib import animation

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

def findPath(robot , dummy, path):
    if robot[2] != dummy[0][2]:
        if robot[2] == 0:
            goal = [230,10,1]
        else:
            goal = [10,230,0]
        return findPath(robot , dummy, goToPoint(robot, goal, path))

    if robot[2] == 1 and robot[0] < robot[1]:
        path = goToPoint(robot, [230,230,1], path)
        path = goToPoint(robot, [dummy[0][0],230,1], path)

    path = goToPoint(robot, dummy[0], path)

    return path

def dummySortFunct(x):
    if x[0][0] > x[0][1]:
        return x[0][1]
    return x[0][0]

def animate(i):
    dummies = [[[0,0,1] , 0] , [[0,0,1] , 1] , [[0,0,1] , 2]]
    goals = [[[90,50,0] , 0] , [[50,90,0] , 1] , [[212,212,1] , 2]]
    robot = [20,20,0]

    plt.gcf().clear()

    for i in range(3):
        dummies[i][0][0] = random.randrange(1,240)
        dummies[i][0][1] = random.randrange(240 - dummies[i][0][0],240)
        dummies[i][0][-1] = 1
        plt.plot(dummies[i][0][0],dummies[i][0][1], 'ro')

    dummies.sort(key = lambda x: dummySortFunct(x))


    for i in range(3):
        path = [[robot[0]],[robot[1]]]
        path = findPath(robot, dummies[i], path)
        path = findPath(robot, goals[dummies[i][1]], path)
        plt.plot(path[0] , path[1])

    path = [[robot[0]],[robot[1]]]
    path = findPath(robot, [[20,20,0] , 0], path)
    plt.plot(path[0],path[1])


    plt.plot([15 , 225],[225,15])

    plt.xlim(0,240)
    plt.ylim(0,240)
    plt.gca().set_aspect("equal", "box")

# ax = plt.gcf()

# ani = animation.FuncAnimation(plt.gcf() , animate, interval = 500)

# plt.show()
