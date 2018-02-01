"""
Sorl Thumbnail Engine that accepts background color
---------------------------------------------------

Created on Sunday, February 2012 by Yuji Tomita
"""
from PIL import Image, ImageColor
from sorl.thumbnail.engines.pil_engine import Engine


class Engine(Engine):
	def create(self, image, geometry, options):
		thumb = super(Engine, self).create(image, geometry, options)
		if options.get('background'):		
			try:
				background = Image.new('RGB', thumb.size, ImageColor.getcolor(options.get('background'), 'RGB'))
				background.paste(thumb, mask=thumb.split()[3]) # 3 is the alpha of an RGBA image.
				return background
			except Exception, e:
				return thumb
		return thumb