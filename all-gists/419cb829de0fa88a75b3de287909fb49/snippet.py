import re

ie_r = re.compile(r'ei|ie')
follows_r = re.compile(r'cei|[^c]ie')
does_not_follow_r = re.compile(r'cie|[^c]ei')

words = 0
ie = 0
follows = 0
does_not_follow = 0

with open('words_alpha.txt', 'r') as fp:
    for word in fp:
        words += 1
        if ie_r.search(word):
            ie += 1
        if follows_r.search(word):
            follows += 1
        if does_not_follow_r.search(word):
            does_not_follow += 1

print(f"{words} words evaluated.")
print(f"{ie} words with ie/ei combos.")
print(f"{follows} words following i before e except after c rule.")
print(f"{does_not_follow} words breaking rule.")
