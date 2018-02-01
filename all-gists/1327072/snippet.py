# A simple Django utility function for encrypting data using GnuPG
#
# https://gist.github.com/1327072


import os
import subprocess
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings


GPG_BIN = getattr(settings, 'GPG_BIN', '/usr/bin/gpg')
GPG_KEYRING_FILE = getattr(settings, 'GPG_KEYRING_FILE', '')
GPG_KEY_IDS = getattr(settings, 'GPG_KEY_IDS', [])


if not os.access(GPG_BIN, os.X_OK):
    raise ImproperlyConfigured, "Cannot find GnuPG binary at %s" % GPG_BIN


class EncryptionError(Exception):
    """
    This exception is raised to indicate that an error occurred during the
    encryption process. The exception value will be the STDERR output of gpg,
    so this exception should be swallowed by the calling process unless running
    in debug mode.
    """

    pass


def encrypt(data, key_ids=None):
    """
    Encrypt data with the public keys as specified as key_ids of the
    application keyring. Data may contain unicode characters, which are sent
    to GPG as UTF-8 data.
    """

    if not key_ids:
        key_ids = GPG_KEY_IDS

    args = [
        GPG_BIN,
        '--encrypt',
        '--no-options',
        '--trust-model',
        'always',
        '--batch',
        '--armor',
    ]

    if GPG_KEYRING_FILE:
        args += ['--no-default-keyring', '--keyring', GPG_KEYRING_FILE]

    for key_id in key_ids:
        args += ['--recipient', key_id]

    try:
        gpg = subprocess.Popen(
            args,
            bufsize = 4096,
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
        )
        output = gpg.communicate(data.encode('utf8'))
        if gpg.returncode != 0:
            raise EncryptionError, "%d: %s" % (gpg.returncode, output[1])
        return output[0]
    except OSError, e:
        raise EncryptionError, e
