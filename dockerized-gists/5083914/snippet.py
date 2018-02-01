#!/user/bin/env python

import json
import sys
from types import *

def cpp_type(value):
    if type(value) is IntType:
        return 'int'
    elif type(value) is FloatType:
        return 'double'
    elif type(value) is BooleanType:
        return 'bool'
    elif type(value) is UnicodeType:
        return 'std::string'
    elif type(value) is ListType:
        return 'std::vector'
    else:
        pass

def generate_variable_info(data):
    includes = []
    varinfo = []
    for k, v in data.iteritems():
        if type(v) is ListType:
            if not 'vector' in includes:
                includes.append('vector')
            varinfo.append((cpp_type(v), cpp_type(v[0]), k))
        else:
            typename = cpp_type(v)
            varinfo.append((typename, k))
        if 'string' in typename and not 'string' in includes:
            includes.append('string')
    return includes, varinfo

def generate_header(classname, includes, varinfo):
    header = open(classname + '.h', 'wb')
    header.write('//\n// {}.h\n'.format(classname))
    header.write('//\n// -- generated class for jsoncpp\n//\n')
    header.write('#ifndef __{}_H__\n'.format(classname.upper()))
    header.write('#define __{}_H__\n'.format(classname.upper()))
    for i in range(len(includes)):
        header.write('#include <{}>\n'.format(includes[i]))
    header.write('class {}\n'.format(classname))
    header.write('{\n')
    header.write('public:\n')
    for info in varinfo:
        if len(info) == 3:
            header.write('\t{}<{}> {};\n'.format(info[0], info[1], info[2]))
        else:
            header.write('\t{} {};\n'.format(info[0], info[1]))
    header.write('\t{}(const char *json);\n'.format(classname))
    header.write('};\n')
    header.write('#endif')

# jsoncpp type methods
type_methods = {'int':'asInt', 'bool':'asBool', 'double':'asDouble', 'std::string':'asString'}
def assign_statement(t, v):
    return '{} = root[\"{}\"].{}();'.format(v, v, type_methods[t])

def array2vector_statements(elemt, var):
    #print info
    stats = []
    temp = 't_'+ var
    stats.append('// {}'.format(var))
    stats.append('const Json::Value {} = root[\"{}\"];'.format(temp, var))
    stats.append('for (int i = 0; i < {}.size(); ++i)'.format(temp))
    stats.append('\t{}.push_back({}[i].{}());'.format(var, temp, type_methods[elemt]))
    return stats

def generate_constructor(classname, varinfo, f):
    f.write('// constructor\n')
    f.write('{}::{}(const char *json)\n'.format(classname, classname))
    f.write('{\n')
    f.write('\tJson::Value root;\n')
    f.write('\tJson::Reader reader;\n')
    f.write('\tbool parsingSuccessful = reader.parse(json, root);\n')
    f.write('\tif (!parsingSuccessful)\n')
    f.write('\t{\n')
    f.write('\t\t// error\n')
    f.write('\t\treturn;\n')
    f.write('\t}\n\n')
    for info in varinfo:
        if len(info) == 2:
            f.write('\t'+assign_statement(info[0], info[1])+'\n')
        elif 'vector' in info[0]:
            for line in array2vector_statements(info[1], info[2]):
                f.write('\t'+line+'\n')
    f.write('}\n')

def generate_source(classname, varinfo):
    source = open(classname + '.cpp', 'wb')
    source.write('//\n// {}.cpp\n'.format(classname))
    source.write('//\n// -- generated class for jsoncpp\n//\n')
    source.write('#include \"{}.h\"\n'.format(classname))
    source.write('#include <json/json.h> // jsoncpp\n\n')
    generate_constructor(classname, varinfo, source)

def main(filename):
    classname = filename.split('.')[0]
    try:
        with open(filename) as f:
            content = f.read()
    except IOError:
        print "Can't open/read file."
        return
    data = json.loads(content)
    includes, varinfo = generate_variable_info(data)
    varinfo.sort()
    generate_header(classname, includes, varinfo)
    generate_source(classname, varinfo)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: {} <json file>'.format(sys.argv[0])
        sys.exit(1)
    main(sys.argv[1])
