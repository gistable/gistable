import tornado.web

class GNUTerryPratchett(tornado.web.RequestHandler):
  
  def prepare(self):
    self.set_header("X-Clacks-Overhead", "GNU Terry Pratchett")