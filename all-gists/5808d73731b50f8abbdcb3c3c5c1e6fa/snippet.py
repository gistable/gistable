from PIL import Image
if __name__ == "__main__":
    im = Image.open("mr.zhang.jpg")
    x, y = im.size
    for i in range(x):
        for j in range(y):
            r, g, b = im.getpixel((i,j))
            if (20< r < 180) and (80< g < 250) and (180< b< 265):
                r, g, b = 255, 255, 255
            im.putpixel((i, j), (r, g, b))
    im.show()
