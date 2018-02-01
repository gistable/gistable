import os
import dropbox
from pprint import pprint

app_key = 'z01qsf9cucfefhg'
app_secret = 'zudrr24prtqivjt'

DEBUG = 0
CFG_DEFAULT = os.path.join(os.getenv('HOME'), '.romsync')


# A Config object to store and load settings
class Config(object):
	settings = {}
	path = ''


	def __init__(self, path=CFG_DEFAULT):
		self.path = path
		self.load()


	# Return value of setting
	def get(self, key):
		return self.settings[key]


	# Update the cursor
	def set_cursor(self, cursor):
		self.settings['cursor'] = cursor


	# Write settings to config
	def save(self):
		open(self.path, 'w').close()	# Flush config before writing
		with open(self.path, 'w') as cfg:
			for key in self.settings:
				cfg.write(key + '=' + self.settings[key] + '\n')


	# Load settings from config
	# return: True if config exists, False otherwise
	def load(self):
		if os.path.isfile(self.path):
			with open(self.path, 'r') as cfg:
				for line in cfg:
					key = line.replace(" ", "").split('=')[0]
					value = line.replace(" ", "").split('=')[1].rstrip()
					self.settings[key] = value
			return True
		else:
			with open(self.path, 'w') as cfg:
				# Generate authorization code
				flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)
				authorize_url = flow.start()

				print('1. Go to: ' + authorize_url)
				print('2. Click "Allow" (you might have to log in first)')
				print('3. Copy the authorization code.')
				code = input('Enter the authorization code here: ').strip()
				local_path = input('Enter your local roms directory: ')

				access_token, user_id = flow.finish(code)

				# Write default settings to config 
				cfg.write('access_token=' + access_token + '\n')
				cfg.write('db_roms=/romsync\n')
				cfg.write('local_roms=' + local_path + '\n')
				cfg.write('cursor= ' + '\n')

				return False


# Download/remove files and directories
# return: dictionary of modified files
def delta_sync(client, delta, config):
	dirs = []
	files = []

	file_change = {'added': [], 'removed': []}
	entries = delta['entries']
	local_path = config.get('local_roms')
	db_path = config.get('db_roms')

	for e in entries:
		path = e[0].replace(db_path, local_path)
		if(e[1] != None):
			try:
				if(e[1]['is_dir']):
					if(len(path) > 0):
						os.makedirs(path)
				else:
					out = open(path, 'wb')
					with client.get_file(e[1]['path']) as rom:
						out.write(rom.read())
					file_change['added'].append(path.replace(local_path, ''))
			except:
				if(DEBUG):
					print(path, ' already exists')
		else:
			try:
				if os.path.isdir(path):
					shutil.rmtree(path)
					for child in os.listdir(path):
						file_change['removed'].append(child)
				else:
					os.remove(path)
					file_change['removed'].append(path.replace(local_path, ''))
			except:
				if(DEBUG):
					print(path, ' does not exist')

	return file_change


def main():

	config = Config()
	config_exists = config.load()

	# Get client
	client = dropbox.client.DropboxClient(config.get('access_token'))
	delta = client.delta(path_prefix=config.get('db_roms'), cursor=config.get('cursor'))
	if DEBUG:
		print(delta)

	# Sync files
	# Report added and removed files
	if(len(delta['entries']) > 0):
		print('Syncing roms...')

		file_change = delta_sync(client, delta, config)
		added = len(file_change['added'])
		removed = len(file_change['removed'])

		if(added > 0):
			print('\n'+'Fetched %s rom(s)' % str(added))
			for entry in file_change['added']:
				rom = entry.split(os.sep)
				print(rom[0] + ' - ' + rom[1])
		if(removed > 0):
			print('\n'+'Removed %s rom(s)' % str(removed))
			for entry in file_change['removed']:
				print(entry)
		print('')
	else:
		print('No need to sync')

	# Update config with new cursor
	config.set_cursor(delta['cursor'])
	config.save()	


if __name__ == "__main__":
    main()