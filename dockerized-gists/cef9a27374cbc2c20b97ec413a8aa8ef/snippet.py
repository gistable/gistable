def is_iso(word):
    if not type(word) is str:
        raise TypeError("Argument should be a string")
    if len(word) == 0:
        return word, False
    word = word.lower()
    for char in word:
        if word.count(char) > 1:
            return tuple(word), False
    return tuple(word), True



print(is_iso("subdermatoglyphic"))
print(is_iso("uncopyrightables"))
print(is_iso("ambidextrously"))
print(is_iso("Goods"))
print(is_iso("Effort"))
print(is_iso("Moose"))
