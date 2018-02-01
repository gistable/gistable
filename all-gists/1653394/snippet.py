from pyramid.config import Configurator
from pyramid.view import view_config

import json
import logging
import datetime 

log = logging.getLogger(__name__)

from webservice.model import Session, Machine, LogFile, LogMessage

session = Session.connect('test')

datetime_types = (datetime.time, datetime.date, datetime.datetime)

class JSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime_types):
            obj = str(obj)
 
        return obj

class BaseRestHandler(object):

    MODEL = None

    limit = 25
    order = None
    direction = None

    def __init__(self, request):
        self.request = request

        if not self.order:
            self.order = self.MODEL.created_at
            self.direction = 'descending'

    def __call__(self, *args, **kwargs):
        rv = getattr(self, self.request.method)(*args, **kwargs)
        return json.dumps(rv, cls=JSONEncoder)

    def filter(self):
        return ()

    def GET(self):
        
        query = session.query(self.MODEL)      \
                       .filter(*self.filter()) \
                       .limit(self.limit)

        query = getattr(query, self.direction)(self.order)

        return [i.to_dict(exclude=['mongo_id']) for i in query.all()]

    def POST(self):
        raise HTTPNotImplemented()

    def PUT(self):
        raise HTTPNotImplemented()

    def DELETE(self):
        raise HTTPNotImplemented()

    def __fetch_from__(self, src, model, match_key, model_attr):
        val = src.get(match_key)

        if not val:
            raise NotFound('%s not found' % model.__name__)

        try:
            obj = session.query(model).filter(model_attr == val).one()
        except NoResultFound:
            raise NotFound('%s %s not found' % (model.__name__, str(val)))

        return obj

    def __fetch__(self, model, match_key, model_attr):
        return self.__fetch_from__(self.request.matchdict,
                                   model,
                                   match_key,
                                   model_attr)

    def __post__(self, model, match_key, model_attr):
        return self.__fetch_from__(self.request.POST,
                                   model,
                                   match_key,
                                   model_attr)

@view_config(route_name='machines', renderer='string')
class MachinesHandler(BaseRestHandler):
    MODEL = Machine

@view_config(route_name='log-files', renderer='string')
class LogFilesHandler(BaseRestHandler):
    MODEL = LogMessage

@view_config(route_name='log-messages', renderer='string')
class LogsHandler(BaseRestHandler):
    MODEL = LogMessage
    
def main(global_config, **settings):

    config = Configurator(settings=settings)

    config.include('pyramid_handlers')

    config.add_static_view('static', 'ui:static')

    config.add_route('machines', '/machines')
    config.add_route('log-files', '/log-files')
    config.add_route('log-messages', '/log-messages')

    config.scan()

    return config.make_wsgi_app()
