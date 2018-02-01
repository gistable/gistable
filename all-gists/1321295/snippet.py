#
# SCons builder for gcc's precompiled headers
# Copyright (C) 2006  Tim Blechmann (C) 2011 Pedro Larroy
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

# 1.2
#
# 09-11-2011 Pedro Larroy: Fixed dependency emitter not working with variant dir
# 07-09-2012 Pedro Larroy: Create the resulting pch on the variant directory,
#   the variant dir should be added to the includes, before any of the other
#   local includes for the compiler to search the pch file on the build directory
#   that we just created. In doubt execute 'strace -f g++ ...' to check that it
#   opens the correct pch. 
#
# FIXME: the original precompiled header has to be set
#   in the environment as
#   env['precompiled_header'], this should be fixed
#
#
# Example usage:
#  src_variant_dir = 'build/release'
#  includes = [
#    Dir(src_variant_dir),
#    ... other includes ...
#  ]
#  ... set includes in environment ...
#  env['precompiled_header'] = File('src/common/includes/all.h')
#  env['Gch'] = env.Gch(target='common/includes/all.h.gch', source=env['precompiled_header'])



import SCons.Action
import SCons.Builder
import SCons.Scanner.C
import SCons.Util
import SCons.Script
import os
import functools

SCons.Script.EnsureSConsVersion(0,96,92)

GchAction = SCons.Action.Action('$GCHCOM', '$GCHCOMSTR')
GchShAction = SCons.Action.Action('$GCHSHCOM', '$GCHSHCOMSTR')

def gen_suffix(env, sources):
    return sources[0].get_suffix() + env['GCHSUFFIX']

GchShBuilder = SCons.Builder.Builder(action = GchShAction,
                                     source_scanner = SCons.Scanner.C.CScanner(),
                                     suffix = gen_suffix)

GchBuilder = SCons.Builder.Builder(action = GchAction,
                                   source_scanner = SCons.Scanner.C.CScanner(),
                                   suffix = gen_suffix)

def header_path(node):
    h_path = node.abspath
    idx = h_path.rfind('.gch')
    if idx != -1:
        h_path = h_path[0:idx]
        if not os.path.isfile(h_path):
            raise SCons.Errors.StopError("can't find header file: {0}".format(h_path))
        return h_path

    else:
        raise SCons.Errors.StopError("{0} file doesn't have .gch extension".format(h_path))

def pch_emitter(pch_env_key, target, source, env):
#    print 'target', target[0].str_for_display(), 'source', str(source[0])
#    print 'target'
#    print map(lambda x: x.str_for_display(), target)
#    print 'source'
#    print map(lambda x: x.str_for_display(), source)
#    print 'env:'
#    print env.get(pch_env_key)
#    print type(env.get(pch_env_key))
#    print
    SCons.Defaults.StaticObjectEmitter( target, source, env )
    scanner = SCons.Scanner.C.CScanner()
    path = scanner.path(env)

    deps = scanner(source[0], env, path)
    if env.get(pch_env_key):
        h_path = env['precompiled_header'].abspath
        #print 'h_path', h_path
        #print env['Gch'].abspath
        #print map(lambda x: x.str_for_display(), deps)
        #if h_path in [x.abspath for x in deps]:
        for i in [x.abspath for x in deps]:
            #print '|{0}|{1}|'.format(i, h_path)
            if i == h_path:
                if 'explain' in env.GetOption('debug'):
                    print 'Found dep. on pch: ', source[0], ' -> ', env[pch_env_key]
                env.Depends(target, env[pch_env_key])


    return (target, source)

def generate(env):
    """
    Add builders and construction variables for the Gch builder.
    """
    env.Append(BUILDERS = {
        'gch': env.Builder(
        action = GchAction,
        suffix = 'gch',
        target_factory = env.fs.File,
        ),
        'gchsh': env.Builder(
        action = GchShAction,
        target_factory = env.fs.File,
        ),
        })

    try:
        bld = env['BUILDERS']['Gch']
        bldsh = env['BUILDERS']['GchSh']
    except KeyError:
        bld = GchBuilder
        bldsh = GchShBuilder
        env['BUILDERS']['Gch'] = bld
        env['BUILDERS']['GchSh'] = bldsh

    env['GCHCOM']     = '$CXX -Wall -o $TARGET -x c++-header -c $CXXFLAGS $CCFLAGS $_CCCOMCOM $SOURCE'
    env['GCHSHCOM']   = '$CXX -o $TARGET -x c++-header -c $SHCXXFLAGS $CCFLAGS $_CCCOMCOM $SOURCE'
    env['GCHSUFFIX']  = '.gch'

    for suffix in SCons.Util.Split('.c .C .cc .cxx .cpp .c++'):
        static_pch_emitter = functools.partial(pch_emitter, 'Gch')
        env['BUILDERS']['StaticObject'].add_emitter( suffix, static_pch_emitter )
        shared_pch_emitter = functools.partial(pch_emitter, 'GchSh')
        env['BUILDERS']['SharedObject'].add_emitter( suffix, shared_pch_emitter )


def exists(env):
    return env.Detect('g++')
