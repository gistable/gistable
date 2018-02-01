"""
Store this file as `vars_plugins/password_from_keyring.py` and specify the
following in `ansible.cfg`:

```
    [defaults]
    vars_plugins=./vars_plugins
```

In your inventory specify:
```
[group1]
web[01:99].server.lan

[group1:vars]
x_auth_system="Old Auth Shell User"

[group2]
db[01:10].server.lan

[group2:vars]
x_auth_system="New Auth Shell User"

[shellhosts]
sh01.server.lan
another.server.lan x_auth_system="Standard Shell User"


[all:vars]
ansible_ask_sudo_pass=true
x_auth_system="New Auth Shell User"
```
"""
import getpass
import keyring
import os
import sys

class VarsModule(object):

    """
    Loads variables for groups and/or hosts
    """

    def __init__(self, inventory):
        """ constructor """
        self.inventory = inventory
        self.inventory_basedir = inventory.basedir()


    def get_host_vars(self, host, vault_password=None):
        """ Get host specific variables. """
        if "-s" in sys.argv or "--sudo" in sys.argv:
            x_auth_system = host.get_variables().get("x_auth_system")
            if VarsModule.sudo_password.get(x_auth_system) is None:
                if x_auth_system == "Old Auth Shell User":
                    user = os.environ.get("OLD_AUTH_SHELL_USER")
                    VarsModule.remote_user[x_auth_system] = user
                    passwd = keyring.get_password(x_auth_system, user)
                if x_auth_system == "New Auth Shell User":
                    user = os.environ.get("NEW_AUTH_SHELL_USER")
                    VarsModule.remote_user[x_auth_system] = user
                    passwd = keyring.get_password(x_auth_system, user)
                elif x_auth_system == "Standard Shell User":
                    user = os.environ.get("USER")
                    VarsModule.remote_user[x_auth_system] = user
                    passwd = keyring.get_password(x_auth_system, user)
                elif x_auth_system == "Vagrant Shell User":
                    VarsModule.remote_user[x_auth_system] = "vagrant"
                    passwd = "vagrant"
                else:
                    raise Exception("Unknown Authentication System %s for host %s" % (x_auth_system, host.name))
                if passwd is None:
                    passwd = getpass.getpass(prompt="%s: sudo password" % x_auth_system)
                VarsModule.sudo_password[x_auth_system] = passwd
            host.set_variable('ansible_sudo_pass', VarsModule.sudo_password[x_auth_system])
            host.set_variable('ansible_ssh_user', VarsModule.remote_user[x_auth_system])
VarsModule.sudo_password = {}
VarsModule.remote_user = {}
