#!/usr/bin/env python
"""
Check all existing Docker containers for their mapped paths, and then purge any
zombie directories in docker's volumes directory which don't correspond to an
existing container.

"""
import logging
import os
import sys
from shutil import rmtree

import docker


DOCKER_VOLUMES_DIR = "/var/lib/docker/vfs/dir"


def get_immediate_subdirectories(a_dir):
    return [os.path.join(a_dir, name) for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]


def main():
    logging.basicConfig(level=logging.INFO)

    client = docker.Client()

    valid_dirs = []
    for container in client.containers(all=True):
        volumes = client.inspect_container(container['Id'])['Volumes']
        if not volumes:
            continue

        for _, real_path in volumes.iteritems():
            if real_path.startswith(DOCKER_VOLUMES_DIR):
                valid_dirs.append(real_path)

    all_dirs = get_immediate_subdirectories(DOCKER_VOLUMES_DIR)
    invalid_dirs = set(all_dirs).difference(valid_dirs)

    logging.info("Purging %s dangling Docker volumes out of %s total volumes found.",
                 len(invalid_dirs), len(all_dirs))
    for invalid_dir in invalid_dirs:
        logging.info("Purging directory: %s", invalid_dir)
        rmtree(invalid_dir)

    logging.info("All done.")


if __name__ == "__main__":
    sys.exit(main())