from django.core.files.temp import NamedTemporaryFile

def save_image_from_url(self):
        """
        Save remote images from url to image field.
        Requires python-requests
        """
        r = requests.get(self.image_url)

        if r.status_code == 200:
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(r.content)
            img_temp.flush()

            try:
                self.image.save(os.path.basename(self.image_url), File(img_temp), save=True)
            except:
                print "Failed downloading image from ", self.image_url
                return False
            else:
                return True
        else:
            return False