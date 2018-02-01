def count_ones(hex_str):
    def count_char(n):
        mapping = lambda m: (m + 1) / 2

        return mapping(n % 4) + mapping(n / 4)

    return sum([count_char(int(char, 16)) for char in hex_str])

assert count_ones('aac8') == 7
assert count_ones('0') == 0
assert count_ones('f') == 4
