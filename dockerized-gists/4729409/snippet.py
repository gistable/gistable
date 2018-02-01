from subprocess import Popen
import os, subprocess

def parseEnv(envoutput):
    handle_line = lambda l: tuple(l.rstrip().split("=", 1))
    pairs = map(handle_line, envoutput)
    valid_pairs = filter(lambda x: len(x) == 2, pairs)
    valid_pairs = [(x[0].upper(), x[1]) for x in valid_pairs]
    return dict(valid_pairs)

def overrideEnv(newenv):
    old = os.environ.copy()
    removed = set(old) - set(newenv)
    for k in newenv.keys():
        os.environ[k] = newenv[k]
    for k in removed:
        os.environ.pop(k)
    return old

def setupVSEnv(vsver):
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess._subprocess.STARTF_USESHOWWINDOW
    cmd = r'cmd /s /c ""%VS{vsver}COMNTOOLS%vsvars32.bat" & set"'.format(**locals())
    ret = Popen(cmd, startupinfo=si, 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE)
    output = ret.communicate()[0]
    output = output.split("\r\n")
    old = overrideEnv(parseEnv(output))
    return old

