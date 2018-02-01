import pygame
import os, sys

width, height = 400, 400
os.environ['SDL_VIDEO_CENTERED'] = '1'
screen = pygame.display.set_mode((width, height))

class Core(object):
    def __init__(self, surface, name):
        pygame.display.set_caption(name)
        self.screen = surface
                
    def dispatch(self, event):
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            sys.exit()     
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pass
            
    def run(self):
        while True:
            for event in pygame.event.get():
                self.dispatch(event)
                
            self.screen.fill([0xFF, 0xFF, 0xFF])
            pygame.display.flip()

if __name__ == '__main__':
    main = Core(screen, 'Node')
    main.run()
