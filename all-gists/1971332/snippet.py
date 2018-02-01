temp_image = Image.open("picture.png")
raw_image = temp_image.tostring()

image = pyglet.image.ImageData(width, height, 'RGB', raw_image, pitch= -resized_x * 3)