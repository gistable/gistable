import os

# def create_directory
# parameter_taken : directory name
# function :
#	1. make directory named var directory
def create_directory(directory):
	if not os.path.exists(directory):
		print('project created')
		os.makedirs(directory)


# def create_data_files
# parameter_taken : project name and base_url(targeted website url)
# function :
#	1. store file path name in a var queue and crawled
#	2. call create_file(file_name, base_url) to create_file if not exists
def create_data_files(project, base_url):
	queue = project + '\queue.text'
	crawled = project + '\crawled.txt'
	if not os.path.isfile(queue):
		create_file(queue, base_url)
	if not os.path.isfile(crawled):
		#passing a blank value in data parameter in create_file(file_name, data)
		create_file(crawled, '')


# def create_file
# parameter_taken : file_name and data
# function :
#	1. open file in write mode
#	2. write if there is any data
#	3. close()
def create_file(file_name, data):
	with open(file_name, 'w') as f:
		f.write(data)
		f.close()


# def append_data
# parameter_taken : file_name and data
# function :
#	1. open file in append mode
#	2. append if there is any data
#	3. close()
def append_data(file_name, data):
	with open(file_name, 'a')as f:
		f.write(data + '\n')
		f.close()


# def delete_data
# parameter_taken : file_name
# function :
#	1. open file in write mode
#	2. pass
#	[basically its override the existing file and writes nothing]
def delete_data(file_name):
	with open(file_name, 'w') as f:
		pass
		f.close()


# def file_to_set
# parameter_taken : file_name
# function :
#	1. convert the file into a set
#		a. declearing an empty set
#		b. open the file in readText mode
#		c. loop through each line in the file
#		d. add every line in the set
#		e.replace new line with blank value
def file_to_set(file_name):
	result = set()
	with open(file_name, 'rt') as f:
		for line in f:
			result.add(line.replace('\n', ''))
	return result


# def set_to_file
# parameter_taken : links and file name
# function :
def set_to_file(links, file_name):
	delete_data(file_name)
	for link in sorted(links):
		append_data(file_name, link)
