import Image

def is_the_same(base, test_image):
  for i in range(len(base)):
      if (base[i] - test_image[i]) != 0:
          return False
  return True
    
base = Image.open('base.png').getdata()
bad = Image.open('bad.png').getdata()
good = Image.open('good.png').getdata()

print is_the_same(base, bad) # returns True
print is_the_same(base, good) # returns False
