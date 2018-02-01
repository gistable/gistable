from PIL import Image

backgroundColor = (0,)*3
pixelSize = 9

image = Image.open('input.png')
image = image.resize((image.size[0]/pixelSize, image.size[1]/pixelSize), Image.NEAREST)
image = image.resize((image.size[0]*pixelSize, image.size[1]*pixelSize), Image.NEAREST)
pixel = image.load()

for i in range(0,image.size[0],pixelSize):
  for j in range(0,image.size[1],pixelSize):
    for r in range(pixelSize):
      pixel[i+r,j] = backgroundColor
      pixel[i,j+r] = backgroundColor

image.save('output.png')
