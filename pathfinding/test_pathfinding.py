from pathfinding import goToPoint#, findPath, pathToInstructions
from modified_pathfinding import findPath, pathToInstructions, generateInstructions

print("goToPoint gives: " + str(goToPoint([10,15,0],[20,40,0],[[10],[15]])))
#print("findPath gives:" + str(findPath([10,15,0],[20,40,1],[[10],[15]])))
path = findPath([10,15,0],[10,200,1], [[10],[15]])
print(path)
print(pathToInstructions(path, 0, []))

print(generateInstructions([10,15,0] , 1 , [10,200,1]))
