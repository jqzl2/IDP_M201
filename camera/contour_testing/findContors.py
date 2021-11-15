import cv2
import numpy as np
import keyboard
import glob

from numpy.core.numeric import Infinity

DIM=(1016, 760)
K=np.array([[617.0246864588934, 0.0, 498.84953870958276], [0.0, 620.5390466649645, 395.6528980159782], [0.0, 0.0, 1.0]])
D=np.array([[0.15842294486041952], [-0.8060115044560319], [1.463190158015197], [-0.9325973032567597]])

def undistort(img):
	h,w = img.shape[:2]

	diml = img.shape[:2][::-1]

	assert diml[0] / diml[1] == DIM[0] / DIM[1]

	dim2 = diml
	
	dim3 = diml

	scaled_K = K * diml[0] / DIM[0]
	scaled_K[2][2] = 1.0

	balance = 0.0

	new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(scaled_K, D, dim2, np.eye(3), balance=balance)
	map1, map2 = cv2.fisheye.initUndistortRectifyMap(scaled_K, D, np.eye(3), new_K, dim3, cv2.CV_16SC2)
	undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

	return undistorted_img

def isolateCenter(img):
	img = undistort(img)

	box = np.array([
            [[201,735]],
            [[178,76]],
            [[813,36]],
            [[878,705]]
        ])

	src_pts = box.astype("float32")

	width = (int)(((201-878)**2 + (735-705)**2)**0.5)
	height = (int)(((201-178)**2 + (735-76)**2)**0.5)

	dst_pts = np.array([[0, height-1],
                        [0, 0],
                        [width-1, 0],
                        [width-1, height-1]], dtype="float32")

	M = cv2.getPerspectiveTransform(src_pts, dst_pts)
	warped = cv2.warpPerspective(img, M, (width, height))

	return(warped)


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

	 		#img = cv2.circle(img, (int(M['m10']/M['m00']),int(M['m01']/M['m00'])), radius=5, color=(0, 0, 255), thickness=-1)

	cv2.circle(img, (430,120), 5, (255,0,0), -1)
	cv2.circle(img, (550,235), 5, (0,0,255), -1)
	cv2.circle(img, (615,53), 5, (255,255,255), -1)

	cv2.drawContours(img, blueGoal[1], -1, (255,0,0), 2)
	cv2.drawContours(img, redGoal[1], -1, (0,0,255), 2)
	cv2.drawContours(img, whiteGoal[1], -1, (255,255,255), 2)

	cv2.imshow("trest",img)




	#cv2.imshow("contour",cv2.drawContours(img, polyContours, -1 , (0,255,75), 2))
	

images = glob.glob('D:/George/Documents/GitHub/IDP_M201/camera/calibrate/*.jpg')

for frame in images:
    findContors(cv2.imread(frame))
    cv2.waitKey(0)


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