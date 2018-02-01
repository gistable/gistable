#!/usr/bin/env python

from pygame import camera
import pygame
import time
import cv
import os


# Recognition
HAAR_PATH = "/usr/share/opencv/haarcascades/"

# Face
FACE_HAAR = os.path.join(HAAR_PATH, "haarcascade_frontalface_default.xml")
FACE_HAAR = cv.Load(FACE_HAAR)

# Eye
EYE_HAAR = os.path.join(HAAR_PATH, "haarcascade_mcs_righteye.xml")
EYE_HAAR = cv.Load(EYE_HAAR)

# Nose
NOSE_HAAR = os.path.join(HAAR_PATH, "haarcascade_mcs_nose.xml")
NOSE_HAAR = cv.Load(NOSE_HAAR)

# Mouth
MOUTH_HAAR = os.path.join(HAAR_PATH, "haarcascade_mcs_mouth.xml")
MOUTH_HAAR = cv.Load(MOUTH_HAAR)

# Screen settings
SCREEN = [640, 360]


def surface_to_string(surface):
    """Convert a pygame surface into string"""
    return pygame.image.tostring(surface, 'RGB')


def pygame_to_cvimage(surface):
    """Convert a pygame surface into a cv image"""
    cv_image = cv.CreateImageHeader(surface.get_size(), cv.IPL_DEPTH_8U, 3)
    image_string = surface_to_string(surface)
    cv.SetData(cv_image, image_string)
    return cv_image


def cvimage_grayscale(cv_image):
    """Converts a cvimage into grayscale"""
    grayscale = cv.CreateImage(cv.GetSize(cv_image), 8, 1)
    cv.CvtColor(cv_image, grayscale, cv.CV_RGB2GRAY)
    return grayscale


def cvimage_to_pygame(image):
    """Convert cvimage into a pygame image"""
    image_rgb = cv.CreateMat(image.height, image.width, cv.CV_8UC3)
    cv.CvtColor(image, image_rgb, cv.CV_BGR2RGB)
    return pygame.image.frombuffer(image.tostring(), cv.GetSize(image_rgb),
                                   "RGB")


def detect_faces(cv_image, storage):
    """Detects faces based on haar. Returns points"""
    return cv.HaarDetectObjects(cvimage_grayscale(cv_image), FACE_HAAR,
                                storage)


def detect_eyes(cv_image, storage):
    """Detects eyes based on haar. Returns points"""
    return cv.HaarDetectObjects(cvimage_grayscale(cv_image), EYE_HAAR,
                                storage)


def detect_nose(cv_image, storage):
    """Detects nose based on haar. Returns ponts"""
    return cv.HaarDetectObjects(cvimage_grayscale(cv_image), NOSE_HAAR,
                                storage)


def detect_mouth(cv_image, storage):
    """Detects mouth based on haar. Returns points"""
    return cv.HaarDetectObjects(cvimage_grayscale(cv_image), MOUTH_HAAR,
                                storage)


def draw_from_points(cv_image, points):
    """Takes the cv_image and points and draws a rectangle based on the points.
    Returns a cv_image."""
    for (x, y, w, h), n in points:
        cv.Rectangle(cv_image, (x, y), (x + w, y + h), 255)
    return cv_image


if __name__ == '__main__':

    # Set game screen
    screen = pygame.display.set_mode(SCREEN)

    pygame.init()  # Initialize pygame
    camera.init()  # Initialize camera

    # Load camera source then start
    cam = camera.Camera('/dev/video0', SCREEN)
    cam.start()

    while 1:  # Ze loop

        time.sleep(1 / 120)  # 60 frames per second

        image = cam.get_image()  # Get current webcam image

        cv_image = pygame_to_cvimage(image)  # Create cv image from pygame image

        # Detect faces then draw points on image
        # FIXME: Current bottleneck. Image has to be Grayscale to make it faster.
        #        One solution would be to use opencv instead of pygame for
        #        capturing images.
        storage = cv.CreateMemStorage(-1)  # Create storage
        #points = detect_eyes(cv_image, storage) + \
        #        detect_nose(cv_image, storage) + \
        #        detect_mouth(cv_image, storage)
        points = detect_faces(cv_image, storage)  # Get points of faces.
        cv_image = draw_from_points(cv_image, points)  # Draw points

        screen.fill([0, 0, 0])  # Blank fill the screen

        screen.blit(cvimage_to_pygame(cv_image), (0, 0))  # Load new image on screen

        pygame.display.update()  # Update pygame display
