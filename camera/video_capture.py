import cv2
import numpy as np

# Create VideoCapture object and read from camera address
cam = cv2.VideoCapture("http://localhost:8081/stream/video.mjpeg")

# Check if camera is opened successfully
if (cam.isOpened() == False):
	print("Error opening video stream")

# Read until video is completed
count = 0
while (cam.isOpened(), count <= 40):
	# Capture frame-by-frame
	count += 1
	ret, frame = cam.read()
	if ret == True:
		# Display the resulting frame
		cv2.imwrite("frame%d.jpg" % count, frame)
		cv2.imshow('Frame', frame)
		cv2.waitKey(1)

		# Press Q on keyboard to exit
		if cv2.waitKey(25) & 0xFF == ord('q'):
			break
	
	# Break the loop
	else:
		break

# When everything done, release the video capture object
cam.release()

# Close all the frames
cv2.destroyAllWindows()