from subprocess import call, Popen, PIPE
from getpass import getpass
import sys

def keychain_wrapper(func):
    @wraps(func)
    def wrapper(service_name, username):
        p = Popen(['security', 'find-internet-password', '-g', '-s', service_name, '-a', username],
                  shell=False, stdout=PIPE, stderr=PIPE)
        rc = p.wait()

        if rc == 0:
            # Security prints the password to stderr for some crazy reason:
            for i in p.communicate()[1].split("\n"):
                if i.startswith("password:"):
                    return i.split(":")[1].strip().strip('"')

        pw = getpass("Password for user %s at %s: " % (username, service_name))

        rc = call(['security', 'add-internet-password', '-s', service_name, '-a', username, '-w', pw])

        if rc != 0:
            print("Unable to save password to Keychain!", file=sys.stderr)

        return pw
    return wrapper