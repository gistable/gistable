"""
Vaporwave a string
"""

def glyph(letter):
    """Returns the full-width character of a given character
    Usage::

      >>> glyph("p")
      'ｐ'
      >>> glyph("X")
      'Ｘ'
    """
    return ("ａ" if letter == "a" else
            "ｂ" if letter == "b" else
            "ｃ" if letter == "c" else
            "ｄ" if letter == "d" else
            "ｅ" if letter == "e" else
            "ｆ" if letter == "f" else
            "ｇ" if letter == "g" else
            "ｈ" if letter == "h" else
            "ｉ" if letter == "i" else
            "ｌ" if letter == "l" else
            "ｍ" if letter == "m" else
            "ｎ" if letter == "n" else
            "ｏ" if letter == "o" else
            "ｐ" if letter == "p" else
            "ｑ" if letter == "q" else
            "ｒ" if letter == "r" else
            "ｓ" if letter == "s" else
            "ｔ" if letter == "t" else
            "ｕ" if letter == "u" else
            "ｖ" if letter == "v" else
            "ｗ" if letter == "w" else
            "ｘ" if letter == "x" else
            "ｙ" if letter == "y" else
            "ｚ" if letter == "z" else
            "Ａ" if letter == "A" else
            "Ｂ" if letter == "B" else
            "Ｃ" if letter == "C" else
            "Ｄ" if letter == "D" else
            "Ｅ" if letter == "E" else
            "Ｆ" if letter == "F" else
            "Ｇ" if letter == "G" else
            "Ｈ" if letter == "H" else
            "Ｉ" if letter == "I" else
            "Ｌ" if letter == "L" else
            "Ｍ" if letter == "M" else
            "Ｎ" if letter == "N" else
            "Ｏ" if letter == "O" else
            "Ｐ" if letter == "P" else
            "Ｑ" if letter == "Q" else
            "Ｒ" if letter == "R" else
            "Ｓ" if letter == "S" else
            "Ｔ" if letter == "t" else
            "Ｕ" if letter == "U" else
            "Ｖ" if letter == "V" else
            "Ｗ" if letter == "W" else
            "Ｘ" if letter == "X" else
            "Ｙ" if letter == "Y" else
            "Ｚ" if letter == "Z" else
            "１" if letter == "1" else
            "２" if letter == "2" else
            "３" if letter == "3" else
            "４" if letter == "4" else
            "５" if letter == "5" else
            "６" if letter == "6" else
            "７" if letter == "7" else
            "８" if letter == "8" else
            "９" if letter == "9" else
            "０" if letter == "0" else
            letter)


def vaporwave(word):
    """Returns the string with full-width characters
    Usage::

      >>> vaporwave("vaporwave")
      'ｖａｐｏｒｗａｖｅ'
      >>> vaporwave("AESTHETICS")
      'ＡＥＳTＨＥTＩＣＳ'
    """
    return "".join([glyph(letter) for letter in str(word)])
