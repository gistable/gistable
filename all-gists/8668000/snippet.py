import cv2
import numpy as np


def in_front_of_both_cameras(first_points, second_points, rot, trans):
    # check if the point correspondences are in front of both images
    rot_inv = rot
    for first, second in zip(first_points, second_points):
        first_z = np.dot(rot[0, :] - second[0]*rot[2, :], trans) / np.dot(rot[0, :] - second[0]*rot[2, :], second)
        first_3d_point = np.array([first[0] * first_z, second[0] * first_z, first_z])
        second_3d_point = np.dot(rot.T, first_3d_point) - np.dot(rot.T, trans)

        if first_3d_point[2] < 0 or second_3d_point[2] < 0:
            return False

    return True

# load the corresponding images
first_img = cv2.imread("first.jpg")
second_img = cv2.imread("second.jpg")

# camera parameters
d = np.array([-0.03432, 0.05332, -0.00347, 0.00106, 0.00000, 0.0, 0.0, 0.0]).reshape(1, 8) # distortion coefficients
K = np.array([1189.46, 0.0, 805.49, 0.0, 1191.78, 597.44, 0.0, 0.0, 1.0]).reshape(3, 3) # Camera matrix
K_inv = np.linalg.inv(K)

# undistort the images first
first_rect = cv2.undistort(first_img, K, d)
second_rect = cv2.undistort(second_img, K, d)

# extract key points and descriptors from both images
detector = cv2.SURF(250)
first_key_points, first_descriptors = detector.detectAndCompute(first_rect, None)
second_key_points, second_descriptos = detector.detectAndCompute(second_rect, None)

# match descriptors
matcher = cv2.BFMatcher(cv2.NORM_L1, True)
matches = matcher.match(first_descriptors, second_descriptos)

# generate lists of point correspondences
first_match_points = np.zeros((len(matches), 2), dtype=np.float32)
second_match_points = np.zeros_like(first_match_points)
for i in range(len(matches)):
    first_match_points[i] = first_key_points[matches[i].queryIdx].pt
    second_match_points[i] = second_key_points[matches[i].trainIdx].pt

# estimate fundamental matrix
F, mask = cv2.findFundamentalMat(first_match_points, second_match_points, cv2.FM_RANSAC, 0.1, 0.99)

# decompose into the essential matrix
E = K.T.dot(F).dot(K)

# decompose essential matrix into R, t (See Hartley and Zisserman 9.13)
U, S, Vt = np.linalg.svd(E)
W = np.array([0.0, -1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]).reshape(3, 3)

# iterate over all point correspondences used in the estimation of the fundamental matrix
first_inliers = []
second_inliers = []
for i in range(len(mask)):
    if mask[i]:
        # normalize and homogenize the image coordinates
        first_inliers.append(K_inv.dot([first_match_points[i][0], first_match_points[i][1], 1.0]))
        second_inliers.append(K_inv.dot([second_match_points[i][0], second_match_points[i][1], 1.0]))

# Determine the correct choice of second camera matrix
# only in one of the four configurations will all the points be in front of both cameras
# First choice: R = U * Wt * Vt, T = +u_3 (See Hartley Zisserman 9.19)
R = U.dot(W).dot(Vt)
T = U[:, 2]
if not in_front_of_both_cameras(first_inliers, second_inliers, R, T):

    # Second choice: R = U * W * Vt, T = -u_3
    T = - U[:, 2]
    if not in_front_of_both_cameras(first_inliers, second_inliers, R, T):

        # Third choice: R = U * Wt * Vt, T = u_3
        R = U.dot(W.T).dot(Vt)
        T = U[:, 2]

        if not in_front_of_both_cameras(first_inliers, second_inliers, R, T):

            # Fourth choice: R = U * Wt * Vt, T = -u_3
            T = - U[:, 2]

#perform the rectification
R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(K, d, K, d, first_img.shape[:2], R, T, alpha=1.0)
mapx1, mapy1 = cv2.initUndistortRectifyMap(K, d, R1, K, first_img.shape[:2], cv2.CV_32F)
mapx2, mapy2 = cv2.initUndistortRectifyMap(K, d, R2, K, second_img.shape[:2], cv2.CV_32F)
img_rect1 = cv2.remap(first_img, mapx1, mapy1, cv2.INTER_LINEAR)
img_rect2 = cv2.remap(second_img, mapx2, mapy2, cv2.INTER_LINEAR)

# draw the images side by side
total_size = (max(img_rect1.shape[0], img_rect2.shape[0]), img_rect1.shape[1] + img_rect2.shape[1], 3)
img = np.zeros(total_size, dtype=np.uint8)
img[:img_rect1.shape[0], :img_rect1.shape[1]] = img_rect1
img[:img_rect2.shape[0], img_rect1.shape[1]:] = img_rect2

# draw horizontal lines every 25 px accross the side by side image
for i in range(20, img.shape[0], 25):
    cv2.line(img, (0, i), (img.shape[1], i), (255, 0, 0))

cv2.imshow('rectified', img)
cv2.waitKey(0)