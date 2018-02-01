import paramiko
import time
import re

bastion_ip='ip'
bastion_pass='pass'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
ssh.connect(bastion_ip, username='root', password=bastion_pass)

chan = ssh.invoke_shell()

# other cloud server 
priv_ip='ip'
passw='pass'

test_script='/root/check_rackconnect.sh'
   
def run_cmd(cmd):
    buff = ''
    while not buff.endswith(':~# '):
        resp = chan.recv(9999)
        buff += resp
        print(resp)

    # Ssh and wait for the password prompt.
    chan.send(cmd + '\n')

    buff = ''
    while not buff.endswith('\'s password: '):
        resp = chan.recv(9999)
        buff += resp
        print(resp)
    
    # Send the password and wait for a prompt.
    time.sleep(3)
    chan.send(passw + '\n')

    buff = ''
    while buff.find(' done.') < 0 :
        resp = chan.recv(9999)
        buff += resp
        print(resp)
       
    ret=re.search( '(\d) done.', buff).group(1)
    ssh.close()

    print('command was successful:' + str(ret=='0'))

scp_opt=""
cmd='scp -q ' + scp_opt + ' -o NumberOfPasswordPrompts=1 -o StrictHostKeyChecking=no %s root@%s:~/; echo $? done.' % ( test_script, priv_ip )
print('\n test 2\n cmd %s\n' % cmd)
run_cmd(cmd)
