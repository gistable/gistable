
#Send image data to v4l2loopback using python
#Remember to do sudo modprobe v4l2loopback first!
#Released under CC0 by Tim Sheerman-Chase, 2013

import fcntl, sys, os
from v4l2 import *
import time
import scipy.misc as misc
import numpy as np

def ConvertToYUYV(sizeimage, bytesperline, im):
	padding = 4096
	buff = np.zeros((sizeimage+padding, ), dtype=np.uint8)
	imgrey = im[:,:,0] * 0.299 + im[:,:,1] * 0.587 + im[:,:,2] * 0.114
	Pb = im[:,:,0] * -0.168736 + im[:,:,1] * -0.331264 + im[:,:,2] * 0.5
	Pr = im[:,:,0] * 0.5 + im[:,:,1] * -0.418688 + im[:,:,2] * -0.081312

	for y in range(imgrey.shape[0]):
		#Set lumenance
		cursor = y * bytesperline + padding
		for x in range(imgrey.shape[1]):
			try:
				buff[cursor] = imgrey[y, x]
			except IndexError:
				pass
			cursor += 2
	
		#Set color information for Cb
		cursor = y * bytesperline + padding
		for x in range(0, imgrey.shape[1], 2):
			try:
				buff[cursor+1] = 0.5 * (Pb[y, x] + Pb[y, x+1]) + 128
			except IndexError:
				pass
			cursor += 4

		#Set color information for Cr
		cursor = y * bytesperline + padding
		for x in range(0, imgrey.shape[1], 2):
			try:
				buff[cursor+3] = 0.5 * (Pr[y, x] + Pr[y, x+1]) + 128
			except IndexError:
				pass
			cursor += 4

	return buff.tostring()

if __name__=="__main__":
	devName = '/dev/video2'
	if len(sys.argv) >= 2:
		devName = sys.argv[1]
	width = 640
	height = 512
	if not os.path.exists(devName):
		print "Warning: device does not exist",devName
	device = open(devName, 'wr')

	print(device)
	capability = v4l2_capability()
	print "get capabilities result", (fcntl.ioctl(device, VIDIOC_QUERYCAP, capability))
	print "capabilities", hex(capability.capabilities)

	fmt = V4L2_PIX_FMT_YUYV
	#fmt = V4L2_PIX_FMT_YVU420

	print("v4l2 driver: " + capability.driver)
	format = v4l2_format()
	format.type = V4L2_BUF_TYPE_VIDEO_OUTPUT
	format.fmt.pix.pixelformat = fmt
	format.fmt.pix.width = width
	format.fmt.pix.height = height
	format.fmt.pix.field = V4L2_FIELD_NONE
	format.fmt.pix.bytesperline = width * 2
	format.fmt.pix.sizeimage = width * height * 2
	format.fmt.pix.colorspace = V4L2_COLORSPACE_JPEG

	print "set format result", (fcntl.ioctl(device, VIDIOC_S_FMT, format))
	#Note that format.fmt.pix.sizeimage and format.fmt.pix.bytesperline 
	#may have changed at this point

	#Create image buffer
	im = misc.imread("Lenna.png")
	buff = ConvertToYUYV(format.fmt.pix.sizeimage, format.fmt.pix.bytesperline, im)

	while True:		
		device.write(buff)
		time.sleep(1./30.)
