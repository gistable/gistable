from flask import Flask as DefaultFlask

class Flask(DefaultFlask):
  def create_jinja_environment(self):
    self.jinja_options = dict(self.jinja_options)
    if 'JINJA_CACHE_SIZE' in self.config:
      self.jinja_options['cache_size'] = self.config['JINJA_CACHE_SIZE']
    return super(Flask, self).create_jinja_environment()