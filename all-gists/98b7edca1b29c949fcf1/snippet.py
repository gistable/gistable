# -*- coding: utf-8 -*-

import argparse

import cv2
import numpy as np


def calc_disparity(left_image, right_image):
    window_size = 3
    min_disp = 1
    num_disp = 16*2
    stereo = cv2.StereoSGBM(
        minDisparity=min_disp,
        numDisparities=num_disp,
        SADWindowSize=window_size,
        uniquenessRatio=10,
        speckleWindowSize=100,
        speckleRange=32,
        disp12MaxDiff=1,
        P1=8*3*window_size**2,
        P2=32*3*window_size**2,
        fullDP=False
    )
    return stereo.compute(left_image, right_image).astype(np.float32) / 16.0


def remove_invalid(disp_arr, points, colors):
    mask = (
        (disp_arr > disp_arr.min()) &
        np.all(~np.isnan(points), axis=1) &
        np.all(~np.isinf(points), axis=1)
    )
    return points[mask], colors[mask]


def calc_point_cloud(image, disp, q):
    points = cv2.reprojectImageTo3D(disp, q).reshape(-1, 3)
    colors = image.reshape(-1, 3)
    return remove_invalid(disp.reshape(-1), points, colors)


def project_points(points, colors, r, t, k, dist_coeff, width, height):
    projected, _ = cv2.projectPoints(points, r, t, k, dist_coeff)
    xy = projected.reshape(-1, 2).astype(np.int)
    mask = (
        (0 <= xy[:, 0]) & (xy[:, 0] < width) &
        (0 <= xy[:, 1]) & (xy[:, 1] < height)
    )
    return xy[mask], colors[mask]


def calc_projected_image(points, colors, r, t, k, dist_coeff, width, height):
    xy, cm = project_points(points, colors, r, t, k, dist_coeff, width, height)
    image = np.zeros((height, width, 3), dtype=colors.dtype)
    image[xy[:, 1], xy[:, 0]] = cm
    return image


def rotate(arr, anglex, anglez):
    return np.array([  # rx
        [1, 0, 0],
        [0, np.cos(anglex), -np.sin(anglex)],
        [0, np.sin(anglex), np.cos(anglex)]
    ]).dot(np.array([  # rz
        [np.cos(anglez), 0, np.sin(anglez)],
        [0, 1, 0],
        [-np.sin(anglez), 0, np.cos(anglez)]
    ])).dot(arr)


def run(left_image, right_image, focal_length, tx):
    image = right_image
    height, width, _ = image.shape

    disp = calc_disparity(left_image, right_image)

    q = np.array([
        [1, 0, 0, -width/2],
        [0, 1, 0, -height/2],
        [0, 0, 0, focal_length],
        [0, 0, -1/tx, 0]
    ])
    points, colors = calc_point_cloud(image, disp, q)

    r = np.eye(3)
    t = np.array([0, 0, -100.0])
    k = np.array([
        [focal_length, 0, width/2],
        [0, focal_length, height/2],
        [0, 0, 1]
    ])
    dist_coeff = np.zeros((4, 1))

    def view(r, t):
        cv2.imshow('projected', calc_projected_image(
            points, colors, r, t, k, dist_coeff, width, height
        ))

    view(r, t)

    angles = {  # x, z
        'w': (-np.pi/6, 0),
        's': (np.pi/6, 0),
        'a': (0, np.pi/6),
        'd': (0, -np.pi/6)
    }

    while 1:
        key = cv2.waitKey(0)

        if key not in range(256):
            continue

        ch = chr(key)
        if ch in angles:
            ax, az = angles[ch]
            r = rotate(r, -ax, -az)
            t = rotate(t, ax, az)
            view(r, t)

        elif ch == '\x1b':  # esc
            cv2.destroyAllWindows()
            break


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('left_image')
    parser.add_argument('right_image')
    parser.add_argument('focal_length', type=float)
    parser.add_argument('distance_between_cameras', type=float)
    args = parser.parse_args()

    left_image = cv2.imread(args.left_image)
    right_image = cv2.imread(args.right_image)
    f = args.focal_length
    tx = args.distance_between_cameras

    run(left_image, right_image, f, tx)


if __name__ == '__main__':
    main()
