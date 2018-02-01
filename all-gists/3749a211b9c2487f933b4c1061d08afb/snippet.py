import pygame, sys

pygame.init()

size = (800, 600)

screen = pygame.display.set_mode(size)

clock = pygame.time.Clock()

xP1 = 1

yP1 = 300

xP2 = 778

yP2 = 300

xP3 = 375

yP3 = 1

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_w]:
        yP1 -=1
    if pressed[pygame.K_s]:
        yP1 +=1
    if pressed[pygame.K_a]:
        xP1 -=1
    if pressed[pygame.K_d]:
        xP1 +=1
    if pressed[pygame.K_i]:
        yP2 -= 1
    if pressed[pygame.K_k]:
        yP2 += 1
    if pressed[pygame.K_j]:
        xP2 -= 1
    if pressed[pygame.K_l]:
        xP2 += 1
    if pressed[pygame.K_t]:
        yP3 -= 1
    if pressed[pygame.K_g]:
        yP3 += 1
    if pressed[pygame.K_f]:
        xP3 -= 1
    if pressed[pygame.K_h]:
        xP3 += 1
    screen.fill((0,0,20))

    player1_rect =  pygame.Rect(xP1, yP1, 20, 20)
    player12_rect = pygame.Rect(xP1, yP1, 15, 15)
    player123_rect = pygame.Rect(xP1, yP1, 10, 10)
    player2_rect = pygame.Rect(xP2, yP2, 25, 25)

    player3_rect = pygame.Rect(xP3, yP3, 30, 30)

    pygame.draw.rect(screen, (150, 0, 150), player3_rect)
    pygame.draw.rect(screen, (0, 150, 150), player2_rect)
    pygame.draw.rect(screen, (150, 10, 0), player1_rect,)
    pygame.draw.rect(screen, (150, 150, 0), player12_rect)
    pygame.draw.rect(screen, (50, 0, 50), player123_rect)
    pygame.display.update()

    clock.tick(60)