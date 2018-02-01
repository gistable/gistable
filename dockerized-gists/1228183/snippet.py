import tornado.web
import tornado.ioloop
import logging
import os.path


def clean_filename(filename):
    i = filename.rfind(".")
    if i != -1:
        filename = filename[0:i] + filename[i:].lower()
    return filename


def get_or_create_file(chunk, dst):
    if chunk == 0:
        f = file(dst, 'wb')
    else:
        f = file(dst, 'ab')
    return f


class UploadHandler(tornado.web.RequestHandler):
    def post(self):
        filename = clean_filename(self.get_argument('name'))
        dst = os.path.join('static', 'upload', filename)

        chunk = int(self.get_argument('chunk', '0'))
        chunks = int(self.get_argument('chunks', 0))

        f = get_or_create_file(chunk, dst)
        body = self.request.files['file'][0]['body']
        f.write(body)
        f.close()

        self.write('uploaded')


if __name__ == "__main__":
    logging.basicConfig()
    
    handlers = [
        (r"/upload", UploadHandler),
    ]
    
    application = tornado.web.Application(handlers,
                                          static_path='static',
                                          )
    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()
