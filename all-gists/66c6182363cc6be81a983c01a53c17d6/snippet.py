class Thing(object):
    URI_TEMPLATE = '/things/{tid}'

    def on_get(self, req, resp, tid):
        pass


# ...

thing = Thing()

app = falcon.API()
app.add_route(thing.URI_TEMPLATE, thing)