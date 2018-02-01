
from flask import abort, request, Response

class Resource(object):
    """ CRUD resource """

    def create(self): self._not_implemented()
    def list(self): self._not_implemented()
    def get(self, id): self._not_implemented()
    def delete(self, id): self._not_implemented()
    def update(self, id): self._not_implemented()
    
    def _not_implemented(self):
        abort(501)

    @classmethod
    def add_urls(cls, app, name):
        def _view(*args, **kwargs):
            m = request.method.upper()
            r = cls()
            if m == "GET":
                if len(kwargs) > 0:
                    return r.get(*args, **kwargs)
                else:
                    return r.list(*args, **kwargs)
            elif m == "POST":
                return r.create(*args, **kwargs)
            elif m == "DELETE":
                return r.delete(*args, **kwargs)
            #else method == "PUT":
            return r.update(*args, **kwargs)

        _view.__name__ = name
        app.add_url_rule(name, view_func=_view, methods=("GET","POST"))
        app.add_url_rule(name + "/<id>", view_func=_view, methods=("GET", "PUT", "DELETE"))

    

if __name__ == '__main__':

    from flask import jsonify, Flask
    import simplejson as json

    res = { 1: {'name': 'test'},
            2: {'name': 'test2'}
    }

    class Test(Resource):
        """ example resource, no error control """

        def _as_json(self, o):
            return Response(json.dumps(o), mimetype='application/json')
            
        def get(self, id):
            return self._as_json(res[int(id)])

        def create(self):
            o = dict(request.form.iteritems())
            new_id =len(res.keys()) + 1
            res[new_id] = o 
            return self._as_json(new_id)

        def list(self):
            return self._as_json(res.keys())

        def delete(self, id):
            del res[int(id)]
            return 'ok'

        def update(self, id):
            res[int(id)].update(dict(request.form.iteritems()))
            return self._as_json(res[id])

    app = Flask(__name__)
    Test.add_urls(app, '/test')
    app.run(debug=True)

    # you can test with curl 
    # curl -d "name=new_name" http://localhost:5000/test
    # curl http://localhost:5000/test
    # curl http://localhost:5000/test/2
    # curl -X delete http://localhost:5000/test/2
    # curl -X put -d "name=updated_name" http://localhost:5000/test/1
    

