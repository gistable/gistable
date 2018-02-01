import os
import paramiko
paramiko.util.log_to_file('/tmp/paramiko.log')
paramiko.util.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))

host = 'local'
port = 22
username = 'user'

files = ['file1', 'file2', 'file3', 'file4']
remote_images_path = '/remote_path/images/'
local_path = '/tmp/'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())
ssh.connect(hostname=host, port=port, username=username)
sftp = ssh.open_sftp()

for file in file:
    file_remote = remote_images_path + file
    file_local = local_path + file

    print file_remote + '>>>' + file_local

    sftp.get(file_remote, file_local)

sftp.close()
ssh.close()