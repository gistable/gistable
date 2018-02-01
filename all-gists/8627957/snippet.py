VIEWS_DIR_NAME = 'views'

# Load all the views in the package called VIEW_DIR_NAME:
for fn in listdir(VIEWS_DIR_NAME):
	if fn.startswith('_') or not fn.endswith('.py'):
		continue
	fn = fn[:-3]	# remove extension
	try:
		vmod = importlib.import_module('%s.%s' % (VIEWS_DIR_NAME, fn))
		app.register_blueprint(vmod.mod)	# assumes the Blueprint will be called "mod" within the file
		print "loaded view:", fn
	except AttributeError:
		continue
