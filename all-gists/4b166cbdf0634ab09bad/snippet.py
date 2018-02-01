# -*- coding: utf-8 -*-

from flask import request, Blueprint, jsonify, Response
from werkzeug.routing import Map, Rule
import json
import traceback

"""
# TODO: 함수명 중복을 피하기 위해 __v를 붙였는데 맘에 안듬..
# TODO: 버전을 입력하지 않았을 때는 최신 버전으로..

app = Flask(__name__)
app.apis = ApisRouter(app)

# /apis/v1.0/test
@app.apis.route('/test', methods=['GET'], version=1.0)
def test_api():
    return '1.0'

# /apis/v2.0/test
@app.apis.route('/test', methods=['GET'], version=2.0)
def test_api__v2():
    return '2.0'

# /apis/v2.1/test
@app.apis.route('/test', methods=['GET'], version=2.1, endpoint='test_api')
def hello():
    return '2.1'
"""


class ApisRouter(object):
    def __init__(self, server, url_prefix='/apis', name='apis'):
        self.server = server
        self.url_map = Map()

        self.versions = []
        self.versioning_viewfunc = {}

        self.blueprint = Blueprint(name, __name__)
        self.blueprint.add_url_rule(
            '/<string:version>/<path:path>', endpoint='route',
            view_func=self.route_func)
        self.server.register_blueprint(self.blueprint, url_prefix=url_prefix)

    def route_func(self, version, path):
        if not version.startswith('v'):
            return 'TODO'

        try:
            version = version.split('v')[1]
            version = float(version)
        except ValueError:
            version = None
            return 'TODO'

        if version is None or type(version) != float:
            return 'TODO'

        environ = request.environ
        environ['PATH_INFO'] = '/' + path

        url_adapter = self.create_url_adapter(request)
        url_rule, view_args = url_adapter.match(return_rule=True)

        viewfunc = self.get_viewfunc(url_rule, version)

        if viewfunc is None:
            return 'No view function found.'

        res = None
        try:
            rst = viewfunc(**view_args)
            if rst is None:
                rst = {}

            if type(rst) == dict:
                res = jsonify(**rst)
            elif type(rst) == list:
                res = Response(json.dumps(rst), mimetype='application/json')
            else:
                res = Response(str(rst))
        except BaseException as e:
            res = Response(json.dumps({
                'exception': e.__class__.__name__,
                'reason': str(e)
            }), mimetype='application/json')
            res.status_code = e.status
            traceback.print_exc()
        except Exception as e:
            res = Response(json.dumps({
                'exception': e.__class__.__name__,
                'reason': str(e)
            }), mimetype='application/json')
            res.status_code = 500
            traceback.print_exc()
        return res

    def route(self, rule, **options):
        version = options.pop('version', 1.0)

        def decorator(f):
            methods = options.pop('methods', None)
            endpoint = options.get('endpoint', None)
            if 'endpoint' not in options:
                endpoint = f.__name__
                endpoint = endpoint.split('__v')[0]
                options['endpoint'] = endpoint
            rule_obj = Rule(rule, methods=methods, **options)
            self.url_map.add(rule_obj)
            self.add_viewfunc(endpoint, version, f)
            return f

        return decorator

    def create_url_adapter(self, request):
        return self.url_map.bind_to_environ(
            request.environ,
            server_name=self.server.config['SERVER_NAME'])

    def add_viewfunc(self, endpoint, version, viewfunc):
        if version not in self.versioning_viewfunc:
            self.versioning_viewfunc[version] = {}
            self.versions = sorted(self.versioning_viewfunc.keys(),
                                   reverse=True)

        self.versioning_viewfunc[version][endpoint] = viewfunc

    def get_viewfunc(self, rule, version):
        target_versions = []
        for v in self.versions:
            if v <= version:
                target_versions.append(v)

        viewfunc = None
        for v in target_versions:
            viewfuncs = self.versioning_viewfunc.get(v, {})

            viewfunc = viewfuncs.get(rule.endpoint, None)
            if viewfunc is not None:
                break

        return viewfunc


class BaseException(Exception):
    status = 500
    values = {}

    def __init__(self, **kwargs):
        super(BaseException, self).__init__(self.message)
        self.values = kwargs

    def __str__(self):
        return u'{0}'.format(json.dumps(self.values))
