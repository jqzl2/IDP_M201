#importing required libaries
import cv2
import numpy as np
import keyboard
import time
from numpy.core.numeric import Infinity

#distortion magic numbers calculated using the chessboard method
DIM=(1016, 760)
K=np.array([[617.0246864588934, 0.0, 498.84953870958276], [0.0, 620.5390466649645, 395.6528980159782], [0.0, 0.0, 1.0]])
D=np.array([[0.15842294486041952], [-0.8060115044560319], [1.463190158015197], [-0.9325973032567597]])

#takes in an image from the camera and returns and image the same size but undistorted
def undistort(img):

	#dimensions of the origional shape
	diml = img.shape[:2][::-1]

	#ensure that the input image is the correct size, used to detect changes in camera
	assert diml[0] / diml[1] == DIM[0] / DIM[1]

	#adjusts the K calculated from the chessboard into one that takes into acount the new dimensions
	scaled_K = K * diml[0] / DIM[0]
	scaled_K[2][2] = 1.0

	#gets a new K that corrects the entire image
	new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(scaled_K, D, diml, np.eye(3), balance=0.0)

	#undistorts the entire image
	map1, map2 = cv2.fisheye.initUndistortRectifyMap(scaled_K, D, np.eye(3), new_K, diml, cv2.CV_16SC2)
	undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

	#returns the undistorted image
	return undistorted_img

#generic function that returns 50 frames from the camera passed through some function F
def start_video(f):
	# Create VideoCapture object and read from camera address
	cam = cv2.VideoCapture("http://localhost:8081/stream/video.mjpeg")

	# Check if camera is opened successfully
	if (cam.isOpened() == False):
		print("Error opening video stream")

	count = 0
	data_mat = []
	# Read until video is completed
	while cam.isOpened() and len(data_mat) < 50:
		# Capture frame-by-frame
		ret, frame = cam.read()
		if ret == True:
			# Display the resulting frame
			frame , data= f(frame)
			data_mat.append(data)
			cv2.imshow("test",frame)
			cv2.waitKey(1)
		# Break the loop
		else:
			print("Failed to read camera") 
			break

	# When everything done, release the video capture object
	cam.release()

	# Close all the frames
	cv2.destroyAllWindows()
	return data_mat

#takes a distorted image and returns an undistorted image of the table only
def isolateCenter(img):
	#undistort the raw image
	img = undistort(img)

	#"magic number" points that are the 4 corners of the table for this specific camera
	box = np.array([
            [[201,735]],
            [[178,76]],
            [[813,36]],
            [[878,705]]
        ])
	
	#casting the box into a form that is easier for cv2 to work with but harder for humans
	src_pts = box.astype("float32")

	#calculating the height and width of the table in the picture space
	width = (int)(((201-878)**2 + (735-705)**2)**0.5)
	height = (int)(((201-178)**2 + (735-76)**2)**0.5)

	#creates a new point array which is a rectangle with the same height and width of the table in image space
	#this is used to map the rotated and translated table to a rectangle centered on the origin
	dst_pts = np.array([[0, height-1],
                        [0, 0],
                        [width-1, 0],
                        [width-1, height-1]], dtype="float32")

	#gets the matrix that maps the image space co-ordinates to the new centered rectangle ones
	M = cv2.getPerspectiveTransform(src_pts, dst_pts)

	#warps the image by the matrix M, and then only takes the table from it as there is some unwanted image around it
	warped = cv2.warpPerspective(img, M, (width, height))
	return warped

#finds the contours that represent the return locations, mostly used to familiarise with open cv
def findGoals(img):
	#isolates the table in place
	img = isolateCenter(img)

	#converts the image into a greyscale image. This is needed for the contour and edge detection algorithms
	imgB = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

	#apply a gaussian blur to make the edge detection more useful, so it doesnt pick up small scrathes etc
	imgBlur = cv2.GaussianBlur(imgB , (3,3) , 0)

	#canny edge detection is used to find the contours, as findcontours alone struggles
	imgEdge = cv2.Canny(image = imgBlur, threshold1=0, threshold2=255)

	#this finds the countours of the edges, effectivally just grouping the edges that touch together
	contours, heirachy = cv2.findContours(imgEdge,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
	
	#used to store polygons that could be the goals
	polyContours = []

	#array used to more easily keep track of which contour is a goal
	blueGoal = [Infinity,0]
	redGoal = [Infinity,0]
	whiteGoal = [Infinity,0]

	#for every contour
	for i in range(len(contours)):
		#heirachy[0][i][2] = -1 if the contour contains no contours, like the goals should
		if heirachy[0][i][2] < 0:
			#add this contour to the list of potential goals
			polyContours.append(contours[i])

	#for every potential goal
	for i in range(len(polyContours)):
		#returns the moments of area of the contour
	 	M = cv2.moments(polyContours[i])

		#if the contour has a real area, used to remove point contotous
	 	if M['m00'] != 0.0:
			 #finds the x and y location of the centroid
			 x = M['m10'] / M['m00']
			 y = M['m01'] / M['m00']

			#code below is same logic for all 3 goals
			#if the center of the contour is closest to the found center of the goal, set it as the goal
			 if (430 - x)**2 + (120 - y)**2 < blueGoal[0]:
				 blueGoal[0] = (430 - x)**2 + (120 - y)**2
				 blueGoal[1] = polyContours[i]
				
			 if (550 - x)**2 + (235 - y)**2 < redGoal[0]:
				 redGoal[0] = (550 - x)**2 + (235 - y)**2
				 redGoal[1] = polyContours[i]
			
			 if (615 - x)**2 + (53 - y)**2 < whiteGoal[0]:
				 whiteGoal[0] = (615 - x)**2 + (53 - y)**2
				 whiteGoal[1] = polyContours[i]

	#draw circles in the found centers of the goals
	cv2.circle(img, (430,120), 5, (255,0,0), -1)
	cv2.circle(img, (550,235), 5, (0,0,255), -1)
	cv2.circle(img, (615,53), 5, (255,255,255), -1)

	#draw the goal contours
	cv2.drawContours(img, blueGoal[1], -1, (0,0,0), 2)
	cv2.drawContours(img, redGoal[1], -1, (0,0,0), 2)
	cv2.drawContours(img, whiteGoal[1], -1, (0,0,0), 2)

	#return the image for display
	return img

#this is used as a sorting function to find dummies, the lower the value the more dummy like it is
def ContSortFunct(contour):
	#area and M are used to evaluate the dummieness
	area = cv2.contourArea(contour)
	M = cv2.moments(contour)
	
	#if the contour has no area it cannot be a dummy
	if M['m00'] != 0.0:
		#x and y co-oridantes of the centroid of the contour
		x_center = int(M['m10'] / M['m00'])
		y_center = int(M['m01'] / M['m00'])
		#if the contour is in the top right conrner goal box then assume its not a dummy
		if x_center > y_center or (x_center < 75 and y_center > 575):
			return Infinity
		#otherwise the dummies should have very small areas so the area is a good sorting function
		return area
	return Infinity


#takes a distorted image and returns the locations of the 6 most likley dummies
def findDummies(img):
	#isolate the table in place
	img = isolateCenter(img)
	#used to allow for the output to be graphed on a undistorted image
	imgB = img.copy()

	#sets up the contrast boosting factors
	contrast = 64 * 4
	f = 131*(contrast + 127)/(127*(131-contrast))

	#isolate the green channel, as the dummies are green
	imgB[:,:,0] = 0
	imgB[:,:,2] = 0

	#this has the effect of boosting the contrast of the image by contrasrt times (64 * 4)
	#this is done in order to change the image into one which is effectively just the dramatic changes in green levels
	#in effect this makes it only show the dummies and white lines
	imgB = cv2.addWeighted(imgB, f, imgB, 0, 127 * (1-f))

	#the edge detection and contour functions require greyscale images
	imgB = cv2.cvtColor(imgB,cv2.COLOR_BGR2GRAY)


	#applies gaussian blure to remove small artifacts
	imgBlur = imgB
	imgBlur = cv2.GaussianBlur(imgB , (7,7) , 0)

	#edge detection is used to find boundaries then contour detection is used to group edges
	imgEdge = cv2.Canny(image = imgBlur, threshold1=0, threshold2=255)
	contours, heirachy = cv2.findContours(imgEdge,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)

	#sorts the contours by their dummyness
	contours = list(contours)
	contours.sort(key = lambda x: ContSortFunct(x))
	
	#return list
	centres = []

	#for the 6 most dummy contours, 6 is used to try to garuntee that each dummy has at least 1 contour
	for i in range(6):
		#calculates the moments to find the centers
	 	M = cv2.moments(contours[i])
		#final catch to avoid dividing by 0
	 	if M['m00'] != 0.0:
			 #calcualating the x and y centroid co-ordinates
			 x_centre = int(M['m10']/M['m00'])
			 y_centre = int(M['m01']/M['m00'])

			 #create the center array, then draw it on the image for real time human error catching
			 centre = (x_centre, y_centre)
			 img = cv2.circle(img, centre, radius=5, color=(0, 0, 255), thickness=-1)
			 centres.append(centre)

	#returns the image with dummies located and their centers
	return img, centres

'References: https://www.geeksforgeeks.org/camera-calibration-with-python-opencv/' 
'https://medium.com/@kennethjiang/calibrate-fisheye-lens-using-opencv-333b05afa0b0'