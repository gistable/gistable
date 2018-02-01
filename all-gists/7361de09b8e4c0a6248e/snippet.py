# After seeing Ex Machina I tweeted:
# "So disappointed in #ExMachina -- the #Python wasn't PEP8 compatible..."
# https://twitter.com/twiecki/status/599615426922938368
# For the original code in the movie as well as what it does (it's kinda neat), see:
# http://moviecode.tumblr.com/post/119171520870/in-the-movie-ex-machina-which-is-really-great

# To put my code where my mouth is, I decided to make the code PEP8 compatible which you can see below.
# I also did some minor cosmetic changes like changing i = i + 1 to i += 1
# Other ideas for improvements? Comment below.

# BlueBook code decryption

import sys


def sieve(n):
    x = [1] * n
    x[1] = 0
    for i in range(2, n/2):
        j = 2 * i
        while j < n:
            x[j] = 0
            j += i
    return x


def prime(n, x):
    i = 1
    j = 1
    while j < n:
        if x[i] == 1:
            j += 1
        i += 1
    return i - 1

x = sieve(10000)
code = [1206, 301, 384, 5]
key = [1, 1, 2, 2]

sys.stdout.write("".join(chr(i) for i in [73, 83, 66, 78, 32, 61, 32]))

for i in range(4):
    sys.stdout.write(str(prime(code[i], x) - key[i]))
