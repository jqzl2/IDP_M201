#importing required libaries
import keyboard
from camera.video_capture import findDummies, start_video
from pathfinding.pathfinding import findPath, generateInstructions, sortDummies
from dummy_differentiation.dummy_stats import avg_dummy_positions
from wifi.server import set_up_server, receive_dummy_mode, send_commands

#main robot controll code
def run():
    #setting up the connection with the arduino
    conn = set_up_server()
    #setting up the intial robot data
    robot = [20, 10, 0]
    direction = 1

    #get the dummies from 50 frames of video
    p = start_video(findDummies)

    #find the dummies given those frames
    dummy1, dummy2, dummy3 = avg_dummy_positions(p)
    dummies = [dummy1, dummy2, dummy3]

    #sort the dummies into their collection order
    dummies = sortDummies(dummies)
    instructString = ""
    count = len(dummies)

    #for the dummies in the first pass
    for i in range(count):
        #get the instructions to collect that dummy
        #dummies[i:] is used to make the robot not avoid dummies that its put in goals
        instructions, robot, direction = generateInstructions(robot, direction, dummies[i], dummies[i:])
        #converts the instructions into a correct format string
        for struct in instructions:
            instructString+=struct + "."
        instructString = "hi!" + instructString + "!$"

        #send the instructions to the robot and wait for the dummy mode to be returned
        send_commands(instructString, conn)
        mode = receive_dummy_mode(conn)

        #if its mode 1 the dummy will be collected last so leave it there
        if mode != 1:
            #otherwise get the instructions to deliver the dummy
            instructions, robot, direction = generateInstructions(robot , direction , mode , dummies[i:])
            #converts intstructions into a correct format string
            for struct in instructions:
                instructString+=struct + "."
        else:
            #add the dummy to be colected in the second pass
            dummies.append(dummies[i])

    #if the mode 1 dummy was found
    if len(dummies) != count:
        #get the instructions to collect that dummy
        instructions, robot, direction = generateInstructions(robot, direction, dummies[count], [])
        #converts the instructions into a correct format string
        for struct in instructions:
            instructString+=struct + "."
        instructString = "hi!" + instructString + "!$"

        #send the instructions to the robot and wait for the dummy mode to be returned
        send_commands(instructString, conn)
        mode = receive_dummy_mode(conn)

        #get the instructions to deliver the dummy
        instructString = ""
        instructions, robot, direction = generateInstructions(robot , direction , 1 , [])
         #converts intstructions into a correct format string
        for struct in instructions:
            instructString+=struct + "."

    #get the instructions to return home
    instructions, robot, direction = generateInstructions(robot , direction , 0 , [])
    #converts intstructions into a correct format string
    for struct in instructions:
        instructString+=struct + "."
    instructString = "hi!" + instructString + "!$"
    #send the final instructions and stop the python program
    send_commands(instructString, conn)
    
#run the controll code
if __name__ == "__main__":
    print("*** WacMan Program ***")
    run()