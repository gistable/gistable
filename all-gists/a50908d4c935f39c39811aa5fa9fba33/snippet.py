#!/bin/env python
import os
import json
import hashlib
from functools import reduce
import argparse
import logging
import shutil

DOCKER_DIR = '/var/lib/docker'
IMAGE_ROOT = os.path.join(DOCKER_DIR, 'image/aufs')
IMAGE_STORE_DIR = os.path.join(IMAGE_ROOT, 'imagedb')
LAYER_STORE_DIR = os.path.join(IMAGE_ROOT, 'layerdb')
AUFS_ROOT = os.path.join(DOCKER_DIR, 'aufs')
AUFS_LAYER_DIR = os.path.join(AUFS_ROOT, 'layers')
AUFS_MNT_DIR = os.path.join(AUFS_ROOT, 'mnt')
AUFS_DIFF_DIR = os.path.join(AUFS_ROOT, 'diff')
CONTAINER_DIR = os.path.join(DOCKER_DIR, 'containers')

def chainID(diffs):
    """calculate chain-id from diff layers
    this is the same logic as in docker's source code
    """
    if len(diffs) == 0:
        return ''

    def chain_hash(x, y):
        s = hashlib.sha256(bytearray(x + ' ' + y, 'utf8')).hexdigest()
        return 'sha256:' + s

    return reduce(chain_hash, diffs)[7:]

def loadImage():
    """load all images from /var/lib/docker/image/aufs/imagedb/content/sha256
    files under this folder is the image spec json file, the filename is same as image id
    """
    images = []
    content_dir = os.path.join(IMAGE_STORE_DIR, 'content/sha256')
    for content_file in os.listdir(content_dir):
        logging.info('found image: %s' % content_file)
        with open(os.path.join(IMAGE_STORE_DIR, 'content/sha256', content_file)) as content:
            image_content = json.load(content)

        if 'rootfs' in image_content and 'diff_ids' in image_content['rootfs']:
            diffs = image_content['rootfs']['diff_ids']
            if isinstance(diffs, list) and len(diffs) > 0:
                chain_id = chainID(diffs)
                logging.debug('calcuated chain id from diff ids: %s' % chain_id)

                image = {
                    'content_id': content_file,
                    'chain_id': chain_id,
                    'layers': getLayersByChainID(chain_id)
                }
                images.append(image)
            else:
                logging.warn('image content diffs is empty or invalid, skip this image')
        else:
            logging.warn('could not find rootfs diffs in image content, skip this image')
    return images

def getLayersByChainID(chainid):
    """first we find the layer folder with chain id under
    /var/lib/docker/image/aufs/layerdb
    then the file 'cache-id' has the contents of the real layer id
    """
    cache_file = os.path.join(LAYER_STORE_DIR, 'sha256', chainid, 'cache-id')
    if not os.path.isfile(cache_file):
        logging.info('no cache-id file found for this chain id: %s', chainid)
        return []

    with open(cache_file) as data_file:
        cache_id = data_file.read()

    if len(cache_id) == 0:
        logging.info('cache-id file is empty, no layers for this chain id:%s' % chainid)
        return []

    logging.debug('found cache id for chain id %s -> %s' % (chainid, cache_id))
    return getLayersByCacheID(cache_id)

def getLayersByCacheID(cache_id):
    """read the layer list in layer file /var/lib/docker/aufs/layers/<cache-id>"""
    layers = []
    if len(cache_id) == 0:
        return layers

    layers.append(cache_id)
    layer_file = os.path.join(AUFS_LAYER_DIR, cache_id)

    if os.path.isfile(layer_file):
        logging.debug('reading layers in layer file: %s' % layer_file)
        with open(layer_file) as data_file:
            layer_content = data_file.read().strip()
            if len(layer_content) == 0:
                logging.warn('layer file content is empty, no following layers for %s', layer_file)
            else:
                layers.extend(data_file.read().splitlines())
    else:
        logging.warn('no layer file found for id: %s' % cache_id)

    return layers

def loadContainer():
    """find all container id from /var/lib/docker/containers
    then we found the mounts dir under /var/lib/docker/image/aufs/layerdb
    the mount-id file has the real layer id in aufs/layers folder
    """
    containers = []
    for container_id in os.listdir(CONTAINER_DIR):
        logging.info('found contianer %s' % container_id)

        mount_dir = os.path.join(LAYER_STORE_DIR, 'mounts', container_id)
        mount_id_file = os.path.join(mount_dir, 'mount-id')

        if os.path.isfile(mount_id_file):
            with open(mount_id_file) as mount_id_data:
                mount_id = mount_id_data.read()
            if len(mount_id) == 0:
                logging.warn('mount id is empty, no layers for this container')
                layers = []
            else:
                logging.debug('found mount id for this container: %s' % mount_id)
                layers = getLayersByCacheID(mount_id)

            containers.append({'id': container_id, 'layers': layers})
        else:
            logging.warn('could not find mount-id file for this container, skip it')

    return containers

def findAufsMountLayers():
    """this is an extra place to check to ensure we do not remove any mounted
    aufs folders
    """
    layers = []
    with open('/proc/mounts') as mount_data:
        mounts = mount_data.read().splitlines()
    for mount in mounts:
        mount_point = mount.split(' ')[1]
        if mount_point.startswith('/var/lib/docker/aufs/mnt/'):
            logging.debug('found aufs mount point: %s' % mount_point)
            layer = mount_point[len('/var/lib/docker/aufs/mnt/'):]
            layers.append(layer)
    return layers

def removeDirs(dirs):
    for dirname in dirs:
        if os.path.isdir(dirname):
            logging.info('deleting directory %s ...', dirname)
            shutil.rmtree(dirname, ignore_errors=True)
        else:
            logging.warn('not a directory: %s', dirname)

def main():
    args = parseArg()

    logging.basicConfig(level=args.loglevel)

    images = loadImage()
    containers = loadContainer()
    aufs_mount_layers = set(findAufsMountLayers())

    logging.info('analyzing layers...')

    all_image_layers = set([layer for image in images for layer in image['layers']])
    all_container_layers = set([layer for container in containers for layer in container['layers']])
    all_layers = all_image_layers | all_container_layers | aufs_mount_layers

    logging.info('found %d layers in use:', len(all_layers))

    all_mounts = set(os.listdir(AUFS_MNT_DIR))
    if not all_mounts >= all_layers:
        logging.warn('some layers is not in aufs/layers/mnt folder, something is wrong')

    unused_mounts = all_mounts - all_layers
    if len(unused_mounts) == 0:
        logging.info('no unused mounts')
    else:
        logging.info('found %d unused mounts: ' % len(unused_mounts))
        mount_path = [os.path.join(AUFS_MNT_DIR, mount) for mount in unused_mounts]

    all_diffs = set(os.listdir(AUFS_DIFF_DIR))
    if not all_diffs >= all_layers:
        logging.warn('some layers is not in aufs/layers/diffs folder, something is wrong')
    unused_diffs = all_diffs - all_layers
    if len(unused_diffs) == 0:
        logging.info('no unused diffs')
    else:
        logging.info('found %d unused diffs: ' % len(unused_diffs))
        diff_path = [os.path.join(AUFS_DIFF_DIR, diff) for diff in unused_diffs]
        logging.debug('%s', '\n'.join(diff_path))

    if len(mount_path) == 0 and len(diff_path) == 0:
        return

    if not args.dryrun:
        if args.yes:
            logging.info('deleting all unused mount and diff directories')
            removeDirs(mount_path)
            removeDirs(diff_path)
        else:
            s = input('Deleting all unused diffs? (Y/n)').lower()
            if s in ['yes', 'y']:
                removeDirs(mount_path)
                removeDirs(diff_path)

def parseArg():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--debug',
        help="Print lots of debugging statements",
        action="store_const", dest="loglevel", const=logging.DEBUG,
        default=logging.INFO,
    )
    parser.add_argument(
        '-v', '--verbose',
        help="Be verbose",
        action="store_const", dest="loglevel", const=logging.INFO,
    )
    parser.add_argument(
        '-r', '--dry-run',
        help="Dry run, don't do actual deleting",
        action="store_true", dest="dryrun"
    )
    parser.add_argument(
        '-y', '--yes',
        help="assume all answers yes",
        action="store_true"
    )
    return parser.parse_args()

if __name__ == '__main__':
    main()
