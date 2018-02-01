# extract_filetype_from_zip.py
# A simple script to extract all files of a certain filetype from many .zip files
# * Requires Python installed on local computer
VERSION = 0.1
# 
# Place this file in the folder where you have all your zipfiles.
# Example use:
# - To extract only PDFs: extract_filetype('.pdf', '/folder') where folder (with the /) is the dir you store your zipfiles
# - 2nd argument is optional (defaults to root)

import zipfile
import os


# to do: target directory for extraction, zip file passwords
def extract_filetype(filetype, directory='root'):
    "Extracts files of filetype from a directory of zipfiles."
    if directory == 'root':
        working_dir = './'
    else:
        working_dir = '.' + str(directory) + '/'
    zipfile_list = zipfile_array(working_dir)

    if zipfile_list:
        print "Working to extract " + str(filetype) + " files from " + str(directory) + "...\n"
        for zips in zipfile_list:
            print "  Found " + str(len(zips)) + " .zip files \n"
            for f in zips:
                with zipfile.ZipFile(f) as curr_zip:
                    for target_filepath in curr_zip.namelist():
                        if target_filepath.endswith(filetype) and not target_filepath.startswith('__MACOSX/'):
                            print "  Extracting... " + str(target_filepath)
                            curr_zip.extract(target_filepath)
        print "\nExtraction complete."
    else:
        print "No .zip files to extract from " + str(directory)


def zipfile_array(directory): # this needs fixing to avoid empty arrays
    "Creates array of zipfile paths and names in the directory."
    return [[os.path.join(root, name) for name in files if name.endswith('zip')] for root, dirs, files in os.walk(directory)]


extract_filetype('.pdf', '/zip')
# print filename_array('./zip')
