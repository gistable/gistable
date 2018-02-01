import os

ENV_VARS_FILENAME = '.env'

def import_env_vars(project_root):
	"""Imports some environment variables from a special .env file in the
	project root directory.

	"""
	if len(project_root) > 0 and project_root[-1] != '/':
		project_root += '/'
	try:
		envfile = file(project_root+ENV_VARS_FILENAME)
	except IOError:
		raise Exception("You must have a {0} file in your project root "
		                "in order to run the server in your local machine. "
		                "This specifies some necessary environment variables. ")
	for line in envfile.readlines():
		[key,value] = line.strip().split("=")
		os.environ[key] = value