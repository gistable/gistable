#!/usr/bin/env python3
"""Backs up data-only volumes to host backup directory using rdiff-backup.

First create a Docker image containing rdiff-backup (named rdiff-backup)
Dockerfile:

    FROM ubuntu:precise
    RUN apt-get update && apt-install -qy rdiff-backup

``docker build -rm -t rdiff-backup .``

"""
import json
from shlex import split
from subprocess import Popen, PIPE

EXCLUDED_VOLUMES = ("sabnzbd_data",)
CONTAINER_EXT_TO_BACKUP = ("data", "config")
BACKUP_DIR = "/mnt/backup/docker"
CONTAINER_BU_DIR = "/backup"
DOCKER_CMD = ("docker run --rm --volumes-from {container_name} "
              "-v {backup_dir}/{container_name}/{container_dir}:"
              "{container_bu_dir} rdiff-backup "
              "rdiff-backup {container_dir} "
              "{container_bu_dir}")


def get_containers():
    """Get container names to backup.

    Only will match containers with CONTAINER_EXT_TO_BACKUP in the name.

    """
    cmd = "docker ps -a"
    res = Popen(split(cmd),
                stdout=PIPE).communicate()[0].decode().split('\n')[1:-1]
    names = [i.split()[-1] for i in res]
    names = [i for ext in CONTAINER_EXT_TO_BACKUP for i in names
             if ext in i and i not in EXCLUDED_VOLUMES]
    return names


def get_dirs(name):
    """Gets container directories to backup from 'docker inspect'

    Args: name - name of container
    Returns: list of container directories

    """
    cmd = "docker inspect {}".format(name)
    res = Popen(split(cmd), stdout=PIPE).communicate()[0].decode()
    res = json.loads(res)
    return res[0]['Config']['Volumes'].keys()


def rdiff(docker_cmd):
    """Runs docker command to rdiff-backup container shared volume data to
    backup folder.

    Try 3 times to run container, then if it still fails, skip it.

    """
    return_code = 1
    count = 0
    while return_code != 0 and count <= 3:
        cmd = Popen(split(docker_cmd), stdout=PIPE)
        cmd.communicate()[0]
        return_code = cmd.returncode
        count += 1


def run():
    """Copy /data or /config to CONTAINER_DIR (TMP_DIR on host)
    Then rdiff-backup TMP_DIR to BACKUP_DIR/<container>

    """
    for container in get_containers():
        dirs = get_dirs(container)
        for directory in dirs:
            rdiff(DOCKER_CMD.format(container_name=container,
                                    backup_dir=BACKUP_DIR,
                                    container_bu_dir=CONTAINER_BU_DIR,
                                    container_dir=directory))


if __name__ == '__main__':
    run()