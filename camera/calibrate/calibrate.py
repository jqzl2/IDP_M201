# # Import required modules
# import cv2
# import numpy as np
# import os
# import glob


# # Define the dimensions of checkerboard
# CHECKERBOARD = (5, 7)


# # stop the iteration when specified
# # accuracy, epsilon, is reached or
# # specified number of iterations are completed.
# criteria = (cv2.TERM_CRITERIA_EPS +
# 			cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)


# # Vector for 3D points
# threedpoints = []

# # Vector for 2D points
# twodpoints = []


# # 3D points real world coordinates
# objectp3d = np.zeros((1, CHECKERBOARD[0]
# 					* CHECKERBOARD[1],
# 					3), np.float32)
# objectp3d[0, :, :2] = np.mgrid[0:CHECKERBOARD[0],
# 							0:CHECKERBOARD[1]].T.reshape(-1, 2)
# prev_img_shape = None


# # Extracting path of individual image stored
# # in a given directory. Since no path is
# # specified, it will take current directory
# # jpg files alone
# images = glob.glob('C:/Users/LUJQZ/OneDrive - University of Cambridge/Engineering Tripos/Part IB/2CW/IDP_M201/camera/calibrate/*.jpg')

# for filename in images:
# 	image = cv2.imread(filename)
# 	grayColor = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 	# Find the chess board corners
# 	# If desired number of corners are
# 	# found in the image then ret = true
# 	ret, corners = cv2.findChessboardCorners(
# 					grayColor, CHECKERBOARD,
# 					cv2.CALIB_CB_ADAPTIVE_THRESH
# 					+ cv2.CALIB_CB_FAST_CHECK +
# 					cv2.CALIB_CB_NORMALIZE_IMAGE)

# 	# If desired number of corners can be detected then,
# 	# refine the pixel coordinates and display
# 	# them on the images of checker board
# 	if ret == True:
# 		threedpoints.append(objectp3d)

# 		# Refining pixel coordinates
# 		# for given 2d points.
# 		corners2 = cv2.cornerSubPix(
# 			grayColor, corners, (11, 11), (-1, -1), criteria)

# 		twodpoints.append(corners2)

# 		# Draw and display the corners
# 		image = cv2.drawChessboardCorners(image,
# 										CHECKERBOARD,
# 										corners2, ret)

# 	cv2.imshow('img', image)
# 	cv2.waitKey(0)

# 	cv2.destroyAllWindows()

# 	h, w = image.shape[:2]


# 	# Perform camera calibration by
# 	# passing the value of above found out 3D points (threedpoints)
# 	# and its corresponding pixel coordinates of the
# 	# detected corners (twodpoints)
# 	ret, matrix, distortion, r_vecs, t_vecs = cv2.calibrateCamera(
# 		threedpoints, twodpoints, grayColor.shape[::-1], None, None)


# 	# Displaying required output
# 	print(" Camera matrix:")
# 	print(matrix)

# 	print("\n Distortion coefficient:")
# 	print(distortion)

# 	print("\n Rotation Vectors:")
# 	print(r_vecs)

# 	print("\n Translation Vectors:")
# 	print(t_vecs)

import cv2
assert cv2.__version__[0] >= '3', 'The fisheye module requires opencv version >= 3.0.0'
import numpy as np
import os
import glob

CHECKERBOARD = (5,7)
subpix_criteria = (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)
calibration_flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC+cv2.fisheye.CALIB_CHECK_COND+cv2.fisheye.CALIB_FIX_SKEW
objp = np.zeros((1, CHECKERBOARD[0]*CHECKERBOARD[1], 3), np.float32)
objp[0,:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
_img_shape = None
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.
images = glob.glob('C:/Users/LUJQZ/OneDrive - University of Cambridge/Engineering Tripos/Part IB/2CW/IDP_M201/camera/calibrate/*.jpg')

for fname in images:
    img = cv2.imread(fname)
    if _img_shape == None:
        _img_shape = img.shape[:2]
    else:
        assert _img_shape == img.shape[:2], "All images must share the same size."
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_FAST_CHECK+cv2.CALIB_CB_NORMALIZE_IMAGE)
    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)
        cv2.cornerSubPix(gray,corners,(3,3),(-1,-1),subpix_criteria)
        imgpoints.append(corners)
N_OK = len(objpoints)
K = np.zeros((3, 3))
D = np.zeros((4, 1))
rvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
tvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
rms, _, _, _, _ = \
    cv2.fisheye.calibrate(
        objpoints,
        imgpoints,
        gray.shape[::-1],
        K,
        D,
        rvecs,
        tvecs,
        calibration_flags,
        (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6)
    )
print("Found " + str(N_OK) + " valid images for calibration")
print("DIM=" + str(_img_shape[::-1]))
print("K=np.array(" + str(K.tolist()) + ")")
print("D=np.array(" + str(D.tolist()) + ")")