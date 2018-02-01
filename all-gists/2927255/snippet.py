class CacheBaseHandler(tornado.web.RequestHandler):

    def prepare(self):
        cached = self.application.db.cache.find_one({"slug": self.request.path})
        if cached is not None:
            self.write(cached["content"])
            self.finish()

    def render_string(self, template_name, **kwargs):
        html_generated = \
            super(CacheBaseHandler, self).render_string(template_name, **kwargs)
        self.application.db.cache.update({"slug": self.request.path},
            {"$set": {"content": html_generated}},
            upsert=True)
        return html_generated