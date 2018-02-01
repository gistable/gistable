#!/usr/bin/env python
#
# Initializes a git repository with some suggested best practices for DNAnexus
# workflow development & continuous integration. Run dx-ci-init.py in the root
# of your git repository; it creates the following, which you should then
# customize as you like:
#
# applets/hello-world
# Trivial applet template which you can build on or copy.
#           
# build_workflow.py
# A script that builds all the applets under applets/ then builds a workflow
# from the applets and optionally launches tests on it. The template builds a
# trivial workflow using the hello-world applet.
#
# run_tests.py
# Runs the workflow on test inputs - normally invoked by
#   ./build_workflow.py --run-tests
#
# DNAnexus platform project for continuous integration of the workflow
# It has the following structure:
#   /builds/ - build_workflow.py by default builds the applets and workflow
#              into a subfolder named based on timestamp and git revision
#   /assets/ - holds large and/or slow-evolving files or other data that may
#              be used as bound inputs in the workflow.
#   /test-data/ - files or other data that may be used in workflow test cases.
# Assets and test data should never be deleted, but moved into the respective
# 'old' subfolder when no longer actively used. This ensures that all historical
# versions of the workflow remain working. A git_revision property is set on the
# workflow and applets.
#
# .travis.yml
# Travis CI script that installs dx and then runs build_workflow.py --run-tests
# A Travis CI secure environment variable with your DNAnexus auth token must be
# added for this to work. Exact instructions will be shown when you run
# dx-ci-init.py. The Travis CI integration is optional; you can always just run
# ./build_workflow.py --run-tests
# locally instead.

from __future__ import print_function
import dxpy
import argparse
import os
import sys
import errno

files_to_create = [
    ".travis.yml",
    "build_workflow.py",
    "run_tests.py",
    "applets/hello-world/dxapp.json",
    "applets/hello-world/src/code.sh"
]

def main():
    argparser = argparse.ArgumentParser(description="Initialize a git repository for DNAnexus workflow development & continuous integration.")
    argparser.add_argument("--name", help="workflow name (default: current directory name)")
    argparser.add_argument("--project", help="DNAnexus project ID for continuous integration (default: create a new project)")
    argparser.add_argument("--force", help="Overwrite existing local files", action="store_true", default=False)
    args = argparser.parse_args()

    # ensure we're in a git repository
    if not os.path.isdir(".git"):
        print("The current directory should be the root of a git repository. Aborting.", file=sys.stderr)
        sys.exit(1)

    # ensure we're not going to clobber any existing files
    if not args.force:
        for fn in files_to_create:
            if os.path.exists(fn):
                print("Local file {} already exists. Aborting.".format(fn), file=sys.stderr)
                sys.exit(1)

    # detect current directory name
    if not args.name:
        args.name = os.path.split(os.getcwd())[1]
    print("Workflow name: " + args.name)

    # create the DNAnexus project for continuous integration
    if not args.project:
        args.project = dxpy.api.project_new({"name": "dx-ci-{}".format(args.name)})["id"]
    project = dxpy.DXProject(args.project)
    initialize_project(project)

    # generate local applet and workflow source
    generate_applet()
    generate_build_workflow_py(args.name, project)
    generate_run_tests_py(args.name)
    generate_travis_yml()

    print("""
Initialized templates for DNAnexus workflow continuous integration; modify
them so that './build_workflow.py --run-tests' does everything you'd like.
If this is a GitHub repository, you can complete Travis CI setup with these
steps:
1. Enable this repository in Travis CI's Accounts settings.
2. Create a long-lived DNAnexus auth token with CONTRIBUTE access to the
   continuous integration project (xxxx).
3. Run 'travis encrypt DX_AUTH_TOKEN=xxxx --add' here.
   ('gem install travis' first, if needed)
4. Commit the modified .travis.yml and push everything to GitHub.
Travis CI integration is optional; you can always just run
./build_workflow.py --run-tests
locally instead.
""")

def initialize_project(project):
    project.new_folder("/builds", parents=True)
    project.new_folder("/assets/old", parents=True)
    project.new_folder("/test-data/old", parents=True)
    print("Initialized DNAnexus project: {} ({})".format(project.describe()["name"], project.get_id()))

def generate_applet():
    # create hello-world applet source
    mkdir_p("applets/hello-world/src")
    with open("applets/hello-world/dxapp.json", "w") as dxapp_json:
        print(hello_world_dxapp_json, file=dxapp_json)
    with open("applets/hello-world/src/code.sh", "w") as code_sh:
        print(hello_world_code_sh, file=code_sh)
    make_executable("applets/hello-world/src/code.sh")
    print("Generated example applet in ./applets/hello-world")

hello_world_dxapp_json = """{
  "name": "hello-world",
  "dxapi": "1.0.0",
  "version": "0.0.1",
  "inputSpec": [
    {
      "name": "infile",
      "class": "file",
      "optional": true
    }
  ],
  "outputSpec": [
    {
      "name": "outfile",
      "class": "file"
    }
  ],
  "runSpec": {
    "interpreter": "bash",
    "file": "src/code.sh",
    "execDepends": [
    ],
    "systemRequirements": {
      "main": {
        "instanceType": "mem2_hdd2_x2"
      }
    }
  },
  "authorizedUsers": []
}
"""
hello_world_code_sh="""#!/bin/bash

main() {
    set -ex -o pipefail
    # dx-download-all-inputs --parallel
    if [ -n "$infile" ]; then
        dx cat "$infile" > /dev/null
    fi

    mkdir -p out/outfile
    echo "Hello, world!" > out/outfile/hello-world.txt

    # dx-upload-all-outputs --parallel
    outfile=$(cat out/outfile/hello-world.txt | dx upload --destination "hello-world.txt" --brief -)
    dx-jobutil-add-output outfile "$outfile" --class=file
}
"""

def generate_build_workflow_py(name, project):
    with open("build_workflow.py", "w") as build_workflow_py:
        src = build_workflow_py_template.replace("<<NAME>>",name).replace("<<PROJECT>>",project.get_id())
        print(src, file=build_workflow_py)
    make_executable("build_workflow.py")
    print("Generated ./build_workflow.py")

build_workflow_py_template = """#!/usr/bin/env python
from __future__ import print_function
import dxpy
import argparse
import sys
import os
import subprocess
import json
import time

here = os.path.dirname(sys.argv[0])
git_revision = subprocess.check_output(["git", "describe", "--always", "--dirty", "--tags"], cwd=here).strip()

def main():
    argparser = argparse.ArgumentParser(description="Build <<NAME>> workflow on DNAnexus.")
    argparser.add_argument("--project", help="DNAnexus project ID", default="<<PROJECT>>")
    argparser.add_argument("--folder", help="Folder within project (default: timestamp/git-based)", default=None)
    argparser.add_argument("--run-tests", help="Execute run_tests.py on the new workflow", action='store_true')
    argparser.add_argument("--run-tests-no-wait", help="Execute run_tests.py --no-wait", action='store_true')
    args = argparser.parse_args()

    # set up environment
    if args.folder is None:
        args.folder = time.strftime("/builds/%Y-%m-%d/%H%M%S-") + git_revision

    project = dxpy.DXProject(args.project)
    applets_folder = args.folder + "/applets"
    print("project: {} ({})".format(project.name, args.project))
    print("folder: {}".format(args.folder))

    # build the applets
    build_applets(project, applets_folder)

    # build the workflow
    wf = build_workflow(project, args.folder, applets_folder)
    print("workflow: {} ({})".format(wf.name, wf.get_id()))

    # run the tests if desired
    if args.run_tests_no_wait is True or args.run_tests is True:
        cmd = "python {} --project {} --workflow {}".format(os.path.join(here, "run_tests.py"),
                                                            project.get_id(), wf.get_id())
        if args.run_tests_no_wait is True:
            cmd = cmd + " --no-wait"
        print(cmd)
        sys.exit(subprocess.call(cmd, shell=True, cwd=here))

def build_applets(project, applets_folder):
    here_applets = os.path.join(here, "applets")
    applet_dirs = [os.path.join(here_applets,dir) for dir in os.listdir(here_applets)]
    applet_dirs = [dir for dir in applet_dirs if os.path.isdir(dir)]

    project.new_folder(applets_folder, parents=True)
    for applet_dir in applet_dirs:
        build_cmd = ["dx","build","--destination",project.get_id()+":"+applets_folder+"/",applet_dir]
        print(" ".join(build_cmd))
        applet_dxid = json.loads(subprocess.check_output(build_cmd))["id"]
        applet = dxpy.DXApplet(applet_dxid, project=project.get_id())
        applet.set_properties({"git_revision": git_revision})

def build_workflow(project, folder, applets_folder):

    # helper functions to get handles to stuff in the continuous integration
    # project: applets (which were just built) and slowly-evolving assets
    # (from the /assets folder -- typically large files used as bound inputs
    # in the workflow, e.g. reference genomes)
    def find_applet(applet_name):
        return dxpy.find_one_data_object(classname='applet', name=applet_name,
                                         project=project.get_id(), folder=applets_folder,
                                         zero_ok=False, more_ok=False, return_handler=True)
    def find_asset(asset_name, classname="file"):
        return dxpy.find_one_data_object(classname=classname, name=asset_name,
                                         project=project.get_id(), folder="/assets",
                                         zero_ok=False, more_ok=False, return_handler=True)
    def find_app(app_handle):
        return dxpy.find_one_app(name=app_handle, zero_ok=False, more_ok=False, return_handler=True)

    # create the workflow object
    wf = dxpy.new_dxworkflow(title="<<NAME>>",
                             name="<<NAME>>",
                             description="<<NAME>>",
                             project=project.get_id(),
                             folder=folder,
                             properties={"git_revision": git_revision})

    # set up the workflow stages, chaining outputs/inputs together as needed
    hello_world1_input = {
        # "infile": dxpy.dxlink(find_asset("myfile").get_id())
    }
    hello_world1_stage_id = wf.add_stage(find_applet("hello-world"), name="hello-world1",
                                         stage_input=hello_world1_input)

    hello_world2_input = {
        "infile": dxpy.dxlink({"stage": hello_world1_stage_id, "outputField": "outfile"})
    }
    hello_world2_stage_id = wf.add_stage(find_applet("hello-world"), name="hello-world2",
                                         stage_input=hello_world2_input)


    return wf

if __name__ == '__main__':
    main()
"""

def generate_run_tests_py(name):
    with open("run_tests.py", "w") as run_tests_py:
        src = run_tests_py_template.replace("<<NAME>>",name)
        print(src, file=run_tests_py)
    make_executable("run_tests.py")
    print("Generated ./run_tests.py")

run_tests_py_template = """#!/usr/bin/env python
from __future__ import print_function
import dxpy
import argparse
import sys
import os
import subprocess

def main():
    argparser = argparse.ArgumentParser(description="Run tests for the <<NAME>> workflow. This should normally be invoked indirectly, through ./build_workflow.py --run-tests")
    argparser.add_argument("--project", help="DNAnexus project ID", required=True)
    argparser.add_argument("--workflow", help="Workflow ID (must reside in the project)", required=True)
    argparser.add_argument("--folder", help="Folder in which to place outputs (default: test/ subfolder of workflow's folder)")
    argparser.add_argument("--no-wait", help="Exit immediately after launching tests", action="store_true", default=False)
    args = argparser.parse_args()

    project = dxpy.DXProject(args.project)
    workflow = dxpy.DXWorkflow(project=project.get_id(), dxid=args.workflow)

    if args.folder is None:
        args.folder = os.path.join(workflow.describe()["folder"], "test")

    print("test folder: " + args.folder)

    def find_test_data(name, classname="file"):
        return dxpy.find_one_data_object(classname=classname, name=name,
                                         project=project.get_id(), folder="/test-data",
                                         zero_ok=False, more_ok=False, return_handler=True)

    test_analyses = run_test_analyses(project, args.folder, workflow, find_test_data)
    print("test analyses: " + ", ".join([a.get_id() for a in test_analyses]))

    if args.no_wait != True:
        print("awaiting completion...")
        # wait for analysis to finish while working around Travis 10m console inactivity timeout
        noise = subprocess.Popen(["/bin/bash", "-c", "while true; do sleep 60; date; done"])
        try:
            for test_analysis in test_analyses:
                test_analysis.wait_on_done()
            print("Success!")
        finally:
            noise.kill()

        # TODO: validate the test analysis results in some way

def run_test_analyses(project, folder, workflow, find_test_data):
    # test cases: one or more named input hashes to run the workflow with
    test_inputs = {
        "test1": {
            # "hello-world1.infile": dxpy.dxlink(find_test_data("myfile").get_id())
        }
        # other test inputs could go here...
    }

    # The tests might only need smaller instance types than the applet
    # defaults (reduces cost of running tests).
    stage_instance_types = {
        # "hello-world1": "mem2_hdd2_x1"
    }

    git_revision = workflow.describe(incl_properties=True)["properties"]["git_revision"]
    analyses = []
    for test_name, test_input in test_inputs.iteritems():
        test_folder = os.path.join(folder, test_name)
        project.new_folder(test_folder, parents=True)
        analyses.append(workflow.run(test_input, project=project.get_id(), folder=test_folder,
                                     stage_instance_types=stage_instance_types,
                                     name="<<NAME>> {} {}".format(test_name, git_revision)))
    return analyses

if __name__ == '__main__':
    main()
"""

def generate_travis_yml():
    with open(".travis.yml", "w") as outfile:
        print(travis_yml, file=outfile)
    # TODO: it would be nice to do 'travis encrypt DX_AUTH_TOKEN=xxxx'
    # automatically. However the repository has to be switched ON in Travis
    # before that command will work.
    print("Generated .travis.yml")

travis_yml = """language: python
python:
  - 2.7
# prevent travis from doing pip install requirements.txt
install: true
script:
# disable Travis default virtualenv
- deactivate
# deploy dx-toolkit
- wget https://wiki.dnanexus.com/images/files/dx-toolkit-current-ubuntu-12.04-amd64.tar.gz
- tar zxf dx-toolkit-current-ubuntu-12.04-amd64.tar.gz
- source dx-toolkit/environment
# execute workflow builder script
- python build_workflow.py --run-tests
"""

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def make_executable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0444) >> 2    # copy R bits to X
    os.chmod(path, mode)

if __name__ == '__main__':
    main()

