import hashlib as hash

# Specify how many bytes of the file you want to open at a time
BLOCKSIZE = 65536

sha = hash.sha256()
with open('kali.iso', 'rb') as kali_file:
    file_buffer = kali_file.read(BLOCKSIZE)
    while len(file_buffer) > 0:
        sha.update(file_buffer)
        file_buffer = kali_file.read(BLOCKSIZE)
        
print sha.hexdigest()