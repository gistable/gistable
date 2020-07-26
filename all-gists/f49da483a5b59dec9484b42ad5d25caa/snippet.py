import os
import re
import subprocess

import requests


GITLAB_ENDPOINT = os.environ["GITLAB_ENDPOINT"]
GITLAB_TOKEN = os.environ["GITLAB_TOKEN"]


BITBUCKET_ENDPOINT = os.environ["BITBUCKET_ENDPOINT"]
BITBUCKET_TEAM = os.environ["BITBUCKET_TEAM"]
BITBUCKET_USERNAME = os.environ["BITBUCKET_USERNAME"]
BITBUCKET_PASSWORD = os.environ["BITBUCKET_PASSWORD"]


bitbucket = requests.Session()
bitbucket.auth = (BITBUCKET_USERNAME, BITBUCKET_PASSWORD)


def list_gitlab_repositories():
    repositories = []
    page = 1
    while True:
        params = {"page": page, "per_page": 100, "private_token": GITLAB_TOKEN}
        url = os.path.join(GITLAB_ENDPOINT, "projects")
        res = requests.get(url, params=params)
        repositories += res.json()
        if page >= int(res.headers["x-total-pages"]):
            break
        page += 1
    return repositories


def list_bitbucket_projects():
    url = os.path.join(BITBUCKET_ENDPOINT, "teams", BITBUCKET_TEAM, "projects/")
    projects = []
    while url:
        res = bitbucket.get(url)
        payload = res.json()
        projects += payload["values"]
        url = payload.get("next", None)
    return projects


def list_bitbucket_repositories():
    url = os.path.join(BITBUCKET_ENDPOINT, "repositories", BITBUCKET_TEAM)
    repositories = []
    while url:
        res = bitbucket.get(url)
        payload = res.json()
        repositories += payload["values"]
        url = payload.get("next", None)
    return repositories


def generate_key(name):
    splitted = re.split("[- _]", name)
    chars = 2 if len(splitted) > 1 else 4
    return ''.join(n[:chars].upper() for n in splitted)


def create_bitbucket_project(name):
    payload = {
        "name": name,
        "key": generate_key(name),
        "is_private": True
    }
    url = os.path.join(BITBUCKET_ENDPOINT, "teams", BITBUCKET_TEAM, "projects/")
    res = bitbucket.post(url, json=payload)
    if not 200 <= res.status_code < 300:
        raise ValueError("could not create project {0}: {1}".format(name, res.text))


def create_bitbucket_repository(name, project):
    payload = {"scm": "git", "is_private": True, "project": {"key": generate_key(project)}}
    url = os.path.join(BITBUCKET_ENDPOINT, "repositories", BITBUCKET_TEAM, name)
    res = bitbucket.post(url, json=payload)
    if not 200 <= res.status_code < 300:
        raise ValueError("could not create repository {0}: {1}".format(name, res.text))


def clone_repository(repository):
    project_dir = os.path.join("/tmp", repository["namespace"]["name"], repository["name"])
    if os.path.exists(project_dir) and os.listdir(project_dir):
        return False
    os.makedirs(project_dir, exist_ok=True)
    subprocess.run(["git", "clone", repository["ssh_url_to_repo"], project_dir])
    return project_dir

def upload_repository(name, project):
    project_dir = os.path.join("/tmp", project, name)
    remote = "git@bitbucket.org:{0}/{1}.git".format(BITBUCKET_TEAM, name)
    subprocess.run(["git", "remote", "add", "bitbucket", remote], cwd=project_dir)
    subprocess.run(["git", "push", "bitbucket", "main"], cwd=project_dir)


class Migrator:
    def __init__(self):
        self.repositories = list_gitlab_repositories()
        self.projects = set(project["name"] for project in list_bitbucket_projects())

    def migrate_repositories(self):
        for repository in self.repositories:
            self.migrate_repository(repository)

    def ensure_project_exists(self, project):
        if project not in self.projects:
            create_bitbucket_project(project)
            self.projects.add(project)

    def migrate_repository(self, repository):
        project = repository["namespace"]["name"]
        self.ensure_project_exists(project)
        project_dir = clone_repository(repository)
        if not project_dir:
            return
        create_bitbucket_repository(repository["name"], project)
        upload_repository(repository["name"], project)


def main():
    migrator = Migrator()
    migrator.migrate_repositories()


if __name__ == '__main__':
    main()