#!/usr/bin/python
# encoding: utf-8
from __future__ import unicode_literals

import re
import subprocess
try:
    import xml.etree.cElementTree as ET
except ImportError:  # pragma: no cover
    import xml.etree.ElementTree as ET

from workflow import Workflow


class AlfredPlist(object):
    def __init__(self, wf):
        self.wf = wf
        self.data = self.wf.info

    ## Properties  ------------------------------------------------------------

    @property
    def all_uids(self):
        return self.data['uidata'].keys()

    @property
    def node_types(self):
        types = [i['type'] for i in self.data['objects']]
        return list(set(types))

    @property
    def script_filters(self):
        uids_gen = self.get_uids_by_type('input.scriptfilter')
        return list(set([x for x in uids_gen]))

    @property
    def script_actions(self):
        actions_gen = self.get_uids_by_type('action.script')
        actions = [x for x in actions_gen]
        outputs_gen = self.get_uids_by_type('output.script')
        outputs = [x for x in outputs_gen]
        return list(set(actions + outputs))

    def get_uids_by_type(self, type):
        if not type.startswith('alfred.workflow.'):
            type = 'alfred.workflow.' + type
        return (i['uid'] for i in self.data['objects']
                if i['type'] == type)

    ## Object Methods  --------------------------------------------------------

    def get_object(self, uid):
        item_gen = (i for i in self.data['objects']
                    if i['uid'] == uid)
        return next(item_gen, False)

    def get_script(self, uid):
        if self.check_objects():
            item = self.get_object(uid)
            if item:
                try:
                    return item['config']['script']
                except KeyError:
                    return False

    def get_connections(self, uid):
        if self.check_connections():
            conns = self.data['connections'].get(uid, False)
            if conns:
                return [(con['destinationuid'], con['modifiersubtext'])
                        for con in conns]

    def get_type(self, uid):
        if self.check_objects():
            item = self.get_object(uid)
            if item:
                try:
                    return item['type'].split('.')[-1]
                except KeyError:
                    return False

    def get_description(self, uid):
        if self.check_objects():
            item = self.get_object(uid)
            if item:
                try:
                    subtext = item['config']['subtext']
                    title = item['config']['title']
                    return ': '.join([title, subtext])
                except KeyError:
                    return False

    ## Section Checkers  ------------------------------------------------------

    def check_objects(self):
        if isinstance(self.data['objects'], list):
            return True
        else:
            raise Exception('Malformed `objects` section of `info.plist`')

    def check_connections(self):
        if isinstance(self.data['connections'], dict):
            return True
        else:
            raise Exception('Malformed `connections` section of `info.plist`')


class WorkflowTesting(object):
    def __init__(self, wf):
        self.wf = wf
        self.info = AlfredPlist(self.wf)

    # TODO
    def test_filters(self, query):
        used_scripts = set()
        for filterer in self.info.script_filters:
            f_script = self.info.get_script(filterer)
            if f_script not in used_scripts:
                print('\n\n\n- - -\n## SCRIPT FILTER')
                arg = self.run_filter(f_script, query)
                used_scripts.add(f_script)
                if arg:
                    print('\n\n- -\n## Arg: ' + arg)
                    cons = self.info.get_connections(filterer)
                    if cons:
                        for con in cons:
                            con_uid, desc = con
                            con_script = self.info.get_script(con_uid)
                            if con_script:
                                con_res = self.run_command(con_script, arg)
                                if con_res:
                                    print('Connection Result: ' + str(con_res))
                                print('\n\n')
                    else:
                        print(cons)

    def run_command(self, command, query):
        filter_cmd = self.prepare_command(command, query)
        try:
            return subprocess.check_output(filter_cmd)
        except subprocess.CalledProcessError as e:
            print(e)
            return False

    def run_filter(self, filter_script, query):
        xml_res = self.run_command(filter_script, query)
        return self.get_filter_result_arg(xml_res)

    def get_filter_result_arg(self, xml_res):
        try:
            root = ET.fromstring(xml_res)
            try:
                return root.find('item').find('arg').text
            except AttributeError:
                return False
        except TypeError:
            return False

    def prepare_command(self, script_str, query=None):
        if query:
            script_str = self.assign_query(script_str, query)
        cmd_str = self.expand_script_path(script_str)
        full_cmd_str = self.explicit_python_call(cmd_str)
        return full_cmd_str.split()

    @staticmethod
    def assign_query(script_str, query):
        clean = re.sub(r"[^\s]{query}[^\s]", '{query}', script_str)
        return clean.replace('{query}', query)

    def expand_script_path(self, script_str):
        # Get name of Python script file
        py_file = re.search(r'(.*?)\.py', script_str)
        if py_file:
            py_file = py_file.group(1) + '.py'
            # Get full path to Python script file
            full_path = self.wf.workflowfile(py_file)
            # Replace file name with file path
            return script_str.replace(py_file, full_path)

    def explicit_python_call(self, script_str):
        return re.sub(r".*?python\s",
                      "/usr/bin/python ",
                      script_str)

WF = Workflow()
t = WorkflowTesting(WF)
#t_scpt = t.info.get_script(t.info.author_filter)
#t_cmd = t.run_filter(t_scpt, 'margheim')
#print(t_cmd)
t.test_filters('horace')
