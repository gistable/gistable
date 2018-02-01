# credit: http://news.ycombinator.com/item?id=1543915

# in ipythonrc:
# execfile copy_and_paste.py

def copy(data):
    from subprocess import Popen, PIPE
    Popen(["xclip", "-selection", "clipboard"], stdin=PIPE).communicate(str(data))

def paste():
    from subprocess import Popen, PIPE
    return Popen(["xclip", "-selection", "clipboard", "-o"], stdout=PIPE).communicate()[0]

def ep():
    return eval(paste())
