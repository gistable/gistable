import cgi


def get_file(name):
    def process_post_form(req, resp, resource, params):
        # TODO: Either validate that content type is multipart/form-data
        # here, or in another hook before allowing execution to proceed.

        # This must be done to avoid a bug in cgi.FieldStorage
        env = req.env
        env.setdefault('QUERY_STRING', '')

        # TODO: Add error handling, when the request is not formatted
        # correctly or does not contain the desired field...

        # TODO: Consider overriding make_file, so that you can
        # stream directly to the destination rather than
        # buffering using TemporaryFile (see http://goo.gl/Yo8h3P)
        form = cgi.FieldStorage(fp=req.stream, environ=env)

        file_item = form[name]
        if file_item.file:
            # It's an uploaded file
            params['file'] = file_item.file
        else:
            # TODO: Raise an error
            pass

    return process_post_form


# Elsewhere...
import falcon


class MyResource(object):
    @falcon.before(get_file('userfile'))
    def on_post(self, req, resp, file):
        pass