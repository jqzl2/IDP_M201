import cv2
import numpy as np
import keyboard

from video_capture import isolateCenter
from numpy.core.numeric import Infinity

DIM=(1016, 760)
K=np.array([[617.0246864588934, 0.0, 498.84953870958276], [0.0, 620.5390466649645, 395.6528980159782], [0.0, 0.0, 1.0]])
D=np.array([[0.15842294486041952], [-0.8060115044560319], [1.463190158015197], [-0.9325973032567597]])

def ContSortFunct(contour):
	area = cv2.contourArea(contour)

	perim = cv2.arcLength(contour,True)
	if contour[0][0][0] > contour[0][0][1] or (contour[0][0][0] < 75 and contour[0][0][1] > 575):
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

	cv2.drawContours(imgB , contours[:3] , -1 , (0,255,75) , 2)
	
	for i in range(4):
	 	M = cv2.moments(contours[i])
	 	if M['m00'] != 0.0:
			 x_centre = int(M['m10']/M['m00'])
			 y_centre = int(M['m01']/M['m00'])
			 centre = (x_centre, y_centre)
			 img = cv2.circle(img, centre, radius=5, color=(0, 0, 255), thickness=-1)

	cv2.imshow("trest",img)
	cv2.waitKey(1)
	# print(centre)
	

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