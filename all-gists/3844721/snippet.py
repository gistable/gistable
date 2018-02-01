import os

PATH = path/to/my/blueprints/directory
BLUEPRINT = 'the_blueprint'

def import_file(path, name=None):
    """ imports a file with given name and path """
    # use the imp module to do actual imports
    import imp
    name = name or os.path.split(path)[-1].replace(".", "_")
    fp, pathname, description = imp.find_module(path)
    return imp.load_module(name, fp, pathname, description)

def register_blueprints(app, files, blueprint_attribute):
    """ registers the blueprints from a given set of files on the given app 

    Parameters:
       app - the Flask application on which to register the blueprints
       files - an iterable of file names to be dynamically imported
       blueprint_attribute - the name of the actually blueprint in each file.
           (e.g. for the flask blueprints example - http://flask.pocoo.org/docs/blueprints/ - you'd
           use 'simple_page')
    """
    imported_modules = [import_file(file) for file in files]
    for module in imported_modules:
        app.register(getattr(module, blueprint_attribute))

if __name__ == "__main__":
   # get the files that end in py in the folder
   filelist = (file for file in os.listdir(PATH) if file.endswith ".py")
   from my_app import app
   register_blueprints(app, filelist, BLUEPRINT)