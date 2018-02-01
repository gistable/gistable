from os import walk, path
import sys
import pygame

extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
width, height = 1920, 1080

if len(sys.argv) != 2:
    print 'usage: %s <path>' % sys.argv[0]
    sys.exit(1)
root_path = sys.argv[1]

screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
print 'Showing images from folder: %s' % root_path

while True:
    # Scan folder
    file_names = []
    for (dirpath, dirs, files) in walk(root_path):
        file_names.extend([path.join(dirpath, f) for f in files if path.splitext(f)[1] in extensions])

    # Iterate over all paths, load images into memory
    images = []
    for img_file in file_names:
        try:
            images.append(pygame.image.load(img_file))
        except:
            pass

    #  Display the images for a short time
    for img in images:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
        # Center image on screen
        r = img.get_rect()
        screen.blit(img, r.move((width-r.w)/2, (height-r.h)/2))
        pygame.display.flip()
        pygame.time.wait(2000)