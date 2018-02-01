    def _thumbnail_image(self, body, size):
        try:
            im = Image.open(StringIO(body))

            # rotate image according rotation meta of this image
#            for orientation in ExifTags.TAGS.keys():
#                if ExifTags.TAGS[orientation] == 'Orientation' : break
            orientation = 274  # get 274 through upper loop
            try:
                exif = im._getexif()
                if exif:
                    exif = dict(exif.items())
                    if exif[orientation] == 3:
                        im = im.rotate(180, expand=True)
                    elif exif[orientation] == 6:
                        im = im.rotate(270, expand=True)
                    elif exif[orientation] == 8:
                        im = im.rotate(90, expand=True)
            except:
                # There is AttributeError: _getexif sometimes.
                pass

            im.thumbnail(size, Image.ANTIALIAS)
            # avoid KeyError(ext) # unknown extension
            # http://www.velocityreviews.com/forums/t339757-convert-all-images-to-jpeg.html
            # http://stackoverflow.com/questions/646286/python-pil-how-to-write-png-image-to-string
            if im.mode != "RGB":
                im = im.convert("RGB")

            # get image string
            s = StringIO()
            im.save(s, "JPEG", quality=options.image_quality)
            body = s.getvalue()
            s.close()

            return body, im.size
        except IOError, e:
            logging.error("Image resize error: %s" % e)