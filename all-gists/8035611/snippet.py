from hashlib import sha256
import os

from pyramid.session import SignedCookieSessionFactory

def make_session_id():
  rand = os.urandom()
  return sha256(sha256(rand).digest()).hexdigest()

class MemorySessionSerializer(object):
  def __init__(self):
    self.sessions = {}
    
  def loads(self, bstruct):
    session_id = bstruct.decode('utf-8')
    try:
      return self.sessions[session_id]
    except KeyError:
      raise ValueError
  
  def dumps(self, appstruct):
    # damn, we have no unhacky way to reuse the old session id
    session_id = make_session_id()
    self.sessions[session_id] = appstruct
    return session_id.encode('utf-8')

def main(global_config, **settings):
  config = Configurator(settings=settings)
  
  serializer = MemorySessionSerializer()
  session_factory = SignedCookieSessionFactory(
    settings['session.secret'],
    serializer=serializer,
  )
  config.set_session_factory(session_factory)
  
  return config.make_wsgi_app()