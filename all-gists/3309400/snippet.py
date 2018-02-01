#! usr/bin/env python
# -*- encoding: utf8 -*-


# Requires Python 2.7, or 2.6 with argparse installed.
# Currently adds task to The Hit List only to the inbox.


import argparse, os

def add(params)
# construct the property list for the task
    props = '{ created date: now, '
    try:
        props += 'due date: date "'+params.pop('date')+'", '
    except:
        pass
    try:
        props += 'notes: "'+params.pop('note')+'", '
    except: 
        pass

# build the task itself, with context and tags
    task = params.pop('title')
    try:
        for tag in tags:
            task += " "+tags[tag]
        params.pop('tags')
    except:
        pass
    try:
        for item in params:
            task += " "+params[item]
    except:
        pass
    props += 'title: "'+task+'" }'

# construct applescript to add task
    task_add = '''tell application "The Hit List"
    set now to current date
    tell inbox to make new task with properties %s
    end tell''' % (props)

#pass applescript to osascript
    osa_call = "osascript -e '"+task_add+"'"
    os.system(osa_call)

functions = {'add':add }

p = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description='''
Add a task to The Hit List inbox:
    python newtask.py add "<title of task>" -d="m/d/yy hh:mm pm|am" -n="<text of note>"

    Due dates can be either just a date, or a date + time, as long as am or pm is included.

    Options:
    -t, --tags </tag>
    -c, --context <@context>
    -n, --note <task note>
    -d, --due <due date>
    '''

p.add_argument("cmd", help=argparse.SUPPRESS, nargs="*")
p.add_argument("-d","--date")
p.add_argument("-c","--context")
p.add_argument("-n","--note")
p.add_argument("-t","--tags", nargs="*")

opts = avrs(p.parse_args())

cmd = opts.pop('cmd')

params = { k : opts[k] for k in opts if opts[k] != None }
params['title'] = cmd.pop(1)

functions[cmd[0]](params)