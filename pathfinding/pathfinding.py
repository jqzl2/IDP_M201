import random
import math
from matplotlib import pyplot as plt
from matplotlib import animation

GoToNum = 0
TurnNum = 1
CollectDummyNum = 2
DepositDummyNum = 3
ReturnToStartNum = 4
DummyAvoidanceNum = 5
MaintainDistNum = 6

robotWidth = 15

def goToPoint(robot , goal, path):
    '''
    input:
    robot = [x1, y1, 0/1]
    goal = [x2, y2, 0/1]
    path = [[x1], [y1]]

    return:
    path = [[x path],[y path]]
    go to point directly by turning 90 degree 
    match y then match x
    '''
    # if y value doesn't match, repeat until match
    if robot[1] != goal[1]:
        robot[1] = goal[1]
        path[0].append(robot[0])
        path[1].append(robot[1])
        return goToPoint(robot , goal , path)

    # if x value doesn't match, repeat until match
    if robot[0] != goal[0]:
        robot[0] = goal[0]
        path[0].append(robot[0])
        path[1].append(robot[1])
        return goToPoint(robot , goal , path)

    robot[2] = goal[2]
    return path

def findPath(robot , goal, path):
    '''
    input:
    robot = [x1, y1, 0/1]
    goal = [x2, y2, 0/1]
    path = [[x1], [y1]]

    return:
    path = [[x path],[y path]]
    go to point considering if transition at corner needed
    '''
    # if robot and goal not on same side
    if robot[2] != goal[2]:
        if robot[2] == 0:
            transitionPoint = [235,15,1]
        else:
            transitionPoint = [5,225,0]
        return findPath(robot , goal, goToPoint(robot, transitionPoint, path))

    # left top quadrant
    if robot[2] == 1 and robot[0] < robot[1]:
        path = goToPoint(robot, [225,235,1], path)
        #path = goToPoint(robot, [goal[0],235,1], path)

    path = goToPoint(robot, goal, path)

    return path

def pathToInstructions(path, direction, instructions, dummies):
    '''
    path 
    direction = direction of robot 0/1/2/3 (90 degree)
    instructions = current instructions
    dummies = list of dummy posotions

    '''
    toPrint = ""

    front = 0
    side = 0

    goalDirect = 1
    if len(path[0]) == 1:
        return instructions
    #change in x
    if path[0][1] != path[0][0]:
        if path[0][0] < 240 - path[1][0]:
            goalDirect = 1
            front = 240-path[0][1]
            side = path[1][1]
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
     
    diff = (goalDirect - direction) % 4
    if diff == 3:
        diff = -1
    
    if diff != 0:
        toPrint = "rotate " +  str(diff * 90) + " degrees clockwise, then " + toPrint
        instructions.append(str(TurnNum) + "," + str(diff).zfill(3) + "," + str(0).zfill(3))

    goal = [path[0][len(path[0]) - 1], path[1][len(path[0]) - 1]]

    for dummy in dummies:
        if dummy[0] != goal[0] and dummy[1] != goal[1]:
            if goalDirect == 1 or goalDirect == 3:
                delta = 0
            else:
                delta = 1
            x0 = path[delta][0]
            x1 = path[delta][1]

            if x0 > x1:
                x0 , x1 = x1 , x0
            if dummy[delta] > x0 and dummy[delta] < x1:
                if abs(dummy[(delta - 1) ** 2] - path[(delta - 1) ** 2][1]) < robotWidth:
                    travelDist = abs(path[delta][0] - dummy[delta]) - 5
                    instructions.append(str(MaintainDistNum) + "," + str(travelDist).zfill(3) + "," + str(side).zfill(3))
                    goAround(instructions)

    instructions.append(str(GoToNum) + "," + str(front).zfill(3) + "," + str(side).zfill(3))

    #print(toPrint)

    instruct = pathToInstructions([path[0][1:],path[1][1:]], goalDirect, instructions, dummies) , direction

    if len(instruct) == 2:
        instruct = instruct[0]

    return instruct


def goAround(instructions):
    # turn left drive for 1s
    instructions.append(str(TurnNum) + "," + str(-1).zfill(3) + "," + str(0).zfill(3))
    instructions.append(str(DummyAvoidanceNum) + "," + str(10).zfill(3) + "," + str(0).zfill(3))

    # turn right drive for 1s
    instructions.append(str(TurnNum) + "," + str(1).zfill(3) + "," + str(0).zfill(3))
    instructions.append(str(DummyAvoidanceNum) + "," + str(20).zfill(3) + "," + str(0).zfill(3))

    # turn right drive for 1s
    instructions.append(str(TurnNum) + "," + str(1).zfill(3) + "," + str(0).zfill(3))
    instructions.append(str(DummyAvoidanceNum) + "," + str(10).zfill(3) + "," + str(0).zfill(3))

    #turn left
    instructions.append(str(TurnNum) + "," + str(-1).zfill(3) + "," + str(0).zfill(3))


def generateInstructions(robot , direction, goal, dummies):
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
    instruct = pathToInstructions(path, direction, instruct, dummies)


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

def dummySortFunct(x):
    if x[0][0] > x[0][1]:
        return x[0][1]
    return x[0][0]


def sortDummies(dummies):
    print(dummies)
    blocking = []
    dummyNo = len(dummies)
    for i in range(dummyNo):
        blocking.append([])
    blocked = False
    for i in range(dummyNo):
        count = 0
        for j in range(dummyNo):
            if i != j:
                blocked = False
                if dummies[j][0] < dummies[i][0]:
                    if abs(dummies[j][1] - dummies[i][1]) < robotWidth:
                        blocked = True

                if dummies[j][1] < dummies[i][1]:
                    if abs(dummies[j][0] - dummies[i][0]) < robotWidth:
                        blocked = True

                if dummies[j][0] > 240 - robotWidth:
                    if dummies[j][1] < dummies[i][1]:
                        blocked = True

                if dummies[j][1] > 250 - robotWidth:
                    if dummies[j][0] < dummies[i][0]:
                        blocked = True

                if blocked:
                    count += 1
        blocking[count].append(dummies[i])

    while(len(blocking[dummyNo - 1]) == 0):
        blocking.insert(0, [])


    if len(blocking[dummyNo - 1]) != 0:
        #1 blocking 2
        if len(blocking[dummyNo - 1]) == 1:
            ret = blocking[dummyNo - 1][0]

        #2 blocking 2
        elif len(blocking[dummyNo - 1]) == 2:
            if blocking[dummyNo -1][0] > blocking[dummyNo - 1][1]:
                ret = blocking[dummyNo - 1][1]
                blocking[dummyNo - 2].append(blocking[dummyNo - 1][0])
            else:
                ret = blocking[dummyNo - 1][0]
                blocking[dummyNo - 2].append(blocking[dummyNo - 1][1])

        else:
            #more please send help
            helperList = []
            herlperVar = 1000
            for i in range(len(blocking[dummyNo - 1])):
                for j in range(dummyNo):
                    if blocking[dummyNo - 1][i] != dummies[j]:
                        herlperVar = min(herlperVar , (blocking[i][0] - dummies[i][0])**2 + (blocking[i][1] - dummies[i][1])**2)

                helperList.append(herlperVar)
            
            herlperVar = 0
            for i in range(len(blocking[dummyNo - 1])):
                if helperList[i] > herlperVar:
                    herlperVar = helperList[i]
                    count = i
            
            ret = blocking[dummyNo - 1][i]
            if i > 0:
                blocking[dummyNo - 2].append(blocking[dummyNo - 1][:i])
            
            if i < len(blocking[dummyNo - 1] - 1):
                blocking[dummyNo - 2].append(blocking[dummyNo - 1][i+1:])

        rec = []

        for i in range(dummyNo - 1):
            for j in range(len(blocking[i])):
                rec.append(blocking[i][j])

        if len(rec) == 0:
            print(ret)
            print("f")
            return [ret]

        print(ret)

        ret = [ret]

        helperList =  sortDummies(rec)

        for i in range(len(helperList)):
            ret.append(helperList[i])

        return ret

    #blocking 2 contains something blocking 2 dummies etc

    #if 0 blocking 2 - fall through
    #if 1 blocking 2 pick up 1
    #if 2 blocking 2 pick up one that occurs latest in the path, go around other
    #if 3 blocking 2 not possible because 3 dummies are right next to each other

    #if 0 blocking 1 - fall through

    #if 3 blocking 1 - sort by distance from wall
    #if 2 blocking 1 - recurse
    #if 1 blocking 1 - collect

    #if blocking 0 sort and collect


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



SDummies  = sortDummies([[230 , 150 , 1],[150,230 , 1],[150,150 , 1]])
I = generateInstructions([10,15,0] , 1 , SDummies[0], SDummies)
print(SDummies)
print(I)
# step 1 sort dummies
#sort dummies into buckets, in terms of how many dummies they block
#sort bucket in terms of distance from walls
#if collisions occur go round one with lowest y