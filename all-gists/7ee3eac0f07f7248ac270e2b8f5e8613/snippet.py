# import
import os
from os import path, listdir as list_dir, rename as move
from os.path import isdir as is_dir, isfile as is_file
from pprint import pprint
import shutil

# global variables
#==================

#list directory content
base_dowload_directory = r"C:\Users\lenin\Downloads"

# file type and location mapping
target_files_to_move = {
	'installer': {
		'location': r"D:\software\001 windows",
		'types': ['exe', 'msi'],
	}, 
	'ebook': {
		'location': r"D:\lenin\books",
		'types': ['pdf'],
	},
	'document': {
		'location': r"D:\lenin\documents",
		'types': ['doc', 'docx'],
	},
	'audio': {
		'location': r"D:\media\audio",
		'types': ['mp3', 'wav'],
	},
	'video': {
		'location': r"D:\media\videos",
		'types': ['mp4', 'avi', 'mov'],
	},
}


# global functions
#==================

def recursively_check( input_path ):
	if is_file( input_path ):
		try_to_move( input_path )

	elif is_dir( input_path ):
		directory_contents = list_dir( input_path )

		for file in directory_contents:
			file_path = path.join( input_path, file )
			recursively_check( file_path )


def try_to_move(file_path):
	file_type = file_path.rsplit( '.', 1 )[-1]

	for key, target in target_files_to_move.items():
		if file_type in target['types']:
			move_file( file_path, target['location'] )

			
def move_file(source_file, destination_dir):
	file_name_with_type = os.path.basename(source_file)	
	file_name, file_type = file_name_with_type.rsplit( '.', 1 )

	destination_file = path.join( destination_dir, file_name_with_type )

	if is_file( destination_file ): # means file exist, so rename it
		destination_file = path.join( destination_dir, file_name + ' - copy 2.' + file_type )

	if is_file( source_file ):
		shutil.move( source_file, destination_file )


# init the program
recursively_check( base_dowload_directory )
	