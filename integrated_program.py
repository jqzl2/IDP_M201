from keyboard import send
from pathfinding.pathfinding import findPath
from wifi.python_wifi import send_data


def get_movement_commands(path):
    commands =[]
    xs = path[0]
    ys = path[1]
    for i in range(len(xs) - 1):
        dx = xs[i+1] - xs[i]
        dy = ys[i+1] - ys[i]
        dr = (dx,dy)
        commands.append(dr)
    return commands

robot = [20, 10, 0]
path = findPath(robot, dummy = [[50,240,1], 0] ,  path = [[robot[0]],[robot[1]]])
movement_commands = get_movement_commands(path)
print(path)
print(movement_commands)

if movement_commands:
    send_data(movement_commands)

