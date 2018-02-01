import subprocess
import sys, os

def pull(dir):
    print dir, ':'
    os.chdir(dir)
    subprocess.call(['git', 'pull'])
    os.chdir('..')

map(pull, filter(os.path.isdir, os.listdir('.')))