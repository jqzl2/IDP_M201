import cv2
import numpy as np
import keyboard
import glob

from camera.video_capture import isolateCenter
from numpy.core.numeric import Infinity

DIM=(1016, 760)
K=np.array([[617.0246864588934, 0.0, 498.84953870958276], [0.0, 620.5390466649645, 395.6528980159782], [0.0, 0.0, 1.0]])
D=np.array([[0.15842294486041952], [-0.8060115044560319], [1.463190158015197], [-0.9325973032567597]])

# def isInAllQuater(contour):
# 	#print(contour)
# 	Quarter = 0
# 	Truth = [False, False, False, False]

# 	for i in range(4):
# 		if contour[i][0][0] > 508:
# 			Quarter = 2
# 		else:
# 			Quarter = 0
		
# 		if contour[i][0][1] > 380:
# 			Quarter += 1
# 		Truth[Quarter] = True

# 	print(Truth)

# 	return True

def testingFunct(img):
	img = isolateCenter(img)
	imgEdge = img.copy()
	imgEdge[:,:,0] = 0
	imgEdge[:,:,2] = 0
	imgEdge = cv2.cvtColor(imgEdge,cv2.COLOR_BGR2GRAY)
	imgEdge = cv2.GaussianBlur(img,(3,3),0)
	imgEdge = cv2.Canny(image=imgEdge,threshold1=0, threshold2=255)

	contours, heirachy = cv2.findContours(imgEdge,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)

	img = cv2.drawContours(img, contours,-1, (0,255,175),2)

	for i in range(len(contours)):
		if contours[i][0][0][1] > contours[i][0][0][0]:
			(x,y) , r = cv2.minEnclosingCircle(contours[i])
			center = (int(x),int(y))

			perim = cv2.arcLength(contours[i],True)

			radius = int((perim)/r)

			cv2.circle(img,center,radius,(255,0,0),2)
		#cv2.circle(img,center,perim,(0,0,255),1)

	cv2.imshow("test",img)

def findContors(img):
	#img = undistort(img)
	img = isolateCenter(img)

	imgB = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

	imgBlur = cv2.GaussianBlur(imgB , (3,3) , 0)

	imgEdge = cv2.Canny(image = imgBlur, threshold1=0, threshold2=255)

	contours, heirachy = cv2.findContours(imgEdge,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
	
	polyContours = []

	blueGoal = [Infinity,0]
	redGoal = [Infinity,0]
	whiteGoal = [Infinity,0]

	max = 0
	cont = []

	for i in range(len(contours)):
		if heirachy[0][i][2] > max:
			max = heirachy[0][i][2]
			
		if heirachy[0][i][2] < 0:
			polyContours.append(contours[i])

	for i in range(len(polyContours)):
	 	M = cv2.moments(polyContours[i])
	 	if M['m00'] != 0.0:
			 x = M['m10'] / M['m00']
			 y = M['m01'] / M['m00']

			 if (430 - x)**2 + (120 - y)**2 < blueGoal[0]:
				 blueGoal[0] = (430 - x)**2 + (120 - y)**2
				 blueGoal[1] = polyContours[i]
				
			 if (550 - x)**2 + (235 - y)**2 < redGoal[0]:
				 redGoal[0] = (550 - x)**2 + (235 - y)**2
				 redGoal[1] = polyContours[i]
			
			 if (615 - x)**2 + (53 - y)**2 < whiteGoal[0]:
				 whiteGoal[0] = (615 - x)**2 + (53 - y)**2
				 whiteGoal[1] = polyContours[i]


	cv2.circle(img, (430,120), 5, (255,0,0), -1)
	cv2.circle(img, (550,235), 5, (0,0,255), -1)
	cv2.circle(img, (615,53), 5, (255,255,255), -1)

	cv2.drawContours(img, blueGoal[1], -1, (0,0,0), 2)
	cv2.drawContours(img, redGoal[1], -1, (0,0,0), 2)
	cv2.drawContours(img, whiteGoal[1], -1, (0,0,0), 2)

	cv2.imshow("trest",img)


# images = glob.glob('D:/George/Documents/GitHub/IDP_M201/camera/calibrate/*.jpg')

# for frame in images:
#     testingFunct(cv2.imread(frame))
#     cv2.waitKey(0)


# Create VideoCapture object and read from camera address
cam = cv2.VideoCapture("http://localhost:8081/stream/video.mjpeg")

# Check if camera is opened successfully
if (cam.isOpened() == False):
	print("Error opening video stream")

count = 0
# Read until video is completed
while cam.isOpened():
	# Capture frame-by-frame
	ret, frame = cam.read()
	if ret == True:

		ret = findContors(frame)
		cv2.waitKey(1)

		#Display the resulting frame
		#cv2.imshow("undistorted",undistort(frame))
		# Press Q on keyboard to exit
		
		if keyboard.is_pressed('q'):
			break
		
		# Press S to save frame
		if keyboard.is_pressed('s'):
			count += 1
			cv2.imwrite("frame%d.jpg" % count, frame)
	
	# Break the loop
	else:
		print("Failed to read camera") 
		break

# When everything done, release the video capture object
cam.release()

# Close all the frames
cv2.destroyAllWindows()

'References: https://www.geeksforgeeks.org/camera-calibration-with-python-opencv/' 
'https://medium.com/@kennethjiang/calibrate-fisheye-lens-using-opencv-333b05afa0b0'