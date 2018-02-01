# .ycm_extra_conf.py for vim source code. This should work after running './configure
import os, re


def create_flags():
    rv = [
        '-Wall',
        '-Wextra',
        '-std=c89',
        '-x',
        'c',
        '-iquote',
        'proto'
    ]

    flags_file = './src/auto/pathdef.c'
    if os.path.exists(flags_file):
        flags_re = re.compile(
            r'^char_u\s*\*all_cflags\s*\=\s*\(char_u\s*\*\)\"(.+)\";\s*$',
            re.MULTILINE)
        with open(flags_file,'r') as fobj:
            rv += []
            for f in flags_re.findall(fobj.read())[0].split():
                if f in ['-c', 'gcc', '-Iproto', '-I.']: continue
                if f.startswith('-I'): rv += ['-isystem', f[2:]]
                else: rv.append(f)
    return rv


flags = create_flags()

database = None

SOURCE_EXTENSIONS = [ '.cpp', '.cxx', '.cc', '.c', '.m', '.mm' ]

def DirectoryOfThisScript():
    return os.path.dirname( os.path.abspath( __file__ ) )


def MakeRelativePathsInFlagsAbsolute( flags, working_directory ):
    if not working_directory:
        return list( flags )
    new_flags = []
    make_next_absolute = False
    path_flags = [ '-isystem', '-I', '-iquote', '--sysroot=' ]
    for flag in flags:
        new_flag = flag

        if make_next_absolute:
            make_next_absolute = False
            if not flag.startswith( '/' ):
                new_flag = os.path.join( working_directory, flag )

        for path_flag in path_flags:
            if flag == path_flag:
                make_next_absolute = True
                break

            if flag.startswith( path_flag ):
                path = flag[ len( path_flag ): ]
                new_flag = path_flag + os.path.join( working_directory, path )
                break

        if new_flag:
            new_flags.append( new_flag )
    return new_flags


def FlagsForFile( filename, **kwargs ):
    relative_to = DirectoryOfThisScript()
    final_flags = MakeRelativePathsInFlagsAbsolute( flags, relative_to )

    return {
      'flags': final_flags,
      'do_cache': True
    }
