#!/usr/bin/env python
r"""Cluster submission

Light helper script for submitting jobs to a cluster. For instance, to submit
a job that calls the command hostname, just use:

    $ sub hostname

Additionally, you can specify the name of the job:

    $ sub -n testjob hostname

Walltime and queue is also available:

    $ sub -q friendlyq -m 2 -w 12:34:56 hostname

If submitting a command that also takes arguments, a POSIX separator must be 
used to indicate the the split. For instance:

    $ sub -n testjob -- grep -i -n export ~/.bash_profile

It is possible to build up a list of commands to execute within a single job
as well. By using `--prime`, you can build up a list of commands. These 
commands are stored in a file within the current working directory. The 
commands can then be submitted by issuing a `--purge`. The `--purge` will
create a PBS script, store it under the sub.primed/ directory, and submit the
script to the cluster. The script includes a wait command at the end to ensure
that all executed commands complete (in the event of using "&"). See the 
example below:

    $ sub --prime -- hostname
    $ sub --prime -- uname -a
    $ sub --prime -- date
    $ sub --purge -q route -w 12:34:56

All commands, time stamps, job details, etc are stored in the current working
directory under the file `sub.notes`. All standard output and standard error 
files are placed in the sub.oe/ directory.
"""

from sys import argv, exit, stderr
from random import choice
from subprocess import PIPE, Popen
from datetime import datetime
from os.path import join, exists, isdir
from os import getcwd, mkdir, environ, path, remove

import click


__author__ = "Daniel McDonald"
__credits__ = ["Daniel McDonald"]
__license__ = "CC0 1.0, http://creativecommons.org/publicdomain/zero/1.0/"
__maintainer__ = "Daniel McDonald"
__email__ = "mcdonadt@colorado.edu"


# files and directories
NOTES = 'sub.notes'
JOB_OE = 'sub.oe'
PRIME_FILE = '.sub_prime'
PRIMED_SCRIPTS = 'sub.primed'


def _random_job_name(prefix='sub', delimiter='_', size=6):
    """Return a random job name

    Not assured to be unique as a job name... but likely
    """
    alpha = "abcdefghijklmnopqrstuvwxyz"
    alpha += alpha.upper()
    alpha += "0123456789"
    suffix = ''.join([choice(alpha) for i in range(size)])

    return "%s%s%s" % (prefix, delimiter, suffix)


def _check_and_make(name):
    """Make a directory if needed"""
    if exists(name):
        if not isdir(name):
            stderr.write("%s is a file, must be a directory!\n" % name)
            exit(1)
    else:
        mkdir(name)


def _format_command(cmd, qsub_args):
    """Format the system call to submit"""
    qsub_args = ' '.join(qsub_args)
    cmd = ' '.join(cmd)

    return 'echo "cd `pwd`; %s" | qsub -V %s' % (cmd, qsub_args)


def _format_script(cmds, res, name):
    """Construct a PBS-file script"""
    script = res
    script.append('cd $PBS_O_WORKDIR')
    script.extend(cmds)
    script.append('wait')
    
    _check_and_make(PRIMED_SCRIPTS)
    script_path = join(PRIMED_SCRIPTS, name + '.pbs')
    with open(script_path, 'w') as script_fp:
        script_fp.write('\n'.join(script))
        script_fp.write('\n')

    return "qsub -V %s" % script_path
    

def _prime(cmd):
    """Stage commands to be executed later"""
    with open(PRIME_FILE, 'a') as fp:
        fp.write(' '.join(cmd))
        fp.write('\n')


def _purge(name, ppn, walltime, queue, mem):
    """Execute staged commands"""
    if not exists(PRIME_FILE):
        stderr.write("No primed commands found.")
        exit(1)
      
    cmds = []
    with open(PRIME_FILE) as fp:
        for line in fp:
            cmds.append(line.strip())

    res = _format_qsub_args(name, queue, ppn, walltime, mem, script=True)
    to_submit = _format_script(cmds, res, name)

    remove(PRIME_FILE)

    return _submit(to_submit, name)


def _oneoff(name, ppn, walltime, queue, cmd, mem):
    """Submit a one-off command"""
    res = _format_qsub_args(name, queue, ppn, walltime, mem, script=False)
    to_submit = _format_command(cmd, res)

    return _submit(to_submit, name)


def _format_qsub_args(name, queue, ppn, wt, mem, script):
    """Format resources"""
    # prefix
    pf = '#PBS ' if script else ''

    res = []
    res.append('%s-o %s' % (pf, JOB_OE))
    res.append('%s-e %s' % (pf, JOB_OE))
    res.append('%s-N %s' % (pf, name))
    res.append('%s-q %s' % (pf, queue)) if queue is not None else None
    res.append('%s-l nodes=1:ppn=%d' % (pf, ppn)) if ppn is not None else None 
    res.append('%s-l walltime=%s' % (pf, wt)) if wt is not None else None 
    res.append('%s-l mem=%sgb' % (pf, mem)) if mem is not None else None 

    return res


def _submit(to_submit, name):
    """Execute a call to qsub"""
    # make stdout/stderr directories
    _check_and_make(JOB_OE)

    # execute the command
    # from QIIME 1.6, qiime.util.qiime_system_call
    proc = Popen(to_submit, shell=True, universal_newlines=True, stdout=PIPE,
                 stderr=PIPE)
    stdout_cmd, stderr_cmd = proc.communicate()
    return_value = proc.returncode
    
    # check sanity
    if return_value != 0:
        stderr.write("Could not submit, exited with:\n")
        stderr.write(stderr_cmd + '\n')
        exit(1)
    else:
        job_id = stdout_cmd.split('.')[0]

    cwd = getcwd()
    stdout_fp = join(cwd, JOB_OE, "%s.o%s" % (name, job_id))
    stderr_fp = join(cwd, JOB_OE, "%s.e%s" % (name, job_id))

    # dump the notes
    notes = open(NOTES, 'a')
    notes.write("time=%s\n" % datetime.now().strftime('%H:%M:%S on %d %b %Y'))
    notes.write("id=%s\n" % name)
    notes.write("job_id=%s\n" % job_id)
    notes.write("cmd=%s\n" % to_submit)
    notes.write("resub=%s\n" % ' '.join(argv))
    notes.write("expected_stdout=%s\n" % stdout_fp)
    notes.write("expected_stderr=%s\n" % stderr_fp)
    notes.write("\n")
    notes.close()

    return job_id


@click.command()
@click.option('--name', '-n', default=None, help='Job name, default to random')
@click.option('--ppn', '-p', default=1, help='Procs per node, default to 1')
@click.option('--walltime', '-w', default=None, help='Job walltime')
@click.option('--queue', '-q', default='route', help='Submission queue')
@click.option('--mem', '-m', default='8', help='Memory (in GB)')
@click.option('--bare', '-b', is_flag=True)
@click.option('--prime', is_flag=True)
@click.option('--purge', is_flag=True)
@click.argument('cmd', nargs=-1)
def sub(name, ppn, walltime, queue, mem, bare, prime, purge, cmd):
    if not cmd and not purge:
        raise click.UsageError("No command specified")
    
    if prime:
        _prime(cmd)
        return
    
    if name is None:
        name = _random_job_name()

    if purge:
        job_id = _purge(name, ppn, walltime, queue, mem)
    else:
        job_id = _oneoff(name, ppn, walltime, queue, cmd, mem)
        
    if bare:
        click.echo(job_id)
    else:
        click.echo("Success! This job is named %s with job id %s." % (name, 
                                                                      job_id))


if __name__ == '__main__':
    sub()