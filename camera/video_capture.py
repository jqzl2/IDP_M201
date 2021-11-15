import cv2
import numpy as np
import keyboard

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
		# Display the resulting frame
		frame = undistort(frame)
		

		cv2.imshow("test",frame)
		cv2.waitKey(1)

		# Press Q on keyboard to exit
		if keyboard.is_pressed('q'):
			break
		
		# Press S to save frame
		if keyboard.is_pressed('s'):
			count += 1
			cv2.imwrite("frame%d.jpg"%count, frame)
		
	
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