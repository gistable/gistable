from IPython.core.display import Image as image
from PIL import Image

def save_and_display(arr, fname):
    pilimg = Image.fromarray(arr)
    pilimg.save(fname)
    return image(filename=fname, width=600)