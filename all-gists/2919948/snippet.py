import hashlib


class FeistelSHA1:
    rounds = 4  # 4 rounds is sufficient as long as the round function is cryptographically secure
    split = 1 / 2

    def __init__(self, key, rounds=rounds):
        self.subkeys = [hashlib.sha1(bytes((i,)) + key).digest() for i in range(rounds)]

    def encipher(self, data):
        split = int(len(data) * self.split)
        d1 = data[:split]
        d2 = data[split:]
        for sk in self.subkeys:
            d1, d2 = self.round(sk, d1, d2)
        return d1 + d2

    def decipher(self, data):
        split = int(len(data) * self.split)
        d1 = data[:split]
        d2 = data[split:]
        for sk in reversed(self.subkeys):
            d2, d1 = self.round(sk, d2, d1)
        return d1 + d2

    def round(self, subkey, d1, d2):
        # Note that d1 is only used to determine the *length* of the pad,
        # but not any of the actual content. In a Feistel cipher, only d2
        # and the subkey are used as inputs to determine the pad. Another
        # way to think of it is the pad being infinitely long, and we only
        # evalute as much of it as we need to.
        #
        # If your data will be fixed-size, you can replace all but the last line
        # with calculating a pad of (at least) your required length, for example:
        #
        # pad = hashlib.sha1(d2 + subkey).digest()

        padparts = ()
        padseed = d2
        for i in range((len(d1) + 19) // 20):
            padseed2 = hashlib.sha1(padseed + subkey).digest()
            padparts += padseed2,=
            padseed = padseed2
        pad = sum(padparts, b'')

        return d2, bytes(d ^ p for d, p in zip(d1, pad))
