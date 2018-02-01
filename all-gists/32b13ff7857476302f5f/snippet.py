import asyncio
import base64
import concurrent.futures
from functools import partial
import os
import pip
import re

import requests


class Session(requests.Session):

    def __init__(self, loop, executor, *args, **kwargs):
        self.loop = loop
        self.executor = executor
        super(Session, self).__init__(*args, **kwargs)

    @asyncio.coroutine
    def request(self, *args, **kwargs):
        func = partial(super(Session, self).request, *args, **kwargs)
        rv = yield from self.loop.run_in_executor(self.executor, func)
        return rv


class Analyser:
    org_name = ''
    github_app_auth = ''

    api_base_url = 'https://api.github.com'
    org_base_url = '{}/orgs/{}'.format(api_base_url, org_name)
    respositories_url = '{}/repos'.format(org_base_url)
    repository_tree_url = '{}/repos/{}/{{}}/git/trees/master?recursive=1'.format(api_base_url, org_name)
    blob_url = '{}/repos/{}/{{}}/git/blobs/{{}}'.format(api_base_url, org_name)

    requirements_re = re.compile(r'(requirements.*?txt$|\bsetup.py$)', re.IGNORECASE)
    next_url_re = re.compile(r'<(.[^>]*)>; rel="next"', re.IGNORECASE)

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.loop.set_debug(True)

        self.executor = concurrent.futures.ThreadPoolExecutor(20)

        self.session = Session(self.loop, self.executor)
        self.session.auth = (self.github_app_auth, 'x-oauth-basic')

    @asyncio.coroutine
    def repositories(self, next_url=None):
        print('Getting a list of repositories {}'.format(next_url or 'initial'))
        response = yield from self.session.get(next_url or self.respositories_url)

        next_url = self.next_url_re.search(response.headers['Link'])
        if next_url:
            additional_repositories = yield from self.repositories(next_url.group(1))
        else:
            additional_repositories = []

        assert response.status_code == 200, "Error getting repositories: {} - {!r}".format(
            response.status_code, response.content)
        repositories = [repository['name'] for repository in response.json()]
        return repositories + additional_repositories

    @asyncio.coroutine
    def process_repository(self, repository_name):
        print(repository_name)

        tree = yield from self.session.get(self.repository_tree_url.format(repository_name))
        if tree.status_code != 200:
            print('Skipping {} because of http status code {}'.format(repository_name, tree.status_code))
            return
        requirements_paths = [t for t in tree.json()['tree'] if self.requirements_re.search(t['path'])]

        requirements = []
        for path in requirements_paths:
            if path['type'] != 'blob':
                continue
            print('Downloading {}/{}'.format(repository_name, path['path']))
            blob = yield from self.session.get(path['url'])
            print('Response {!r}'.format(blob))
            dest_file = os.path.join(os.path.dirname(__file__), 'repositories', repository_name, path['path'])
            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
            with open(dest_file, 'wb') as f:
                f.write(base64.b64decode(blob.json()['content'].encode()))

        # Another for because of dependencies.
        for path in requirements_paths:
            if path['type'] != 'blob' or 'setup.py' in path['path'].lower():
                continue
            filename = '{}/{}'.format(repository_name, path['path'])
            print('Reading {}'.format(filename))
            try:
                for requirement in pip.req.parse_requirements('repositories/{}'.format(filename), session=self.session):
                    if requirement.req and requirement.req.specs:
                        version = ','.join([''.join(s) for s in requirement.req.specs])
                    else:
                        version = 'No version specified'

                    requirements.append((repository_name, requirement.name or 'No name provided', version, requirement.url or 'pypi', ''))
            except pip.exceptions.InstallationError as e:
                requirements.append(['Invalid requirements: {!r}'.format(e)] * 5)

        return requirements

    @asyncio.coroutine
    def analyse(self):
        repositories = yield from self.repositories()
        requirements_file = open(os.path.join(os.path.dirname(__file__), 'requirements.csv'), 'w')
        requirements_file.write('project\tlib_name\tlib_version\tlib_origin\tdescription\n')
        jobs = [asyncio.async(self.process_repository(repository)) for repository in repositories]

        for future in jobs:
            requirements = yield from future
            if requirements is None:
                continue
            for requirement in requirements:
                requirements_file.write('\t'.join(requirement) + '\n')


analyser = Analyser()
analyser.loop.run_until_complete(asyncio.async(analyser.analyse()))
print("Pending tasks at exit: %s" % asyncio.Task.all_tasks(analyser.loop))
analyser.loop.close()
