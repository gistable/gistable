import os

# your xcode project directory
directory = ''

for root, _, files in os.walk(directory):
	for f in files:
		edited = False
		fullpath = os.path.join(root, f)
		with open(fullpath, 'r') as open_file:
			contents = open_file.read()
			if contents[:3] == "'''" or contents[:3] == '"""':
				edited = True
				contents = "#dummycomment\n" + contents
				
			if contents[:2] == '#!':
				edited = True
				contents = contents.splitlines(True)
				contents[0] = '#dummycomment\n'
				contents = ''.join(contents)

		if edited:
			with open(fullpath, 'w') as open_file:
				open_file.write(contents)
				
print "Done"