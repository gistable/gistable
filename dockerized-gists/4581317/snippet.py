def anti_vowel(text):
    vowels = ["A", "a", "E", "e", "I", "i", "O", "o", "U", "u"]
    anti = []
    for i in text:
        if i in vowels:
            pass
        else:
            anti.append(i)
    return "".join(anti)

print anti_vowel("and i Like apricots")
