import os

from importlib import import_module

from flask.blueprints import Blueprint


def load_blueprints_from_path(app, packages_path, blueprint_name='bp'):
    blueprints = []

    for name in os.listdir(packages_path):
        if os.path.isdir(os.path.join(packages_path, name)):

            blueprint_name = blueprint_name
            path, base_name = os.path.split(packages_path)
            package_name = name

            try:
                package = import_module('{}.{}'.format(base_name, package_name))
                module = getattr(package, blueprint_name)

                if isinstance(module, Blueprint):
                    blueprints.append(module)

                    # Register blueprint
                    app.register_blueprint(module)
                    print "Blueprint Installed: {}".format(name)
            except ImportError, AttributeError:
                pass

    return blueprints