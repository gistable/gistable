# Create a SSH connection
import paramiko
import os

ssh = paramiko.SSHClient()
ssh._policy = paramiko.WarningPolicy()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh_config = paramiko.SSHConfig()
user_config_file = os.path.expanduser("~/.ssh/config")
if os.path.exists(user_config_file):
    with open(user_config_file) as f:
        ssh_config.parse(f)

cfg = {'hostname': environment}

user_config = ssh_config.lookup(cfg['hostname'])
cfg["hostname"] = user_config["hostname"]
cfg["username"] = user_config["user"]
key=paramiko.RSAKey.from_private_key_file("/home/cebrian/.ssh/id_rsa")
cfg["pkey"] = key

if 'proxycommand' in user_config:
    cfg['sock'] = paramiko.ProxyCommand(user_config['proxycommand'])

ssh.connect(**cfg)

stdin, stdout, stderr = ssh.exec_command("ls -l /tmp")
print stdout.read()