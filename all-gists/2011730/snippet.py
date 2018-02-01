from __future__ import with_statement
from paver.easy import *
from paver.svn import update as svnupdate
import os

def run_svn(dir):
    print "svn update %s" % dir
    sh('svn up')

def run_hg(dir):
    print "hg update %s" % dir
    sh('hg pull -u')

def run_git(dir):
    print "git update %s" % dir
    sh('git pull ')

def run_bzr(dir):
    print "bzr update %s" % dir
    sh('bzr pull && bzr update ')

@task
def vcs_cmd():
    current = path("./")
    cmds = []
    for lib_dir in current.dirs():
        with pushd(lib_dir):
            for f in current.listdir():
                if f == "./.svn":
                    for s in f.files("entries"):
                        url = s.lines()[4].strip()
                        cmd = "svn co %s %s" % (url, lib_dir)
                        cmds.append(cmd)
                    print "svn %s" % f 
                elif f == "./.hg":
                    for h in f.files("hgrc"):
                        url = h.lines()[1].strip()
                        url = url.split("=")[1].strip()
                        cmd = "hg clone %s " % url
                        cmds.append(cmd)
                elif f == "./.git":
                    for h in f.files("config"):
                        for l in h.lines():
                            url = l.strip()
                            if url.startswith('url'):
                                url = url.split("=")[1].strip()
                                cmd = "git clone %s " % url
                                cmds.append(cmd)
                                break
                elif f == "./.bzr":
                    for h in f.files("config"):
                        pass
    
    path("./vcs.txt").write_lines(cmds)

@task
def co_vcs():
    for cmd in path("./vcs.txt").lines(retain=False):
        #print cmd
        try:
            sh(cmd)
        except:
            pass

@task
def all_update():
    current = path("./")
    for lib_dir in current.dirs():
        with pushd(lib_dir):
            vcs = lambda x:x
            for f in current.listdir():
                if f == "./.svn":
                    vcs = run_svn
                elif f == "./.hg":
                    vcs = run_hg
                elif f == "./.git":
                    vcs = run_git
                elif f == "./.bzr":
                    vcs = run_bzr
            try: 
                #print os.getcwd()
                vcs(lib_dir)
            except:
                pass
        
def exec_sh(py_dir, cmd):
    print py_dir
    with pushd(py_dir):
        sh(cmd)
        
