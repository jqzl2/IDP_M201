import random
from matplotlib import pyplot as plt

dummies = [[[0,0,1] , 1] , [[[0,0,1] , 2]] , [[0,0,1] , 3]]
goals = [[(90,50,0) , 1] , [[(50,90,0) , 2]] , [[(212,212,0) , 3]]]

for i in range(3):
    dummies[i][0][0] = random.randrange(1,240)
    dummies[i][0][1] = random.randrange(240 - dummies[i][0][0],240)
    plt.plot(dummies[i][0][0],dummies[i][0][1], 'ro')

plt.show()


print(dummies)
