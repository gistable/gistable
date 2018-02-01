#!/usr/bin/env python

import os, random, subprocess, sys

HAS_VENV = bool(subprocess.Popen(['which','virtualenv'], stdout=subprocess.PIPE).communicate()[0])
if not HAS_VENV:
    print "virtualenv is required to run this script. Please install it with\n  easy_install virtualenv\n\nor\n\n  pip virtualenv"
    sys.exit(1)

HAS_VENVW = bool(subprocess.Popen(['which','virtualenvwrapper.sh'], stdout=subprocess.PIPE).communicate()[0])
if not HAS_VENVW:
    print "virtualenvwrapper is required to run this script. Please install it with\n  easy_install virtualenvwrapper\n\nor\n\n  pip virtualenvwrapper"
    sys.exit(1)

CHARS = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
BLACKLIST = (
    'jquery',
    '.tar.gz',
    'admin/css',
    'admin/img',
    'admin/js',
    '/.git/',
    '.svn',
    '.hg',
)

def replace(repl, text):
    text = text.replace('/gitignore', '/.gitignore')
    for key, value in repl.iteritems():
        text = text.replace('$$$$%s$$$$' % (key,), value)
    return text



def main(repl, dest, templ_dir):
    try:
        os.makedirs(dest)
    except OSError:
        pass
    
    for root, dirs, files in os.walk(templ_dir):
        for filename in files:
            source_fn = os.path.join(root, filename)
            dest_fn = replace(repl, os.path.join(dest, root.replace(templ_dir, ''), replace(repl, filename)))
            try:
                os.makedirs(os.path.dirname(dest_fn))
            except OSError:
                pass
            print 'Copying %s to %s' % (source_fn, dest_fn)
            should_replace = True
            for bl_item in BLACKLIST:
                if bl_item in dest_fn:
                    should_replace = False
            data = open(source_fn, 'r').read()
            if should_replace:
                data = replace(repl, data)
            open(dest_fn, 'w').write(data)
            os.chmod(dest_fn, os.stat(source_fn)[0])
    
    print "Making the virtual environment (%s)..." % repl['virtenv']
    create_env_cmds = [
        'source virtualenvwrapper.sh', 
        'cd %s' % dest,
        'mkvirtualenv --no-site-packages --distribute %s' % repl['virtenv'],
        'easy_install pip'
    ]
    create_pa_cmd = [
        'source virtualenvwrapper.sh',
        'cat > $WORKON_HOME/%s/bin/postactivate '\
        '<<END\n#!/bin/bash/\ncd %s\nEND\n'\
        'chmod +x $WORKON_HOME/%s/bin/postactivate' % (repl['virtenv'], dest,repl['virtenv'])
    ]
    subprocess.call([';'.join(create_env_cmds)], env=os.environ, executable='/bin/bash', shell=True)
    subprocess.call([';'.join(create_pa_cmd)], env=os.environ, executable='/bin/bash', shell=True)
    
    print "Installing requirements..."
    subprocess.call(['$WORKON_HOME/%s/bin/pip install -r %s' \
        % (repl['virtenv'], os.path.join(dest, 'setup', 'requirements.txt'))],
        env=os.environ, executable='/bin/bash', shell=True, cwd=dest)

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    
    parser.add_option("-a", "--admin", dest="name", default=os.getlogin(), help="The name of the administrator.")
    parser.add_option("-e", "--email", dest="email_address", help="The email address of the administrator.")
    parser.add_option("-n", "--name", dest="project_name", help="The name of the project.")
    parser.add_option("-v", "--virtenv", dest="virtenv", help="The name of the virtualenv.")
    parser.add_option("-d", "--dest", dest="destination", help="Where to put the new project.")
    parser.add_option("-t", "--template", dest="template", help="The project template to use as a basis for the new project.")
    (options, args) = parser.parse_args()
    
    repl = {
        'EMAIL_ADDRESS':None, 
        'PROJECT_NAME':None,
        'NAME':None,}
    dest_dir = None
    templ_dir = None
    
    cur_user = os.getlogin()
    
    if options.project_name:
        repl['PROJECT_NAME'] = options.project_name
    elif len(args) > 0:
        repl['PROJECT_NAME'] = args[0]
    
    while not repl['PROJECT_NAME']:
        repl['PROJECT_NAME'] = raw_input('Project name: ')
    
    if options.name:
        repl['NAME'] = options.name
    
    while not repl['NAME']:
        repl['NAME'] = raw_input('Administrator name  [%s]: ' % cur_user) or cur_user
    
    if options.email_address:
        repl['EMAIL_ADDRESS'] = options.email_address
    
    while not repl['EMAIL_ADDRESS']:
        repl['EMAIL_ADDRESS'] = raw_input('Administrator e-mail address: ')
    
    repl['SECRET_KEY'] = ''.join([random.choice(CHARS) for i in xrange(50)])
    
    if options.destination:
        dest_dir = options.destination
    
    while not dest_dir:
        dest_dir = raw_input('Destination directory (currently at %s): ' % (os.getcwd(),)) or os.getcwd()
    dest_dir =  os.path.realpath(os.path.expanduser(dest_dir))
    dest = os.path.join(dest_dir, repl['PROJECT_NAME'])
    
    if options.template:
        templ_dir = options.template
    
    default = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'project_tmpl'))
    while not templ_dir:
        templ_dir = raw_input('Project template directory [%s]: ' % default) or default
    templ_dir = os.path.realpath(os.path.expanduser(templ_dir))
    if templ_dir[-1] != '/':
        templ_dir = templ_dir + "/"
    if options.virtenv:
        repl['virtenv'] = options.virtenv
    
    repl['virtenv'] = None
    while not repl['virtenv']:
        repl['virtenv'] = raw_input('Virtual environment name (e.g. %s): ' % repl['PROJECT_NAME']) or repl['PROJECT_NAME']
    
    main(repl, dest, templ_dir)