import cv2
import numpy as np
import keyboard
import glob
import math

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

def isolateCenter(img, distorted = True):
	if distorted == True:
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

def ContSortFunct(contour):
	area = cv2.contourArea(contour)

	perim = cv2.arcLength(contour,True)
	if contour[0][0][0] > contour[0][0][1] or area == 0 or perim == 0:
		return Infinity
	return area


def findDummies(img):
	imgB = img.copy()
	contrast = 64 * 4
	f = 131*(contrast + 127)/(127*(131-contrast))

	imgB[:,:,0] = 0
	imgB[:,:,2] = 0

	imgB = cv2.addWeighted(imgB, f, imgB, 0, 127 * (1-f))


	imgB = cv2.cvtColor(imgB,cv2.COLOR_BGR2GRAY)



	imgBlur = imgB
	imgBlur = cv2.GaussianBlur(imgB , (7,7) , 0)


	imgEdge = cv2.Canny(image = imgBlur, threshold1=0, threshold2=255)

	contours, heirachy = cv2.findContours(imgEdge,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)

	contours = list(contours)
	contours.sort(key = lambda x: ContSortFunct(x))

	imgB = cv2.cvtColor(imgB , cv2.COLOR_GRAY2BGR)

	cv2.drawContours(imgB , contours[:5] , -1 , (0,255,75) , 2)

	cv2.imshow("trest",imgB)
	

# images = glob.glob('D:/George/Documents/GitHub/IDP_M201/camera/contour_testing/*.jpg')

# for frame in images:
# 	 findDummies(isolateCenter(cv2.imread(frame),False))
# 	 cv2.waitKey(0)


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

		ret = findDummies(isolateCenter(frame))
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