#setting up constants for instruction generation
GoToNum = 0
TurnNum = 1
CollectDummyNum = 2
DepositDummyNum = 3
ReturnToStartNum = 4
DummyAvoidanceNum = 5
MaintainDistNum = 5
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
    # if y value doesn't match, repeat until it matches
    if robot[1] != goal[1]:
        #if the robot is going up/down
        if robot[1] > goal[1]:
            sign = -1
        else:
            sign = 1
        #first the robot sets its new position
        robot[1] = goal[1]

        #the robot will go to the its x value then overshoot its y value by 20
        #this is done to acount for the change in y due to rotation
        path[0].append(robot[0])
        path[1].append(robot[1] + (sign * 20))
        #the robot then rotates
        path[0].append(robot[0] + (sign * 10))
        path[1].append(robot[1])
        #call the function again
        return goToPoint(robot , goal , path)

    # if x value doesn't match, repeat until it matches
    if robot[0] != goal[0]:
        #set the new x value
        robot[0] = goal[0]
        #go to the location
        path[0].append(robot[0])
        path[1].append(robot[1])
        #call the function again
        return goToPoint(robot , goal , path)

    #ensure that the half is correct
    robot[2] = goal[2]
    #return the entire path so far
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
        #if the robot is on the lower half
        if robot[2] == 0:
            #set the transition points and errors
            transitionPoint = [238,15,1]
            xError = -20
            yError = 20
        else:
            #set the transition points and errors
            transitionPoint = [13,225,0]
            xError = 20
            yError = -20
        #go to the transition point, changing halves in the process
        path = goToPoint(robot, transitionPoint, path)
        #account for the robot turning
        robot[0] += xError
        robot[1] += yError
        path[0].append(robot[0])
        path[1].append(robot[1])
        #find the path from this point to the goal
        return findPath(robot , goal, path)

    #if the dummy is very close to the right wall then go to an intermediate point that has the same
    #x but a lesser y
    if goal[2] == 1 and goal[0] > 240 - (2*robotWidth):
        path = goToPoint(robot , [goal[0] , 80, 1] , path)

    #go to the dummy
    path = goToPoint(robot, goal, path)

    #return the entire path
    return path

def pathToInstructions(path, direction, instructions, dummies):
    '''
    path 
    direction = direction of robot 0/1/2/3 (90 degree)
    instructions = current instructions
    dummies = list of dummy posotions

    '''

    #setting up vairables
    front = 0
    side = 0
    goalDirect = 1

    #if the path is done then return the instructions
    if len(path[0]) == 1:
        return instructions

    #change in x
    if path[0][1] != path[0][0]:
        #if there is a change in x and y then there has been a rotation and this point should be ignored
        if path[1][0] != path[1][1]:
            #call the function again
            instruct = pathToInstructions([path[0][1:],path[1][1:]], direction, instructions, dummies) , direction
            #used to cure the insctruction as they need to remove the direction
            if len(instruct) == 2:
                instruct = instruct[0]
            return instruct

        #if the robot is in the bottom half
        if path[0][0] < 240 - path[1][0]:
            #go to the right
            goalDirect = 1
            front = 240-path[0][1]
            side = path[1][1]
        else:
            #go to the left
            front = path[0][1]
            side = 240 - path[1][1]
            goalDirect = 3
   
    else:
        #if the robot is in the bottom half
        if path[0][0] < 240 - path[1][0]:
            #go down
            goalDirect = 2
            front = path[1][1]
            side = path[0][1]
        else:
            #go up
            goalDirect = 0
            front = 240 - path[1][1]
            side = 240 - path[0][1]

    #calculates the change in direction
    diff = (goalDirect - direction) % 4
    if diff == 3:
        diff = -1

    #if there is any change in direction
    if diff != 0:
        #if this is not the first instruction
        if len(instructions) != 0:
            #if the previous instruction was a rotation
            if str(instructions[-1]).split(',')[0] == "0,":
                #change its distance from the fron by 20, the length of the robot
                temp = str(instructions[-1]).split(',')
                temp[1] = str(int(temp[1]) - 20)
                temps = ""
                for S in temp:
                    temps += S
                instructions[-1] = temps
        #append the turn instruction
        instructions.append(str(TurnNum) + "," + str(diff).zfill(3) + "," + str(0).zfill(3))

    #goal is where the robot is going eventually
    goal = [path[0][len(path[0]) - 1], path[1][len(path[0]) - 1]]


    #if the x or y is changing
    if goalDirect == 1 or goalDirect == 3:
        delta = 0
    else:
        delta = 1
    #delta is the list that contains the change, meaing x0 x1 are the changed values
    x0 = path[delta][0]
    x1 = path[delta][1]

    #ensure that x0 and x1 are ordered
    if x0 > x1:
        x0 , x1 = x1 , x0

    #for every dummy
    for dummy in dummies:
        #if the dummy is the final goal there is no need to avoid it
        if dummy[0] != goal[0] and dummy[1] != goal[1]:
            #if the dummy lies somewhere perpendicular to the path
            if dummy[delta] > x0 and dummy[delta] < x1:
                #if the dummy lies very close to the path
                if abs(dummy[(delta - 1) ** 2] - path[(delta - 1) ** 2][1]) < robotWidth:
                    #avoiding the dummy
                    #approach the dummy to be 5 cm away
                    travelDist = abs(path[delta][0] - dummy[delta]) - 5
                    instructions.append(str(DummyAvoidanceNum) + "," + str(travelDist).zfill(3) + "," + str(side).zfill(3))
                    #go around the dummy
                    goAround(instructions)

    #if the robot cannot use at least 1 set of its sensors
    if front > 100 or side > 60:
        #if the robot is too far away from the wall to wall follow
        if side > 60:
            instructions.append(str(DummyAvoidanceNum) + "," + str(x1 - x0).zfill(3) + "," + str(side).zfill(3))
        else:
            #if the robot is too far away from the front wall to stop correctly
            instructions.append(str(MaintainDistNum) + "," + str(x1 - x0).zfill(3) + "," + str(side).zfill(3))
    elif front < 150 and side < 60:
        #use the normal wall following
        instructions.append(str(GoToNum) + "," + str(front).zfill(3) + "," + str(side).zfill(3))

    #call the function again
    instruct = pathToInstructions([path[0][1:],path[1][1:]], goalDirect, instructions, dummies) , direction

    #cure the instructions
    if len(instruct) == 2:
        instruct = instruct[0]
    return instruct


def goAround(instructions):
    '''
    input:
    instructions = [instruction]

    return:
    instructions = [instruction]
    appends instructions to go around a dummy
    '''

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
    '''
    input:
    robot = [x1, y1, 0/1]
    direction = 0,1,2,3 (90 degree roations)
    goal = [x2, y2, 0/1]
    dummies = [[[dx1], [dy1] , ... , [dx3],[dy3]]]

    return:
    instructions = [instruction]
    robot = [x1, y1, 0/1]
    direction = 0,1,2,3 (90 degree roations)
    generates the instructions to get the robot from its location to its goal
    '''
    #setting up variables
    instruct = []
    dummy = True
    returnToStart = False
    finalInstruct = ""
    #this is currently where the goal positions are stored
    # [home, white, red, blue]
    dummyGoals = [[24,24,0], [215,215,1], [50,90,0], [90,50,0]]

    #if an int is passed the  the goal is a return goal
    if type(goal) == int:
        #this is a the final goal
        if goal == 0:
            returnToStart = True
        #set the goal location and type
        goal = dummyGoals[goal]
        dummy = False

    #find the path that the robot should take
    path = findPath(robot , goal, [[robot[0]],[robot[1]]])
    
    #generate the instructions for that path
    instruct = pathToInstructions(path, direction, instruct, dummies)

    #reconstruct the instructions to find the turning number
    for struct in instruct:
        data = str(struct).split(',')
        if data[0] == str(TurnNum):
            #change the direction such that its correct to the final state of the robot
            direction += int(data[1])
    
    #if the robot is collecting a dummy
    if dummy:
        #final instruction is to get very close to the dummy then collect is
        finalInstruct += str(GoToNum) + "," + str(0).zfill(3) + "," + str(240 - goal[1]).zfill(3) + "."
        finalInstruct += str(CollectDummyNum) + "," + str(240 - goal[1]).zfill(3) + ",000"
    else:
        if returnToStart:
            #final instruction is to return to the very start position
            finalInstruct = str(ReturnToStartNum) + ",000,000"
        else:
            #final instruction is to deposit a dummy in the correct goal
            finalInstruct = str(DepositDummyNum) + "," + str(goal[1]).zfill(3) + ",000"

    #cahnge the final instruction to be the correct one
    instruct[len(instruct) -1] = finalInstruct

    #return the data for the robot to continue its journey
    return instruct , robot, direction % 4

#custom sort parameter that returns (240 - the distance to the closest edge wall)
def dummySortFunct(x):
    #if the answer will be the top wall
    if x[0][0] > x[0][1]:
        #return the y
        return x[0][1]
    #return the x
    return x[0][0]


def sortDummies(dummies):
    '''
    input:
    dummies = [[[dx1], [dy1] , ... , [dx3],[dy3]]]

    return:
    dummies = [[[dx1], [dy1] , ... , [dx3],[dy3]]]
    sorts the dummies list into its collection order
    '''

    #creating the blocking buckets, the max number of dummies a dummy can block is 1- dummyNo
    blocking = []
    dummyNo = len(dummies)
    for i in range(dummyNo):
        blocking.append([])

    blocked = False
    #for every dummy
    for i in range(dummyNo):
        count = 0
        #for every other dummy
        for j in range(dummyNo):
            if i != j:
                #assume its not blocking
                blocked = False

                #the first two modes are for if the robot will collide with the dummy during the L section of its movement
                #if the other dummy has a lower x value
                if dummies[j][0] < dummies[i][0]:
                    #and their y value is close enough to colide
                    if abs(dummies[j][1] - dummies[i][1]) < robotWidth:
                        #then the dummy I is blocking the dummy j
                        blocked = True

                #if the other dummy has a lower y value
                if dummies[j][1] < dummies[i][1]: 
                    #and their x value is close enough to colide
                    if abs(dummies[j][0] - dummies[i][0]) < robotWidth:
                        blocked = True

                #the second 2 modes are for the if dummy is located in the path outside of the L section
                #if the dummy is close to the right wall
                if dummies[i][0] > 240 - robotWidth:
                    #and the other dummy is above it
                    if dummies[i][1] < dummies[j][1]:
                        blocked = True
                #if the dummy is close to the top wall
                if dummies[i][1] > 240 - robotWidth:
                    #and the other dummy is to the right of it
                    if dummies[i][0] < dummies[j][0]:
                        blocked = True
                #if the other dummy is blocked then the blocked number for the dummy goes up by 1
                if blocked:
                    count += 1  
        #add the dummy to the correct bucked
        blocking[count].append(dummies[i])

    #effectivally removes the empty buckets at the top, to prevent infinate recursion if no dummies are blocking the max amount
    while(len(blocking[dummyNo - 1]) == 0):
        blocking.insert(0, [])

    #error catching for trying to access empty lists
    if len(blocking[dummyNo - 1]) != 0:
        #1 blocking 2
        if len(blocking[dummyNo - 1]) == 1:
            #return the most blocking dummy
            ret = blocking[dummyNo - 1][0]

        #2 blocking 2
        elif len(blocking[dummyNo - 1]) == 2:
            #the robot doesnt want to go round a dummy while transporting one so priority is given to the lates dummy in this case
            #if the first dummy is earlier in the path than the second one
            if blocking[dummyNo -1][0] > blocking[dummyNo - 1][1]:
                #return the second dummy
                ret = blocking[dummyNo - 1][1]
                blocking[dummyNo - 2].append(blocking[dummyNo - 1][0])
            else:
                #return the first dummy
                ret = blocking[dummyNo - 1][0]
                blocking[dummyNo - 2].append(blocking[dummyNo - 1][1])

        else:
            #if there is no heirachy of blocking
            #helperList contains the distances between the dummies
            helperList = []
            #for every dummy
            for i in range(len(blocking[dummyNo - 1])):
                #this is an arbitarly large number so that min can be used
                helperVar = 100000
                #for every other dummy
                for j in range(dummyNo):
                    if blocking[dummyNo - 1][i] != dummies[j]:
                        #helperVar will always be the distance to the closest dummy
                        helperVar = min(helperVar , (blocking[i][0] - dummies[i][0])**2 + (blocking[i][1] - dummies[i][1])**2)
                helperList.append(helperVar)
            
            #this finds the most isolated dummy
            helperVar = 0
            for i in range(len(blocking[dummyNo - 1])):
                if helperList[i] > helperVar:
                    helperVar = helperList[i]
                    count = i
            
            #erturn the most isolated dummy
            ret = blocking[dummyNo - 1][count]
            #adds all of the dummies but the returned one to the new list
            if count > 0:
                blocking[dummyNo - 2].append(blocking[dummyNo - 1][:count])
            if count < len(blocking[dummyNo - 1] - 1):
                blocking[dummyNo - 2].append(blocking[dummyNo - 1][count+1:])

        rec = []
        #for every dummy apart from the returned one add them to the rec list
        for i in range(dummyNo - 1):
            for j in range(len(blocking[i])):
                rec.append(blocking[i][j])
        
        #if the len(rec) is 0 then the algorithm is done
        if len(rec) == 0:
            return [ret]
            
        #listify ret
        ret = [ret]

        #append the rest of the dummies to the ret list, after sorting
        helperList =  sortDummies(rec)
        for i in range(len(helperList)):
            ret.append(helperList[i])

        #return the sorted list
        return ret