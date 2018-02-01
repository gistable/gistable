#!/usr/bin/env python
import os
import pprint
import subprocess
import sys
from optparse import make_option
from urllib import quote_plus
from urlparse import urljoin

import dateutil.parser
import requests
from django.conf import settings
from django.core.management import BaseCommand, CommandError
from six import python_2_unicode_compatible

ORGANIZATION_NAME = 'org'
PROJECT_NAME = 'project'


class Command(BaseCommand):

    help = 'CircleCI Command Line Interface'

    option_list = BaseCommand.option_list + (
        make_option('--ssh', action='store_true', default=False),
        make_option('--cancel', action='store_true', default=False),
        make_option('--artifacts', action='store_true', default=False),
        make_option('--me', action='store_true', default=False),
        make_option('--cancel-redundant-builds', action='store_true'),
        make_option('--start'),
    )

    def __init__(self):
        super(Command, self).__init__()
        token = getattr(settings, 'CIRCLECI_TOKEN', None) or os.environ.get('CIRCLECI_TOKEN')
        if not token:
            raise CommandError('You need to specify a circleci access token either in your settings or '
                               'in your environment')
        self.cci = CircleCi(token)

    def handle(self, build_id=None, *args, **options):

        # Some commands don't require a build

        if options['me']:
            pprint.pprint(self.cci.me)
            return 0

        elif options['cancel_redundant_builds']:
            self.cancel_redundant_builds()
            return 0

        elif options['start']:
            self.start_build(options['start'])
            return 0

        # From here on, we need a build number to operate

        if not build_id:
            error('Please specify a build number.')

        build = self.cci.build(build_id)

        if options['ssh']:
            build_dict = build.data
            if not build_dict['ssh_enabled']:
                error('This build does not have SSH enabled.')
            node = build_dict['node'][0]
            ip_addr = node['public_ip_addr']
            port = node['port']
            cmd = ['ssh', 'ubuntu@{}'.format(ip_addr),
                   '-p', str(port),
                   '-o', 'UserKnownHostsFile /dev/null',
                   '-o', 'StrictHostKeyChecking=no']
            print('Running: {}'.format(cmd))
            p = subprocess.Popen(cmd, stdout=sys.stdout, stdin=sys.stdin, stderr=sys.stderr)
            p.communicate()
        elif options['cancel']:
            build.cancel()
        elif options['artifacts']:
            artifacts = build.artifacts
            for a in artifacts:
                print(a)
            print('{} artifact(s).'.format(len(artifacts)))
        else:
            pprint.pprint(self.cci.build(build_id))

    def cancel_redundant_builds(self):
        active_builds = {}
        for build in self.cci.builds:
            if not build.active:
                continue
            if 'branch' not in build.data:
                print('Got weird build #{} without a branch...?'.format(build.build_num))
                continue
            if not build.queued_at:
                print('Looks like build #{} was not queued...?'.format(build.build_num))
                pprint.pprint(build)
                continue
            branch = build.data['branch']
            active_builds.setdefault(branch, []).append((build.queued_at, build))

        for branch, builds in active_builds.iteritems():
            if len(builds) > 1:
                builds = sorted(builds)
                for queued_at, build in builds[:-1]:
                    build.cancel()

    def start_build(self, branch):
        self.cci.post_project('tree/{}'.format(quote_plus(branch)))


class CircleCi(object):

    BASE_URL = 'https://circleci.com/api/v1/'

    def __init__(self, access_token):
        self.token = access_token

    @property
    def project_base_path(self):
        return 'project/{}/{}/'.format(ORGANIZATION_NAME, PROJECT_NAME)

    def request(self, method, path, **kwargs):
        kwargs.setdefault('params', {}).update(**{'circle-token': self.token})
        kwargs.setdefault('headers', {}).update(**{'Accept': 'application/json'})
        url = urljoin(self.BASE_URL, path)
        print('\x1b[1m{} {}\x1b[0m'.format(method, url))
        r = requests.request(method, url, **kwargs)
        r.raise_for_status()
        return r

    def get(self, *args, **kwargs):
        r = self.request('GET', *args, **kwargs)
        return r.json()

    def get_project(self, path='', *args, **kwargs):
        path = urljoin(self.project_base_path, path)
        return self.get(path, *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request('POST', *args, **kwargs)

    def post_project(self, path, *args, **kwargs):
        path = urljoin(self.project_base_path, path)
        return self.post(path, *args, **kwargs)

    @property
    def builds(self):
        builds_data = self.get_project()
        return [CircleCiBuild(self, data=build) for build in builds_data]

    @property
    def me(self):
        return self.get('me')

    def build(self, build_num):
        return CircleCiBuild(self, build_num)


@python_2_unicode_compatible
class CircleCiBuild(object):

    def __init__(self, api, build_num=None, data=None):
        self.api = api
        self.build_num = int(build_num or data['build_num'])
        self._data = data or None

    def __str__(self):
        commits = self.data.get('all_commit_details')
        subject = commits[-1]['subject'] if commits and len(commits) > 0 else '(No subject)'
        return u'#{} {} {} {} {}'.format(self.build_num, self.queued_at, self.data['status'], self.data['branch'], subject)

    def __repr__(self):
        self_str = unicode(self).encode('ascii', 'backslashreplace')
        return '<{}: {}>'.format(self.__class__.__name__, self_str)

    def cancel(self):
        print('Canceling build: {}'.format(self))
        return self.api.post_project('{}/cancel'.format(self.build_num))

    @property
    def queued_at(self):
        queued_at = self.data.get('usage_queued_at')
        return queued_at and dateutil.parser.parse(queued_at)

    @property
    def data(self):
        if self._data is None:
            self._data = self.api.get_project('{}'.format(self.build_num))
        return self._data

    @property
    def artifacts(self):
        artifacts = self.api.get_project('{}/artifacts'.format(self.build_num))
        return [a['url'] for a in artifacts]

    @property
    def status(self):
        return self.data['status']

    @property
    def active(self):
        if self.status in ['success', 'timedout', 'fixed', 'canceled', 'failed', 'not_run', 'retried', 'no_tests']:
            return False
        if self.status in ['not_running', 'scheduled', 'running', 'queued']:
            return True

        raise CommandError('Unknown CircleCI status: {!r}'.format(self.status))


def error(s, *args, **kwargs):
    print(s.format(*args, **kwargs))
    sys.exit(1)
