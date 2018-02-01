#!/usr/bin/python
import boto
import boto.utils
import subprocess
import logging
import re
import sys
import os
import psutil
import time

#_ Statics
#_ Credentials for ec2-autoscale account
AWS_ACCESS_KEY_ID='blah'
AWS_SECRET_ACCESS_KEY='blah'


def setup_logging():
    """ Setup the logging facility. """
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    hdlr = logging.StreamHandler(sys.stdout)
    hdlr.setLevel(logging.INFO)
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    return logger


def is_mounted(volume):
    """ Return True / False if volume mounted. """
    mounted = []
    try:
        with open('/proc/mounts', 'r') as f:
            mounts = f.readlines()
            for m in mounts:
                if volume in m:
                    return True
    except Exception, e:
        raise e
    return False


def is_formatable(path):
    """ Look at path. Determine if I should format based on rules. """
    whitelist = ['linux_raid_member', 'ext4', 'xfs']
    regex = re.compile('([A-Z]+)=\"([^\s]+)\"')
    try:
        output = subprocess.check_output('blkid -p {}'.format(path), shell=True)
        for m in regex.finditer(output):
            if 'TYPE' in m.group(1):
                if not m.group(2) in whitelist:
                    return True
    except subprocess.CalledProcessError, e:
        return False
    return False


def format_ephemeral(volume, options=['-E lazy_itable_init=1', '-m 0']):
    """ Given a volume, format as EXT4 """
    try:
        output = subprocess.check_output('mkfs.ext4 {} {}'.format(volume, ' '.join(options)), shell=True)
    except subprocess.CalledProcessError, e:
        raise e
    return True


def umount_ephemeral(path):
    """ Unmount an elphemeral volume. """
    try:
        output = subprocess.check_output('umount -f {}'.format(path), shell=True)
    except subprocess.CalledProcessError, e:
        raise e


def mount_ephemeral(volume, options=['nodiratime', 'noatime']):
    """ Create a mount point in /data, mount ephemeral. """
    mount_path = '/data/{}'.format(volume)
    drive_path = '/dev/{}'.format(volume)
    if not os.path.exists(mount_path):
        os.makedirs(mount_path)
    if not is_mounted(drive_path):
        try:
            output = subprocess.check_output('mount -t auto {} {} -o {}'.format(drive_path, mount_path, ','.join(options)), shell=True)
        except subprocess.CalledProcessError, e:
            raise e


#_ Main
def main():
    ephemerals = []
    log = setup_logging()
    log.info('EC2 Mount & Format')

    # Get information
    try:
        log.info('Connecting to EC2')
        conn = boto.connect_ec2(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        metadata = boto.utils.get_instance_metadata()
        log.info('Connection successful: %s' % (conn))
    except Exception, e:
        log.error('Could not connec to EC2')
        sys.exit(1)

    # Verify information
    if 'block-device-mapping' in metadata:
        for mapping in metadata['block-device-mapping']:
            if mapping.startswith('ephemeral'):
                # Transform sd -> xvd
                ephem = metadata['block-device-mapping'][mapping]
                log.info('Appending {} as {}'.format(ephem, ephem.replace('sd', 'xvd')))
                ephemerals.append(ephem.replace('sd', 'xvd'))
        log.info('Ephemeral list: {}'.format(ephemerals))
    else:
        log.error('Could not find ephemeral mapping')
        sys.exit(1)

    # Everythings unmounted. Lets start formatting at ext4
    for m in ephemerals:
        device_path = '/dev/{}'.format(m)
        if is_formatable(device_path):
            log.info('Processing: {}'.format(device_path))
            if is_mounted(device_path):
                log.info('  Unmounting: {}'.format(device_path))
                try:
                    umount_ephemeral(device_path)
                except Exception, e:
                    log.error('Skipping - Unable to unmount {}: {}'.format(device_path, e))
                    continue
            log.info('  Formatting: {}'.format(device_path))
            try:
                format_ephemeral(device_path)
            except Exception, e:
                log.error('Skipping - Unable to format {}: {}'.format(device_path, e))
                continue
        else:
            log.info('Skipped Formatting {}'.format(device_path))
        if not is_mounted(device_path):
            log.info('  Mounting: {}'.format(device_path))
            try:
                mount_ephemeral(m)
            except Exception, e:
                log.error('Skipping - Unable to mount {}: {}'.format(device_path, e))
                continue
    log.info('Complete')


if __name__ == '__main__':
    main()