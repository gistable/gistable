#! /usr/bin/env python2

"""
encfs-agent 

Mounts encfs filesystems with passwords generated using private keys stored in ssh-agent.
You can have any number of encrypted filesystems ("vaults") under VAULTS_DIR. Password for 
each of them is derived from its name and given private key stored in ssh-agent.
You can use ssh-askpass for ssh-agent if you want.

Adapted from code from http://ptspts.blogspot.cz/2010/06/how-to-use-ssh-agent-programmatically.html
Thank you, pts!

------------------ REQUIREMENTS
  - python 2.x
  - correctly configured ssh-agent (test with "ssh-add -L")

------------------ INSTALL

## download encfs-agent file and adjust VAULTS_DIR and MNT_DIR variables in it if you don't like the defaults
## defaults are:
##    vaults stored in ~/.vaults
##    vaults mounted under /mnt/vaults

## Ready! You can test it...

## set following variables appropriately (use the same values as in the previous step)
EA=~/bin/encfs-agent
VAULTS_DIR=~/.vaults
MNT_DIR=/mnt/vaults

chmod +x "$EA"
mkdir -p "$MNT_DIR"
mkdir -p "$VAULTS_DIR"

## create first vault...
$EA mount first
  -- encfs will prompt you for some settings for a newly created fs...
echo test > $MNT_DIR/first/test
umount $MNT_DIR/first

## see the encrypted directory...
ls -la "$VAULTS_DIR/first"

## mount it again...
$EA mount first
cat $MNT_DIR/first/test
umount $MNT_DIR/first

## and again...
$EA passwd first | encfs --extpass='cat' "$VAULTS_DIR/first" "$MNT_DIR/first"
cat /mnt/vaults/first/test
umount /mnt/vaults/first

------------------ NOTE

ssh-agent client sends arbitrary string to the agent. Agent makes SHA-1 hash of it and encrypts the
hash with a chosen private key. SHA-1 hashes are 160 bit long, so we can get only precisely
160 bits long passwords.

"""

import cStringIO
import os
import os.path
import re
import sha
import socket
import struct
import sys
import subprocess

# adjust this for your system...
VAULTS_DIR=os.path.join(os.getenv('HOME'),'.vaults')
MNT_DIR="/mnt/vaults"


# no user serviceable parts below this line  



SSH2_AGENTC_REQUEST_IDENTITIES = 11
SSH2_AGENT_IDENTITIES_ANSWER = 12
SSH2_AGENTC_SIGN_REQUEST = 13
SSH2_AGENT_SIGN_RESPONSE = 14
SSH_AGENT_FAILURE = 5

def recv_all(sock, size):
  if size == 0:
    return ''
  assert size >= 0
  if hasattr(sock, 'recv'):
    recv = sock.recv
  else:
    recv = sock.read
  data = recv(size)
  if len(data) >= size:
    return data
  assert data, 'unexpected EOF'
  output = [data]
  size -= len(data)
  while size > 0:
    output.append(recv(size))
    assert output[-1], 'unexpected EOF'
    size -= len(output[-1])
  return ''.join(output)

def recv_u32(sock):
  return struct.unpack('>L', recv_all(sock, 4))[0]

def recv_str(sock):
  return recv_all(sock, recv_u32(sock))

def append_str(ary, data):
  assert isinstance(data, str)
  ary.append(struct.pack('>L', len(data)))
  ary.append(data)

# Get list of public keys, and find our key.
def get_pubkey(sock,key_comment):
  sock.sendall('\0\0\0\1\v') # SSH2_AGENTC_REQUEST_IDENTITIES
  response = recv_str(sock)
  resf = cStringIO.StringIO(response)
  assert recv_all(resf, 1) == chr(SSH2_AGENT_IDENTITIES_ANSWER)
  num_keys = recv_u32(resf)
  assert num_keys < 2000  # A quick sanity check.
  assert num_keys, 'no keys have_been added to ssh-agent'
  matching_keys = []
  for i in xrange(num_keys):
    key = recv_str(resf)
    comment = recv_str(resf)
    if comment == key_comment:
      matching_keys.append(key)
  assert '' == resf.read(1), 'EOF expected in resf'
  assert matching_keys, 'no keys in ssh-agent with comment %r' % key_comment
  assert len(matching_keys) == 1, (
      'multiple keys in ssh-agent with comment %r' % key_comment)
  assert matching_keys[0].startswith('\x00\x00\x00\x07ssh-rsa\x00\x00'), (
      'non-RSA key in ssh-agent with comment %r' % key_comment)
  keyf = cStringIO.StringIO(matching_keys[0][11:])
  public_exponent = int(recv_str(keyf).encode('hex'), 16)
  modulus_str = recv_str(keyf)
  modulus = int(modulus_str.encode('hex'), 16)
  assert '' == keyf.read(1), 'EOF expected in keyf'
  return (matching_keys[0],public_exponent,modulus,len(modulus_str))

# Ask ssh-agent to sign with our key.
def sign(sock,pub_key,msg_to_sign):
  request_output = [chr(SSH2_AGENTC_SIGN_REQUEST)]
  append_str(request_output, pub_key)
  append_str(request_output, msg_to_sign)
  request_output.append(struct.pack('>L', 0))  # flags == 0
  full_request_output = []
  append_str(full_request_output, ''.join(request_output))
  full_request_str = ''.join(full_request_output)
  sock.sendall(full_request_str)
  response = recv_str(sock)
  resf = cStringIO.StringIO(response)
  assert recv_all(resf, 1) == chr(SSH2_AGENT_SIGN_RESPONSE)
  signature = recv_str(resf)
  assert '' == resf.read(1), 'EOF expected in resf'
  assert signature.startswith('\0\0\0\7ssh-rsa\0\0')
  sigf = cStringIO.StringIO(signature[11:])
  signed_value = int(recv_str(sigf).encode('hex'), 16)
  assert '' == sigf.read(1), 'EOF expected in sigf'
  return signed_value

# Verify the signature.
def verify_signature(signed_value,pub_exponent,pub_modulus,pub_modlen,msg_to_sign):
  decoded_value = pow(signed_value, pub_exponent, pub_modulus)
  decoded_hex = '%x' % decoded_value
  if len(decoded_hex) & 1:
    decoded_hex = '0' + decoded_hex
  decoded_str = decoded_hex.decode('hex')
  assert len(decoded_str) == pub_modlen - 2  # e.g. (255, 257)
  assert re.match(r'\x01\xFF+\Z', decoded_str[:-36]), 'bad padding found'
  expected_sha1_hex = decoded_hex[-40:]
  msg_sha1_hex = sha.sha(msg_to_sign).hexdigest()
  return expected_sha1_hex == msg_sha1_hex

def usage():
  print """
  {0} converts any string to 160-bit password using private key stored in ssh-agent.
  This password is used to conveniently mount encrypted encfs filesystems.

  usage:

     {0} mount  <vault_name> [ssh_key_file]
        -- mount encfs {1}/<vault_name> to {2}/<vault_name>

     {0} passwd <vault_name> [ssh_key_file]
        -- convert vault_name (or arbitrary string) to password

     vault_name   ... encfs will mount {1}/<vault_name> to {2}/<vault_name>
     ssh_key_file ... key file name (key comment as printed by "ssh-add -L")
""".format(sys.argv[0],VAULTS_DIR,MNT_DIR)
  sys.exit(1)


def main():
  if len(sys.argv)<3:
     usage()

  key_comment = os.path.join(os.getenv('HOME'),'.ssh','id_rsa')
  if len(sys.argv)==4:
     key_comment = sys.argv[3]

  vault = sys.argv[2]

  if sys.argv[1]=='passwd':
     # Connect to ssh-agent.
     assert 'SSH_AUTH_SOCK' in os.environ, (
         'ssh-agent not found, set SSH_AUTH_SOCK')
     sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM, 0)
     sock.connect(os.getenv('SSH_AUTH_SOCK'))
     pub_key,pub_exponent,pub_modulus,pub_modlen = get_pubkey(sock,key_comment)
     passwd = sign(sock,pub_key,vault)
     assert verify_signature(passwd,pub_exponent,pub_modulus,pub_modlen,vault), 'bad signature (SHA1 mismatch)'
     #print "vault=%r password=%r"%(vault,passwd)
     sys.stdout.write("%x"%(passwd,))
  elif sys.argv[1]=='mount':
     mnt_src=os.path.join(VAULTS_DIR,vault)
     mnt_dest=os.path.join(MNT_DIR,vault)
     ## we could pass password by "-extpass=cat", but that will break interaction
     ## with encfs (at first mount, when creating encrypted fs)
     cmd=["encfs", "--extpass='%s' passwd '%s'"%(sys.argv[0],vault),mnt_src,mnt_dest]
     #print '"'+('" "'.join(cmd))+'"'
     subprocess.call(cmd)
  else:
     usage()

  sys.exit(0)


if __name__ == '__main__':
  main()
