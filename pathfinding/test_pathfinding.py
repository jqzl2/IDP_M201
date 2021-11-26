from pathfinding import goToPoint, findPath, pathToInstructions

print(goToPoint([10,15,0],[20,40,0],[[10],[15]]))
print(findPath([10,15,0],[20,40,1],[[10],[15]]))
path = findPath([10,15,0],[20,40,1],[[10],[15]])
print(pathToInstructions(path, 0, []))
