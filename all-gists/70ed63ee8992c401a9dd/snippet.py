# add this to your vimrc
#let g:ycm_global_ycm_extra_conf = "~/.vim/.ycm_extra_conf_openframeworks.py"


# Partially stolen from https://bitbucket.org/mblum/libgp/src/2537ea7329ef/.ycm_extra_conf.py
import os
import ycm_core

# These are the compilation flags that will be used in case there's no
# compilation database set (by default, one is not set).
# CHANGE THIS LIST OF FLAGS. YES, THIS IS THE DROID YOU HAVE BEEN LOOKING FOR.
flags = [
	'-c',
	'-O3',
	'-Wall',
	'-march=native',
	'-mtune=native',
	'-DOF_USING_GTK',
	'-DOF_USING_GTK',
	'-DOF_USING_MPG123',
    # THIS IS IMPORTANT! Without a "-std=<something>" flag, clang won't know which
    # language to use when compiling headers. So it will guess. Badly. So C++
    # headers will be compiled as C headers. You don't want that so ALWAYS specify
    # a "-std=<something>".
    # For a C project, you would set this to something like 'c99' instead of
    # 'c++11'.
    '-std=c++11',
    # ...and the same thing goes for the magic -x option which specifies the
    # language that the files to be compiled are written in. This is mostly
    # relevant for c++ headers.
    # For a C project, you would set this to 'c' instead of 'c++'.
    '-x', 'c++',
    # This path will only work on OS X, but extra paths that don't exist are not
    # harmful
    #'-isystem', '/System/Library/Frameworks/Python.framework/Headers',
    '-isystem', '/usr/local/include',
    #'-isystem', '/usr/local/include/eigen3',
	'-I./src',
	'-I./data',
	'-I./data/model',
	'-I/usr/include/cairo',
	'-I/usr/include/glib-2.0',
	'-I/usr/lib/x86_64-linux-gnu/glib-2.0/include',
	'-I/usr/include/pixman-1',
	'-I/usr/include/freetype2',
	'-I/usr/include/libpng12',
	'-I/usr/include/gstreamer-1.0',
	'-I/usr/include/alsa',
	'-I/usr/include/libdrm',
	'-I/usr/include/GL',
	'-I/usr/include/gtk-3.0',
	'-I/usr/include/atk-1.0',
	'-I/usr/include/at-spi2-atk/2.0',
	'-I/usr/include/pango-1.0',
	'-I/usr/include/gio-unix-2.0/',
	'-I/usr/include/gdk-pixbuf-2.0',
	'-I/usr/include/harfbuzz',
	'-I../../../libs/cairo/include',
	'-I../../../libs/cairo/include/pixman-1',
	'-I../../../libs/cairo/include/cairo',
	'-I../../../libs/cairo/include/libpng15',
	'-I../../../libs/fmodex/include',
	'-I../../../libs/glfw/include',
	'-I../../../libs/glfw/include/GLFW',
	'-I../../../libs/kiss/include',
	'-I../../../libs/openssl/include',
	'-I../../../libs/openssl/include/openssl',
	'-I../../../libs/poco/include',
	'-I../../../libs/rtAudio/include',
	'-I../../../libs/tess2/include',
	'-I../../../libs/openFrameworks',
	'-I../../../libs/openFrameworks/sound',
	'-I../../../libs/openFrameworks/utils',
	'-I../../../libs/openFrameworks/communication',
	'-I../../../libs/openFrameworks/events',
	'-I../../../libs/openFrameworks/types',
	'-I../../../libs/openFrameworks/app',
	'-I../../../libs/openFrameworks/gl',
	'-I../../../libs/openFrameworks/video',
	'-I../../../libs/openFrameworks/math',
	'-I../../../libs/openFrameworks/3d',
	'-I../../../libs/openFrameworks/graphics',
    '-I.'
]

addons = [
	'-I../../../addons/ofxOpenCv/src',
	'-I../../../addons/ofxOpenCv/libs',
	'-I../../../addons/ofxOpenCv/libs/opencv',
	'-I../../../addons/ofxOpenCv/libs/opencv/include',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2/features2d',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2/core',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2/gpu',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2/ts',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2/contrib',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2/flann',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2/objdetect',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2/highgui',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2/legacy',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2/imgproc',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2/video',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2/ml',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2/calib3d',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv',
	'-I../../../addons/ofxOpenCv/libs/opencv/lib',
	'-I../../../addons/ofxOpenCv/libs/opencv/lib/osx',
	'-I../../../addons/ofxOpenCv/libs/opencv/lib/win_cb',
	'-I../../../addons/ofxOpenCv/libs/opencv/lib/ios',
	'-I../../../addons/ofxOpenCv/libs/opencv/lib/linux',
	'-I../../../addons/ofxOpenCv/libs/opencv/lib/vs',
	'-I../../../addons/ofxOpenCv/libs/opencv/lib/linuxarmv6l',
	'-I../../../addons/ofxOpenCv/libs/opencv/lib/android',
	'-I../../../addons/ofxOpenCv/libs/opencv/lib/android/armeabi',
	'-I../../../addons/ofxOpenCv/libs/opencv/lib/android/armeabi-v7a',
	'-I../../../addons/ofxOpenCv/libs/opencv/lib/linuxarmv7l',
	'-I../../../addons/ofxOpenCv/libs/opencv/lib/linux64',
	'-I../../../addons/ofxOpenCv/libs/opencv/include',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2/features2d',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2/core',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2/gpu',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2/ts',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2/contrib',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2/flann',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2/objdetect',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2/highgui',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2/legacy',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2/imgproc',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2/video',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2/ml',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv2/calib3d',
	'-I../../../addons/ofxOpenCv/libs/opencv/include/opencv',
	'-I../../../addons/ofxCv/src',
	'-I../../../addons/ofxCv/libs',
	'-I../../../addons/ofxCv/libs/CLD',
	'-I../../../addons/ofxCv/libs/CLD/include',
	'-I../../../addons/ofxCv/libs/CLD/include/CLD',
	'-I../../../addons/ofxCv/libs/CLD/src',
	'-I../../../addons/ofxCv/libs/ofxCv',
	'-I../../../addons/ofxCv/libs/ofxCv/include',
	'-I../../../addons/ofxCv/libs/ofxCv/include/ofxCv',
	'-I../../../addons/ofxCv/libs/ofxCv/src',
	'-I../../../addons/ofxCv/libs/CLD/include',
	'-I../../../addons/ofxCv/libs/CLD/include/CLD',
	'-I../../../addons/ofxCv/libs/ofxCv/include',
	'-I../../../addons/ofxCv/libs/ofxCv/include/ofxCv',
	'-I../../../addons/ofxFaceTracker/src',
	'-I../../../addons/ofxFaceTracker/libs',
	'-I../../../addons/ofxFaceTracker/libs/FaceTracker',
	'-I../../../addons/ofxFaceTracker/libs/FaceTracker/include',
	'-I../../../addons/ofxFaceTracker/libs/FaceTracker/include/FaceTracker',
	'-I../../../addons/ofxFaceTracker/libs/FaceTracker/src',
	'-I../../../addons/ofxFaceTracker/libs/FaceTracker/src/lib',
	'-I../../../addons/ofxFaceTracker/libs/FaceTracker/model',
	'-I../../../addons/ofxFaceTracker/libs/FaceTracker/include',
	'-I../../../addons/ofxFaceTracker/libs/FaceTracker/include/FaceTracker',
	'-pthread',
	'-D_REENTRANT'
]

#concat flags and addons
flags += addons

# Set this to the absolute path to the folder (NOT the file!) containing the
# compile_commands.json file to use that instead of 'flags'. See here for
# more details: http://clang.llvm.org/docs/JSONCompilationDatabase.html
#
# Most projects will NOT need to set this to anything; you can just change the
# 'flags' list of compilation flags. Notice that YCM itself uses that approach.
compilation_database_folder = ''

if compilation_database_folder:
  database = ycm_core.CompilationDatabase( compilation_database_folder )
else:
  database = None


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


def FlagsForFile( filename ):
  if database:
    # Bear in mind that compilation_info.compiler_flags_ does NOT return a
    # python list, but a "list-like" StringVec object
    compilation_info = database.GetCompilationInfoForFile( filename )
    final_flags = MakeRelativePathsInFlagsAbsolute(
      compilation_info.compiler_flags_,
      compilation_info.compiler_working_dir_ )
  else:
    relative_to = ''#DirectoryOfThisScript()
    final_flags = MakeRelativePathsInFlagsAbsolute( flags, relative_to )

  return {
    'flags': final_flags,
    'do_cache': True
  }
