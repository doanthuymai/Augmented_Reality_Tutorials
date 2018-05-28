# *****************************************************************************
# * Filename : sift_lk_realtime_marker.py
# * Date : 27/May/2018
# * Author : Ram
# * Email : ramkalath@gmail.com
# * Breif Description : realtime marker detection using sift and lk
# * Detailed Description :
# *****************************************************************************

import cv2
import numpy as np
import sys
import time
import match_and_display as md


# params for ShiTomasi corner detection
feature_params = dict(maxCorners = 100,
                      qualityLevel = 0.3,
                      minDistance = 7,
                      blockSize = 7)

# Parameters for lucas kanade optical flow
lk_params = dict(winSize  = (15,15),
                 maxLevel = 2,
                 criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

if __name__ == "__main__":
    # print "keep the marker picture still in front of the camera for a short while"
    img_path = sys.argv
    marker_img = cv2.imread(img_path[1])
    # marker_img = cv2.imread("marker_image.jpg")
    gray_marker_img = cv2.cvtColor(marker_img, cv2.COLOR_BGR2GRAY)
    print "place the marker in front of the camera"

    time.sleep(5)

    cap = cv2.VideoCapture(0)
    flag, old = cap.read()
    old = cv2.imread("./first_frame.jpg")
    gray_old = cv2.cvtColor(old, cv2.COLOR_BGR2GRAY)
    print "images captured"

    sift = cv2.SIFT()
    kp_marker, des_marker = sift.detectAndCompute(gray_marker_img, None)
    kp_old, des_old = sift.detectAndCompute(gray_old, None)
    print "sift computed"

    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)

    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des_marker, des_old, k=2)

    good = []
    for m, n in matches:    
        if m.distance < 0.7*n.distance:
            good.append(m)
    
    if len(good) > 10:
        print "number of good points = ", len(good)
        src_pts = np.float32([kp_marker[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp_old[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        print "matching points found"

        # md.match_and_display(src_pts, dst_pts, marker_img, old)
        h, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

    else:
        print "could not find a matching marker"
        exit()
        
    p0 = cv2.goodFeaturesToTrack(gray_old, mask=None, **feature_params)

    check = True

    print "entering loop"

    points_on_marker_image = np.array([[0, 0, 1], [300, 0, 1], [300, 475, 1], [0, 475, 1]])

    first = cv2.imread("./first_frame.jpg")
    gray_first = cv2.cvtColor(first, cv2.COLOR_BGR2GRAY)

    p1 = cv2.goodFeaturesToTrack(gray_first, mask=None, **feature_params)

    second = cv2.imread("./second_frame.jpg")
    gray_second = cv2.cvtColor(first, cv2.COLOR_BGR2GRAY)

    p2, st, err = cv2.calcOpticalFlowPyrLK(gray_first, gray_second, p1, None, **lk_params)

    h_new, mask = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
    h = np.dot(h, h_new)
    points_on_webcam_image = np.dot(h, points_on_marker_image.T).T
    points_on_marker_image = np.array([[[0, 0]], [[300, 0]], [[300, 475]], [[0, 475]]])
    points_on_webcam_image = np.array([[[points_on_webcam_image[0][0]/points_on_webcam_image[0][2], points_on_webcam_image[0][1]/points_on_webcam_image[0][2]]], [[points_on_webcam_image[1][0]/points_on_webcam_image[1][2], points_on_webcam_image[1][1]/points_on_webcam_image[1][2]]], [[points_on_webcam_image[2][0]/points_on_webcam_image[2][2], points_on_webcam_image[2][1]/points_on_webcam_image[2][2]]], [[points_on_webcam_image[3][0]/points_on_webcam_image[3][2], points_on_webcam_image[3][1]/points_on_webcam_image[3][2]]]])
    md.match_and_display(points_on_marker_image, points_on_webcam_image, marker_img, second)
    # while 1:
        # _, new = cap.read()
        # new = cv2.imread("marker_first_frame.jpg")
        # gray_new = cv2.cvtColor(new, cv2.COLOR_BGR2GRAY)

        # p1, st, err = cv2.calcOpticalFlowPyrLK(gray_old, gray_new, p0, None, **lk_params)
        # good_new = p1[st==1]
        # good_old = p0[st==1]

        # h_new, mask = cv2.findHomography(good_new, good_old, cv2.RANSAC, 5.0)
        # # if(check):
            # # h_old = h * h_new
            # # check=False
        # # else:
            # # h_old=h_old*h_new

        # # h_old = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
        # print "points_on_marker_image\n", points_on_marker_image
        # points_on_webcam_image = np.dot(h_old, points_on_marker_image.T).T
        # print "points_on_webcam_image\n", points_on_webcam_image
        # cv2.imwrite("webcam_image.jpg", new)
        # break

        # gray_old = gray_new.copy()
        # p0 = good_new.reshape(-1,1,2)

        # cv2.imshow("cap", new)
        # key = cv2.waitKey(10)
        # if(key == 27):
            # break

cv2.destroyAllWindows()
cap.release()
