import tornado.ioloop
import tornado.web
import urllib2 as urllib                        
from PIL import Image
from cStringIO import StringIO
import numpy as np
import tesserwrap
import cv2

class MainHandler(tornado.web.RequestHandler):
    def get(self):

        # Obtenemos el captcha
        url = "http://consultas.curp.gob.mx/CurpSP/imagenCatcha"
        file = StringIO(urllib.urlopen(url).read())
        original = Image.open(file)

        # Convertimos formato PIL a CV2
        cv_img = np.asarray(original)[:,:,::].copy()

        # Convertimos imagen a scala de grises.
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

        # Aplicamos filtro Canny para eliminar lineas.
        edges = cv2.Canny(gray, 60, 200, apertureSize = 3)

        # Obtenemos las lineas.
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 1, None, 0, 0)

        # Dibujamos las lineas encontradas en color blanco.
        for x1, y1, x2, y2 in lines[0]:
            cv2.line(cv_img, (x1, y1), (x2, y2), (255,255,255 ), 2)

        # Creamos una copia de nuestra imagen limpia sin lineas.
        processed = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

        # Aplicamos un desenfoque gaussiano.
        blur = cv2.GaussianBlur(processed, (3, 3), 0)

        # Aplicamos threshold.
        threshold = cv2.threshold(blur, 128, 255, cv2.THRESH_BINARY)[1]

        # Aplicamos transformación morfologica.
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (6, 6))
        morph = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)

        # Convertimos nuestra imagen final procesada a PIL.
        pil_img = Image.fromarray(morph)

        # Iniciamos tesseract y leemos la imagen.
        tesseract = tesserwrap.tesseract()
        tesseract.set_variable("tessedit_char_whitelist", "0123456789abcdefghijklmnopqrstuvwxyz")
        tesseract.set_page_seg_mode(8)
        text = tesseract.ocr_image(pil_img)
        self.write(text.strip())

application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()