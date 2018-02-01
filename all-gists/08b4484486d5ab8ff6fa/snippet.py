def shift_letters(string, shift):
    new_string = ""

    for char in string:
        if char.isupper():
            end_ord = 90 # Z
        elif char.islower():
            end_ord = 122 # z
        else:
            # Skip non-letters
            new_string += char
            continue

        letter_num = ord(char) + shift

        # Shift down into range of letters, if necessary
        if letter_num > end_ord:
            letter_num -= 26

        new_letter = chr(letter_num)
        new_string += new_letter

    return new_string
