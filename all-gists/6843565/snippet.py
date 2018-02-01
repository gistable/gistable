from __future__ import division, print_function
import Image

class Wallmask(object):
    def __init__(self):
        self.load_wallmask("Maps/ctf_dirtbowl_v2.png")
        self.name = "ctf_dirtbowl_v2"
        
    def load_wallmask(self, name):
        print("---LOADING WALLMASK---")
    
        image = Image.open(name)
        for key, value in image.text.items():
            if key == "Gang Garrison 2 Level Data":
                text = value
                break
                
        text = text[text.find("{WALKMASK}\n")+len("{WALKMASK}\n"):text.find("\n{END WALKMASK}")]
        index = text.find("\n")
        self.width = int(text[:index])
        text = text[index+1:]
        index = text.find("\n")
        self.height = int(text[:index])
        text = text[index+1:]
        
        self.mask = [[False for j in range(self.height)] for i in range(self.width)]
        
        self.uncompress_wallmask_data(text)
        
        
        large_mask = [[False for j in range(len(self.mask[0])*6)] for i in range(len(self.mask)*6)]
        for i in range(len(self.mask)*6):
            for j in range(len(self.mask[0])*6 - 7):
                large_mask[i][j] = self.mask[int(i/6)][int(j/6)]
        self.mask = large_mask
        self.width = len(self.mask)
        self.height = len(self.mask[0])

    def uncompress_wallmask_data(self, data):
        bitmask = 0x1
        index = len(data)-1
        value = ord(data[index]) - 32
        
        for i in range(len(data)*6 - self.width*self.height):
            bitmask *= 2
        for y in range(self.height-1, -1, -1):
            for x in range(self.width-1, -1, -1):
                if bitmask == 64:
                    index -= 1
                    bitmask = 0x1
                    value = ord(data[index]) - 32
                if value & bitmask:
                    self.mask[x][y] = True
                bitmask *= 2


    def print_wallmask(self):
        n_image = Image.new("L", (self.width, self.height))
        for x in range(self.width):
            for y in range(self.height):
                if self.mask[x][y]:
                    n_image.putpixel((x, y), 0)
                else:
                    n_image.putpixel((x, y), 255)
        n_image.save("output.png")