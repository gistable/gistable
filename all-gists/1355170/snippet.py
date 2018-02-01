"Customize Flask to select a template based on some criteria."

import os

from flask import Flask, request, render_template
from flask.helpers import locked_cached_property
from jinja2 import FileSystemLoader, TemplateNotFound

# Import a detection utility from your project, not defined here.
# Takes a request object and returns True if browser is mobile.
# Could sniff User-Agent, use sessions, or look for URL arguments.
from my_helpers import detect_mobile_browser


# Customize Flask. Could move these two classes to a separate Python module.
class DetectingFlask(Flask):
    "A Flask with separate templates for mobile and desktop browsers."

    @locked_cached_property
    def jinja_loader(self):
        "Override for a custom template loader."
        if self.template_folder is not None:
            return DetectingLoader(os.path.join(self.root_path,
                                                self.template_folder))


# See jinja2.loaders for ideas on template loaders.
class DetectingLoader(FileSystemLoader):
    "Template loader choosing template based on browser detection, w/defaults."

    def get_source(self, environment, template):
        # Consider moving the mobile template prefix to a config variable.
        if detect_mobile_browser(request):
            mobile_template = 'm/' + template
            try:
                return super(DetectingLoader, self).get_source(environment,
                                                               mobile_template)
            except TemplateNotFound:
                pass # Fall back to default template.
        return super(DetectingLoader, self).get_source(environment, template)


app = DetectingFlask(__name__)


@app.route('/')
def index():
    return render_template('index.html')
