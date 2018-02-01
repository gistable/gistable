import re
import gnupg
import logging

log = logging.getLogger(__name__)
GPG_HEADER = re.compile(r'-----BEGIN PGP MESSAGE-----')
GPG_HOMEDIR = '/etc/salt/gpgkeys'


def decrypt_ciphertext(c, gpg):
    decrypted_data = gpg.decrypt(c)
    if not decrypted_data.ok:
        log.critical("Could not decrypt cipher {0}, received {1}".format(
            c, decrypted_data.stderr))
        return c
    else:
        return str(decrypted_data)


def decrypt_object(o, gpg):
    if isinstance(o, str):
        if GPG_HEADER.search(o):
            return decrypt_ciphertext(o, gpg)
        else:
            return o
    elif isinstance(o, dict):
        for k, v in o.items():
            o[k] = decrypt_object(v, gpg)
        return o
    elif isinstance(o, list):
        return [decrypt_object(e, gpg) for e in o]
    else:
        return o


def render(data, saltenv='base', sls='', argline='', **kwargs):
    gpg = gnupg.GPG(gnupghome=GPG_HOMEDIR)
    return decrypt_object(data, gpg)
