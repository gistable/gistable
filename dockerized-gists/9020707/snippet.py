import json
import urllib
import urllib2

url = 'http://localhost:8888/ansible'

def post(category, data):
    data['category'] = category

    invocation = data.pop('invocation', None)
    if invocation:
        data['module_name'] = invocation['module_name']
        data['module_args'] = invocation['module_args']

    values = {'json': json.dumps(data)}

    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    urllib2.urlopen(req)

class CallbackModule(object):
    def on_any(self, *args, **kwargs):
        pass

    def runner_on_failed(self, host, res, ignore_errors=False):
        res["host"] = host
        post('FAILED', res)

    def runner_on_ok(self, host, res):
        res["host"] = host
        post('OK', res)

    def runner_on_error(self, host, msg):
        post('ERROR', {"host": host, 'error': msg})

    def runner_on_skipped(self, host, item=""):
        post('SKIPPED', {"host": host, "item": item})

    def runner_on_unreachable(self, host, res):
        res['host'] = host
        post('UNREACHABLE', res)

    def runner_on_no_hosts(self):
        pass

    def runner_on_async_poll(self, host, res, jid, clock):
        pass

    def runner_on_async_ok(self, host, res, jid):
        pass

    def runner_on_async_failed(self, host, res, jid):
        pass

    def playbook_on_start(self):
        post("Play_on_start", {})

    def playbook_on_notify(self, host, handler):
        pass

    def playbook_on_no_hosts_matched(self):
        pass

    def playbook_on_no_hosts_remaining(self):
        pass

    def playbook_on_task_start(self, name, is_conditional):
        pass

    def playbook_on_vars_prompt(self, varname, private=True, prompt=None, encrypt=None, confirm=False, salt_size=None, salt=None, default=None):
        pass

    def playbook_on_setup(self):
        pass

    def playbook_on_import_for_host(self, host, imported_file):
        pass

    def playbook_on_not_import_for_host(self, host, missing_file):
        pass

    def playbook_on_play_start(self, pattern):
        post("Play_start", {})

    def playbook_on_stats(self, stats):
        pass

