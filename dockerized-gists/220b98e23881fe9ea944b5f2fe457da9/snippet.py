def str_base(number, base):
    div, mod = divmod(number, len(base))
    if div > 0:
        return str_base(div, base) + base[mod]
    return base[mod]
