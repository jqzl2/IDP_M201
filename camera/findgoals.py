import cv2
import numpy as np
import keyboard
import glob

from video_capture import findContours

DIM=(1016, 760)
K=np.array([[617.0246864588934, 0.0, 498.84953870958276], [0.0, 620.5390466649645, 395.6528980159782], [0.0, 0.0, 1.0]])
D=np.array([[0.15842294486041952], [-0.8060115044560319], [1.463190158015197], [-0.9325973032567597]])

# images = glob.glob('D:/George/Documents/GitHub/IDP_M201/camera/contour_testing/*.jpg')

# for frame in images:
#     findContours(cv2.imread(frame))
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