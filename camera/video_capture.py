import cv2
import numpy as np

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
		cv2.imshow('Frame', frame)
		cv2.waitKey(1)

		# Press Q on keyboard to exit
		if cv2.waitKey(25) & 0xFF == ord('q'):
			break
		
		if cv2.waitKey(25) & 0xFF == ord('s'):
			cv2.imwrite("frame%d.jpg" % count, frame)
	
	# Break the loop
	else:
		print("Failed to read camera")
		break

# When everything done, release the video capture object
cam.release()

# Close all the frames
cv2.destroyAllWindows()