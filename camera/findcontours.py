import cv2
import numpy as np
import keyboard

from video_capture import isolateCenter, findContours

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

		frame = findContours(frame)
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