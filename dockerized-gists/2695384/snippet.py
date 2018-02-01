#!/usr/bin/env python
import sys, os.path, fnmatch, re, shlex, subprocess

def searchMakefile(where, visit, recursive):
    if not os.path.exists(where):
        return False
    if recursive:
        for root, dirname, filenames in os.walk(where):
            for filename in fnmatch.filter(filenames, 'Makefile*'):
                if visit(os.path.join(root, filename)):
                    return os.path.join(root, filename)
    else:
        standardMakefile = os.path.join(where, 'Makefile')
        if os.path.isfile(standardMakefile) and visit(standardMakefile):
            return standardMakefile
        for makefile in fnmatch.filter(os.listdir(where), 'Makefile*'):
            if visit(os.path.join(where, makefile)):
                return os.path.join(where, makefile)

def searchMakefileContainingFilename(where, filename):
    # FIXME: Using only the base name can lead to false positives if two files with the
    # same name have different build options (i.e. appearing in different Makefiles).
    # We should search for the relative path between the pro file and the source file instead.
    findBasename = re.compile('[/\s]' + re.escape(os.path.basename(filename)))
    def containsSource(makefile):
        for line in open(makefile):
            if findBasename.search(line):
                return True
    return searchMakefile(where, containsSource, recursive = True)

def isBuildDirOfSource(buildDir, sourceFile):
    # Assume it's a build dir of our file if it contains a Makefile that was
    # generated using a .pro file placed in a parent directory of our source file.
    def checkQmakeHeader(makefile):
        prog = re.compile('# Project:\s*(.*)')
        for line in open(makefile):
            if not line.startswith('#'):
                return False
            m = prog.match(line)
            if m:
                proFilePath = m.group(1)
                if not os.path.isabs(proFilePath):
                    proFprintilePath = os.path.join(os.path.dirname(makefile), proFilePath)
                proFileDir = os.path.realpath(os.path.dirname(proFilePath))
                sourceDir = os.path.realpath(os.path.dirname(sourceFile))
                return sourceDir.startswith(proFileDir)
    return searchMakefile(buildDir, checkQmakeHeader, recursive = False)

def extractRelevantFlags(flags):
    # Keep flags that affect the preprocessor and could fail the compile.
    relevantFlags = re.findall('-fPIC|-fPIE|-include [^\s]+', flags)
    return ' '.join(relevantFlags)

def removeVarRef(flags):
    return re.sub('\s?\$\([^\)]*\)', '', flags) if flags else ''

def getOptions(makefile, sourceFile, onlyRelevant=True):
    makefileDir = os.path.dirname(os.path.realpath(makefile))
    cmdProg = re.compile('^CXX\s*=\s*(.*)')
    definesProg = re.compile('^DEFINES\s*=\s*(.*)')
    incpathProg = re.compile('^INCPATH\s*=\s*(.*)')
    flagsProg = re.compile('^CXXFLAGS\s*=\s*(.*)')
    cmd = None
    defines = None
    incpath = None
    relevantFlags = None
    for line in open(makefile):
        cmdMatch = cmdProg.match(line)
        definesMatch = definesProg.match(line)
        incpathMatch = incpathProg.match(line)
        flagsMatch = flagsProg.match(line)
        if cmdMatch:
            cmd = cmdMatch.group(1)
        elif definesMatch:
            defines = definesMatch.group(1)
        elif incpathMatch:
            incpath = re.sub('-I([^/])', '-I' + makefileDir + '/\\1', incpathMatch.group(1))
            # Explicitely include config.h for WebKit headers which expect their including cpp file to do so.
            if "/webkit/" in sourceFile and sourceFile.endswith('.h'):
                incpath += ' -include config.h'
        elif flagsMatch:
            relevantFlags = removeVarRef(flagsMatch.group(1))
            if onlyRelevant:
                relevantFlags = extractRelevantFlags(relevantFlags)
        if cmd != None and defines != None and incpath != None and relevantFlags != None:
            return cmd, shlex.split(relevantFlags + ' ' + defines + ' ' + incpath)

def makefileForSource(buildDirs, sourceFile):
    makefile = None
    for buildDir in buildDirs:
        # Heuristic to fast skip build dirs unrelated to this source file.
        if not isBuildDirOfSource(buildDir, sourceFile):
            continue
        makefile = searchMakefileContainingFilename(buildDir, sourceFile)
        if makefile:
            break
    if not makefile:
        sys.stderr.write('Options for [%s] could not be found. Make sure that you have an existing build.\n' % sourceFile)
        sys.exit(-1)
    return makefile

def sublimeClangArguments(makefile, sourceFile):
    # Extract the options from the makefile that lists our source file somewhere as a dependency.
    cmd, options = getOptions(makefile, sourceFile)
    print(' '.join(options))

def build(makefile, sourceFile):
    # Extract the options from the makefile that lists our source file somewhere as a dependency.
    cmd, args = getOptions(makefile, sourceFile, onlyRelevant=False)
    args += ('-fsyntax-only', sourceFile)
    sys.exit(subprocess.call([cmd,] + args))

if __name__ == "__main__":
    if sys.argv[1] != '-b':
        buildDirs = sys.argv[1:-1]
        sourceFile = sys.argv[-1]
        sublimeClangArguments(makefileForSource(buildDirs, sourceFile), sourceFile)
    else:
        buildDirs = sys.argv[2:-1]
        sourceFile = sys.argv[-1]
        build(makefileForSource(buildDirs, sourceFile), sourceFile)
