#!/bin/env/python
import hashlib
import binascii

# Utility methods for generating and comparing RabbitMQ user password hashes.
#
# Rabbit Password Hash Algorithm:
# 
# Generate a random 32 bit salt: 
# CA D5 08 9B 

# Concatenate that with the UTF-8 representation of the password (in this 
# case "simon"): 
# CA D5 08 9B 73 69 6D 6F 6E 

# Take the MD5 hash: 
# CB 37 02 72 AC 5D 08 E9 B6 99 4A 17 2B 5F 57 12 

# Concatenate the salt again: 
# CA D5 08 9B CB 37 02 72 AC 5D 08 E9 B6 99 4A 17 2B 5F 57 12 

# And convert to base64 encoding: 
# ytUIm8s3AnKsXQjptplKFytfVxI= 
# 
# Sources:
# http://rabbitmq.1065348.n5.nabble.com/Password-Hashing-td276.html
# http://hg.rabbitmq.com/rabbitmq-server/file/df7aa5d114ae/src/rabbit_auth_backend_internal.erl#l204 

# Test Case:
#   print encode_rabbit_password_hash('CAD5089B', "simon")
#   print decode_rabbit_password_hash('ytUIm8s3AnKsXQjptplKFytfVxI=')
#   print check_rabbit_password('simon','ytUIm8s3AnKsXQjptplKFytfVxI=')

def encode_rabbit_password_hash(salt, password):
    salt_and_password = salt + password.encode('utf-8').encode('hex')
    salt_and_password = bytearray.fromhex(salt_and_password)
    salted_md5 = hashlib.md5(salt_and_password).hexdigest()
    password_hash = bytearray.fromhex(salt + salted_md5)
    password_hash = binascii.b2a_base64(password_hash).strip()
    return password_hash

def decode_rabbit_password_hash(password_hash):
    password_hash = binascii.a2b_base64(password_hash)
    decoded_hash = password_hash.encode('hex')
    return (decoded_hash[0:8], decoded_hash[8:])

def check_rabbit_password(test_password, password_hash):
    salt, hash_md5sum = decode_rabbit_password_hash(password_hash)
    test_password_hash = encode_rabbit_password_hash(salt, test_password)
    return test_password_hash ==  password_hash