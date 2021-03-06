import random
from matplotlib import pyplot as plt
from matplotlib import animation
from pathfinding import goToPoint

GoToNum = 0
TurnNum = 1
CollectDummyNum = 2
DepositDummyNum = 3
ReturnToStartNum = 4

# goTo method for region B
def goToPoint(robot, goal, path):
    '''
    input:
    robot = [x1, y1, 0/1]
    goal = [x2, y2, 0/1]
    path = [[x1], [y1]]

    return:
    path = [[x path],[y path]]
    go to point directly by turning 90 degree 
    match y then match x for some cases
    match x then match y for other cases
    '''
    # assume wall on the right
    # if goal in right top quadrant, match y then x
    if (goal[2] == 1 and goal[0] >= goal[1]) or (goal[2] == 0 and goal[0] <= goal[1]):
        # repeat until y matched
        if robot[1] != goal[1]:
            robot[1] = goal[1]
            path[0].append(robot[0])
            path[1].append(robot[1])
            return goToPoint(robot , goal , path)
        # repeat until x matched
        if robot[0] != goal[0]:
            robot[0] = goal[0]
            path[0].append(robot[0])
            path[1].append(robot[1])
            return goToPoint(robot , goal , path)

    # if goal in left top quadrant, match x then y
    elif goal[2] == 1 and goal[0] < goal[1] or (goal[2] == 0 and goal[0] > goal[1]):
        # repeat until x matched
        if robot[0] != goal[0]:
            robot[0] = goal[0]
            path[0].append(robot[0])
            path[1].append(robot[1])
            return goToPoint(robot , goal , path)
        # repeat until y matched
        if robot[1] != goal[1]:
            robot[1] = goal[1]
            path[0].append(robot[0])
            path[1].append(robot[1])
            return goToPoint(robot , goal , path)

    robot[2] = goal[2]
    return path

def findPath(robot, goal, path, obstacle = []):
    '''
    input:
    robot = [x1, y1, 0/1]
    goal = [[dummy1],[dummy2],[dummy3]]
    obstacle = []
    path = [[x1], [y1]]

    return:
    path = [[x path],[y path]]
    
    considers: turning at corner to go over 0-1, dummies obstructing
    '''
    # define region A and region B and region C
    regionA = [240-43, 240-43, 1]
    regionB = [240, 240, 1]
    regionC = []

    # if robot and goal not on same side, goToCorner added to path and findPath again
    if robot[2] != goal[2]:
        if robot[2] == 0:
            transitionPoint = [235,15,1]
        else:
            transitionPoint = [5,225,0]
        path = goToPoint(robot, transitionPoint, path)
        robot = transitionPoint

    # if goal in left top quadrant
    if robot[2] == 1 and goal[0] < goal[1]:
        transitionPoint = [235,235,1]
        path = goToPoint(robot, transitionPoint, path)
        robot = transitionPoint
        #path = findPath(robot , goal, path)
        #path = goToPoint(robot, [goal[0],235,1], path)

    path = goToPoint(robot, goal, path)

    return path

def pathToInstructions(path, direction, instructions):
    '''
    path 
    direction = direction of robot 0/1/2/3 (90 degree)
    instructions = current instructions
    '''
    toPrint = ""

    front = 0
    side = 0

    goalDirect = 1
    if len(path[0]) == 1:
        return instructions
    # change in x
    if path[0][1] != path[0][0]:
        if path[0][0] < 240 - path[1][0]:
            front = 240-path[0][1]
            side = path[1][1]
            goalDirect = 1
        else:
            front = path[0][1]
            side = 240 - path[1][1]
            goalDirect = 3
   
    else:
        if path[0][0] < 240 - path[1][0]:
            goalDirect = 2
            front = path[1][1]
            side = path[0][1]
        else:
            goalDirect = 0
            front = 240 - path[1][1]
            side = 240 - path[0][1]

    toPrint = "go to " + str(front) + " from the front and " + str(side) + " from the side"
     
    diff = (goalDirect - direction)
    if diff == 3:
        diff = -1
    
    if diff != 0:
        toPrint = "rotate " +  str(diff * 90) + " degrees clockwise, then " + toPrint
        instructions.append(str(TurnNum) + "," + str(diff).zfill(3) + "," + str(0).zfill(3))

    instructions.append(str(GoToNum) + "," + str(front).zfill(3) + "," + str(side).zfill(3))

    #print(toPrint)

    instruct = pathToInstructions([path[0][1:],path[1][1:]], goalDirect, instructions) , direction


    if len(instruct) == 2:
        instruct = instruct[0]

    return instruct

def generateInstructions(robot , direction, goal):
    instruct = []
    dummy = True
    returnToStart = False

    ##this is currently where the goal positions are stored

    # [home, white, red, blue]
    dummyGoals = [[24,24,0], [215,215,1], [50,90,0], [90,50,0]]

    if type(goal) == int:
        #this is a dummy goal
        if goal == 0:
            returnToStart = True

        goal = dummyGoals[goal]
        dummy = False

    path = findPath(robot , goal, [[robot[0]],[robot[1]]])
    instruct = pathToInstructions(path, direction, instruct)


    for struct in instruct:
        data = str(struct).split(',')
        if data[0] == str(TurnNum):
            direction += int(data[1])

    finalInstruct = ""

    if dummy:
        finalInstruct = str(CollectDummyNum) + "," + str(240 - goal[1]).zfill(3) + ",000"
    else:
        if returnToStart:
            finalInstruct = str(ReturnToStartNum) + ",000,000"
        else:
            finalInstruct = str(DepositDummyNum) + "," + str(goal[1]).zfill(3) + ",000"

    instruct[len(instruct) -1] = finalInstruct

    return instruct , robot, direction % 4



# instruct , robot, direction = generateInstructions([10,10,0] , 1 , [100,220,1])
# print(instruct)
# instruct , robot, direction = generateInstructions(robot , direction , 2)
# print(instruct)

# instruct , robot, direction = generateInstructions(robot , direction , [150,175,1])
# print(instruct)
# instruct , robot, direction = generateInstructions(robot , direction , 3)
# print(instruct)

# instruct , robot, direction = generateInstructions(robot , direction , [200,100,1])
# print(instruct)
# instruct , robot, direction = generateInstructions(robot , direction , 1)
# print(instruct)

# instruct , robot, direction = generateInstructions(robot , direction , 0)
# print(instruct)


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


    for i in range(1):
        path = [[robot[0]],[robot[1]]]
        path = findPath(robot, dummies[i], path)
        path = findPath(robot, goals[dummies[i][1]], path)
        plt.plot(path[0] , path[1])

    path = [[robot[0]],[robot[1]]]
    path = findPath(robot, [[20,20,0] , 0], path)
    plt.plot(path[0],path[1])

    robot = [20,20,0]

    path = [[robot[0]], [robot[1]]]

    for i in range(1):
        path = findPath(robot, dummies[i], path)
        path = findPath(robot, goals[dummies[i][1]], path)
        

    path = findPath(robot , [[20,20,0], 0], path)

    instructions = []

    pathToInstructions(path, 1, instructions)

    print(instructions)





    plt.plot([15 , 225],[225,15])

    plt.xlim(0,240)
    plt.ylim(0,240)
    plt.gca().set_aspect("equal", "box")
