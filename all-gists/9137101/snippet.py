from flask import current_app

class FeatureFlags(object):

    def __init__(self, app=None):
       
        if app is not None:
            self.init_app(app)

    def init_app(self, app):

        app.config.setdefault('FEATURE_FLAGS’, {})
        
        if hasattr(app, "add_template_test"):
             app.add_template_test(self.in_config, name='active_feature')
        else:
             app.jinja_env.tests['active_feature'] = self.in_config

        app.extensions['FeatureFlags'] = self 

    def in_config(self, feature):
        try:
             return current_app.config['FEATURE_FLAGS'][feature]
        except (AttributeError, KeyError):
             return False

def is_active(feature): 
    feature_flagger = current_app.extensions['FeatureFlags']
    return feature_flagger.in_config(feature)
