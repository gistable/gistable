# coding: utf-8

import photos
import console
from objc_util import *

CIFilter, CIImage, CIContext, CIDetector, CIVector = map(ObjCClass, ['CIFilter', 'CIImage', 'CIContext', 'CIDetector', 'CIVector'])

def take_photo(filename='.temp.jpg'):
	img = photos.capture_image()
	if img:
		img.save(filename)
		return filename

def pick_photo(filename='.temp.jpg'):
	img = photos.pick_image()
	if img:
		img.save(filename)
		return filename

def load_ci_image(img_filename):
	data = NSData.dataWithContentsOfFile_(img_filename)
	if not data:
		raise IOError('Could not read file')
	ci_img = CIImage.imageWithData_(data)
	return ci_img
	
def find_faces(ci_img):
	opt = {'CIDetectorAccuracy': 'CIDetectorAccuracyHigh'}
	d = CIDetector.detectorOfType_context_options_('CIDetectorTypeFace', None, opt)
	faces = d.featuresInImage_(ci_img)
	return faces

def apply_perspective(corners, ci_img):
	tr, br, tl, bl = [CIVector.vectorWithX_Y_(c.x, c.y) for c in corners]
	filter = CIFilter.filterWithName_('CIPerspectiveCorrection')
	filter.setDefaults()
	filter.setValue_forKey_(ci_img, 'inputImage')
	filter.setValue_forKey_(tr, 'inputTopRight')
	filter.setValue_forKey_(tl, 'inputTopLeft')
	filter.setValue_forKey_(br, 'inputBottomRight')
	filter.setValue_forKey_(bl, 'inputBottomLeft')
	out_img = filter.valueForKey_('outputImage')
	return out_img

def write_output(out_ci_img, filename='.output.jpg'):
	ctx = CIContext.contextWithOptions_(None)
	cg_img = ctx.createCGImage_fromRect_(out_ci_img, out_ci_img.extent())
	ui_img = UIImage.imageWithCGImage_(cg_img)
	c.CGImageRelease.argtypes = [c_void_p]
	c.CGImageRelease.restype = None
	c.CGImageRelease(cg_img)
	c.UIImageJPEGRepresentation.argtypes = [c_void_p, CGFloat]
	c.UIImageJPEGRepresentation.restype = c_void_p
	data = ObjCInstance(c.UIImageJPEGRepresentation(ui_img.ptr, 0.75))
	data.writeToFile_atomically_(filename, True)
	return filename

def main():
	console.clear()
	i = console.alert('Info', 'This script detects faces in a photo.', 'Take Photo', 'Pick from Library')
	if i == 1:
		filename = take_photo()
	else:
		filename = pick_photo()
	if not filename:
		return
	ci_img = load_ci_image(filename)
	out_file = write_output(ci_img)
	console.show_image(out_file)
	faces = find_faces(ci_img)
	if faces.count() == 0:
		print('Error: Could not find a face in the photo. Please try again with a different image.')
		return
	j=0
	for face in faces:
		b = face.bounds()
		w=b.size.width
		h=b.size.height
		rt=CGPoint(b.origin.x+w,b.origin.y+h)
		rb=CGPoint(b.origin.x+w,b.origin.y)
		lt=CGPoint(b.origin.x,b.origin.y+h)
		lb=CGPoint(b.origin.x,b.origin.y)
		corners = (rt,rb,lt,lb)
		out_img = apply_perspective(corners, ci_img)
		j=j+1
		out_file = write_output(out_img,filename='.output'+str(j)+'.jpg')
		console.show_image(out_file)
	print('Tap and hold the image to save it to your camera roll.')

if __name__ == '__main__':
	main()
	
