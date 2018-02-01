import StringIO
from selenium import webdriver
from PIL import Image
 
 
# Install instructions
#
# npm install phantomjs
# sudo apt-get install libjpeg-dev
# pip install selenium pillow
 
 
driver = webdriver.PhantomJS(executable_path="node_modules/phantomjs/bin/phantomjs")
driver.set_window_size(1366, 728) # optional
driver.get('http://google.com')
driver.save_screenshot('screen_hires.png')
 
screen = driver.get_screenshot_as_png()
 
# Crop it back to the window size (it may be taller)
box = (0, 0, 1366, 728)
im = Image.open(StringIO.StringIO(screen))
region = im.crop(box)
region.save('screen_lores.jpg', 'JPEG', optimize=True, quality=95)