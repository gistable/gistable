import os 
from pyramid.config import Configurator


def main(global_config, **settings):
    settings = {k: os.path.expandvars(v) for k, v in settings.items()}
    config = Configurator(settings=settings)
    config.include(__name__)
    return config.make_wsgi_app()


def includeme(config):
    pass