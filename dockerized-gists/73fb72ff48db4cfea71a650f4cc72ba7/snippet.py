# https://gist.github.com/gretel/73fb72ff48db4cfea71a650f4cc72ba7
# based on example at https://github.com/pupil-labs/pyuvc
# install libuvc and pyuvc - see https://github.com/pupil-labs/pyuvc/blob/master/README.md
# install pygame (pip install pygame)

import uvc
import sys
import logging
import pygame
from pygame.locals import *

logging.basicConfig(level=logging.INFO)

SCREEN_SIZE = (1280, 720)
CAP_MODE = (1280, 720, 30) # TODO: how to add int to tuple?

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption('wtfcam')

dev_list =  uvc.device_list()
print dev_list
cap = uvc.Capture(dev_list[0]['uid']) # TODO: choosable camera
print cap.avaible_modes

cap.frame_mode = CAP_MODE
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit(0)
    frame = cap.get_frame_robust()
    # TODO: fails with anything else than RGB
    surf = pygame.image.fromstring(frame.bgr.tostring(), SCREEN_SIZE, 'RGB', True).convert()
    screen.blit(surf, (0,0))
    pygame.display.update()
    pygame.time.delay(100)
