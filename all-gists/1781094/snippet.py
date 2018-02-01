#!/usr/bin/python

#gypify.py for GYP (http://code.google.com/p/gyp)
#Found @ http://code.google.com/p/gyp/issues/detail?id=82 (Oct 1, 2009)
#Download original @ http://gyp.googlecode.com/issues/attachment?aid=1601673567448205219&name=gypify.py&token=qm9EhXN3mZxrS1pniUgsh5nG6Bs%3A1328804204976

#Attached is a script that converts a set of existing Chromium-dependent
#.sln and .vcproj files to .gyp.  It currently supports executable, shared
#library, static library and build event projects.  The output .gyp file is
#created by:

#1. Building a list of all .vcproj files referenced in the .sln
#2. Outputting a target for each .vcproj that does not already have an
#associated .gyp file. This is determined by (a) looking for a .gyp file
#with the same name and directory as the .vcproj file or (b) looking for a
#.gyp RelativePath entry in the .vcproj file.
#3. Building dependencies based on the analysis of the .sln file.
#4. Generating sources, actions and msvs_props blocks by parsing the .vcproj
#files.

#Feel free to use and/or improve this script however you like.

__author__ = 'magreenblatt@gmail.com (Marshall A. Greenblatt)'

from optparse import OptionParser
import os.path
import posixpath
import re
import string
import sys

# cannot be loaded as a module
if __name__ != "__main__":
    sys.stderr.write('This file cannot be loaded as a module!')
    sys.exit()

def read_file(name, normalize = True):
    """ Read a file. """
    try:
    	name = name.replace("\\", "/")
        f = open(name, 'r')
        # read the data
        data = f.read()
        if normalize:
            # normalize line endings
            data = data.replace("\r\n", "\n")
        return data
    except IOError, (errno, strerror):
        sys.stderr.write('Failed to read file '+ name +': '+strerror)
        raise
    else:
        f.close()
#Fast-Unique list (original named: 'f7(seq)') found @ http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order
def uniq_list_fast(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]

def get_single_value(data, regex):
    """ Return a single regex result. """

    p = re.compile(regex)
    result = p.findall(data)
    if len(result) > 0:
        return result[0]
    return None

def relpath(path, start):
    """ Return a relative version of a path. """

    if not path:
        raise ValueError("no path specified")

    start_list = start.split('\\')
    path_list = path.split('\\')

    # Work out how much of the filepath is shared by start and path.
    i = len(posixpath.commonprefix([start_list, path_list]))

    rel_list = [posixpath.pardir] * (len(start_list)-i) + path_list[i:]
    if not rel_list:
        return posixpath.curdir
    return posixpath.join(*rel_list)
    
# parse command-line options
desc = """
This utility generates GYP files based on Visual Studio project files.
"""

parser = OptionParser(description=desc)
parser.add_option('--sln', dest='slnfile', metavar='FILE',
                  help='source SLN file [required]')
(options, args) = parser.parse_args()

# the SLN file option is required
if options.slnfile is None:
    parser.print_help(sys.stdout)
    sys.exit()

# make sure the SLN file exists
if not os.path.exists(options.slnfile):
    sys.stderr.write('File '+options.slnfile+' does not exist.')
    sys.exit()

# retrieve the SLN file contents
content = read_file(options.slnfile)
projects = {}

# identify the base path for the SLN file
basepath = os.path.dirname(os.path.abspath(options.slnfile))
    
# extract project entries
p = re.compile('Project\("\{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942\}"\)(.*?)EndProject\n',
               re.MULTILINE | re.DOTALL)
list = p.findall(content)
for pdata in list:
    # extract name, location and ID
    p = re.compile('"(.*?)"');
    list2 = p.findall(pdata)
    if len(list2) != 3:
        continue
    
    # remove { } from the ID
    id = list2[2][1:-1]
    
    # extract dependencies
    p = re.compile('\} = \{([A-F0-9\-]{0,})\}')
    list3 = p.findall(pdata)
    
    # identify the absolute path for the project file    
    proj_file = os.path.abspath(os.path.join(basepath, list2[1]))
    
    # identify the absolute path for the GYP file
    gyp_file = os.path.splitext(proj_file)[0] + '.gyp'
    if(not os.path.exists(gyp_file)):
        # no GYP file of the project name exists so
        # interrogate the project file for a GYP dependency
        proj_contents = read_file(proj_file)
        gyp_name = get_single_value(proj_contents, 'RelativePath="(.*)\.gyp"')
        if not gyp_name is None:
            gyp_file = os.path.abspath(os.path.join(os.path.dirname(gyp_file), gyp_name+'.gyp'))
            if(not os.path.exists(gyp_file)):
                gyp_file = None
        else:
            gyp_file = None
    
    # add the project entry
    project = {
        'id' : id,
        'name' : list2[0],
        'proj_file' : proj_file,
        'gyp_file' : gyp_file,
        'depends' : list3
    }
    projects[id] = project
    
# begin GYP output
output = \
"""{
  'variables': {
  },
  'targets': [
"""
    
# create any GYP targets that are missing
for id in projects.keys():
    project = projects[id]
    
    # skip the project if the GYP file already exists
    if(not project['gyp_file'] is None):
        continue

    # Determine the VCPROJ directory
    projpath = os.path.dirname(project['proj_file'])
    
    # Read the VCPROJ file contents
    proj_contents = read_file(project['proj_file'])
    
    # Extract the ConfigurationType value
    config_type = get_single_value(proj_contents, 'ConfigurationType="(.*)"')
    if config_type == '1':
        config_type_str = 'executable'
    elif config_type == '2':
        config_type_str = 'shared_library'
    elif config_type == '4':
        config_type_str = 'static_library'
    elif config_type == '10': # build event
        config_type_str = 'none'
    else:
        config_type_str = ''
    
    # Build the list of dependencies with relative paths
    rel_depends = []
    for depend in project['depends']:
        dep_proj = projects[depend]
        if not dep_proj['gyp_file'] is None:
            dep_gyp_file = relpath(dep_proj['gyp_file'], basepath)+':'
        else:
            dep_gyp_file = ''
        rel_depends.append(dep_gyp_file+dep_proj['name'])
    rel_depends.sort()
     
    # Extract the InheritedPropertySheets value
    prop_sheets = get_single_value(proj_contents, 'InheritedPropertySheets="(.*)"')
    rel_prop_sheets = []
    if not prop_sheets is None:
        # Build the list of property sheets with relative paths
        prop_sheets = string.split(prop_sheets, ';')
        for prop_sheet in prop_sheets:
            if prop_sheet[0] == '$':
                # Skip property sheets beginning with variable names
                continue
            rel_prop_sheets.append(relpath(os.path.abspath(os.path.join(projpath, prop_sheet)), basepath))
        rel_prop_sheets.sort()
        
    # Extract the RelativePath values
    p = re.compile('RelativePath="(.*)"')
    paths = p.findall(proj_contents)
    rel_paths = []
    # Build the list of files with relative paths
    for path in paths:
        if path[0] == '$':
            # Paths beginning with variable names are not converted
            rel_path = path.replace('\\', '/')
        else:
            rel_path = relpath(os.path.abspath(os.path.join(projpath, path)), basepath)
        rel_paths.append(rel_path)
    rel_paths.sort()
        
    output += \
        "    {\n"+\
        "      'target_name': '"+project['name']+"',\n"+\
        "      'type': '"+config_type_str+"',\n"+\
        "      'msvs_guid': '"+project['id']+"',\n"+\
        "      'dependencies': [\n"
    
    for depend in rel_depends:
        output += "        '"+depend+"',\n"
    
    output += "      ],\n"
    
    if config_type_str == 'none':
        # action project
        output += \
            "      'actions': [\n"+\
            "        {\n"+\
            "          'action_name': '"+project['name']+"',\n"+\
            "          'msvs_cygwin_shell': 0,\n"+\
            "          'inputs': [\n"
            
        for path in rel_paths:
            output += "            '"+path+"',\n"
        
        output += \
            "          ],\n"+\
            "          'outputs': [\n"
            
        for path in rel_paths:
            output += "            '"+path+".output',\n"
        
        output += \
            "          ],\n"+\
            "          'action': ['', '<@(_inputs)'],\n"+\
            "        },\n"+\
            "      ],\n"            
    else:
        # sources project
        output += \
            "      'defines': [\n"+\
            "      ],\n"+\
            "      'include_dirs': [\n"

#Begin - Potential Header directories for GCC '-I' switch - Richard Joseph, 27/02/12
	rel_paths_no_file = []
	for path in rel_paths:
            rel_paths_no_file.append(os.path.dirname(path))

	uniq_list_paths = uniq_list_fast(set(rel_paths_no_file))

        for header_path_dir in uniq_list_paths:
            output += "        '"+header_path_dir+"',\n" 
#End - Potential Header directories for GCC '-I' switch          
        
	output += \
            "      ],\n"+\
            "      'sources': [\n"

        for path in rel_paths:
            output += "        '"+path+"',\n"
            
        output += \
            "      ],\n"+\
            "      'conditions': [\n"+\
            "        ['OS==\"win\"', {\n"+\
            "          'defines': [\n"+\
            "          ],\n"+\
            "          'msvs_props': [\n"
            
        for prop_sheet in rel_prop_sheets:
            output += "            '"+prop_sheet+"',\n"
        
        output += \
            "          ],\n"+\
            "        }],\n"+\
            "      ],\n"
    
    output += "    },\n"

# end GYP output
output += \
"""
  ]
}
"""

print output
