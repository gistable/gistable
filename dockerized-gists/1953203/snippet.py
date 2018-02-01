# -*- coding:utf-8 -*-
import sys
import numpy.random
import itertools


class GostCrypt(object):
    def __init__(self, key, sbox):
        assert self._bit_length(key) <= 256
        self._key = None
        self._subkeys = None
        self.key = key
        self.sbox = sbox

    @staticmethod
    def _bit_length(value):
        return len(bin(value)[2:]) #remove '0b' at start

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, key):
        assert self._bit_length(key) <= 256
        #Для генерации подключей исходный 256-битный ключ разбивается на восемь 32-битных блоков: K1…K8.
        self._key = key
        self._subkeys = [(key >> (32 * i)) & 0xFFFFFFFF for i in range(8)] #8 кусков


    def _f(self, part, key):
        """Функция шифрования (выполняется в раудах)"""
        assert self._bit_length(part) <= 32
        assert self._bit_length(part) <= 32
        temp = part ^ key #складываем по модулю
        output = 0
        #разбиваем по 4бита
        #в рез-те sbox[i][j] где i-номер шага, j-значение 4битного куска i шага
        #выходы всех восьми S-блоков объединяются в 32-битное слово
        for i in range(8):
            output |= ((self.sbox[i][(temp >> (4 * i)) & 0b1111]) << (4 * i))
            #всё слово циклически сдвигается влево (к старшим разрядам) на 11 битов.
        return ((output >> 11) | (output << (32 - 11))) & 0xFFFFFFFF


    def _decrypt_round(self, left_part, right_part, round_key):
        return left_part, right_part ^ self._f(left_part, round_key)

    def encrypt(self, plain_msg):
        "Шифрование исходного сообщения"

        def _encrypt_round(left_part, right_part, round_key):
            return right_part, left_part ^ self._f(right_part, round_key)

        assert isinstance(plain_msg, (int, long))
        assert self._bit_length(plain_msg) <= 64
        #открытый текст сначала разбивается на две половины
        #(младшие биты — rigth_path, старшие биты — left_path)
        left_part = plain_msg >> 32
        right_part = plain_msg & 0xFFFFFFFF
        #Выполняем 32 рауда со своим подключом Ki
        #Ключи K1…K24 являются циклическим повторением ключей K1…K8 (нумеруются от младших битов к старшим).
        for i in range(24):
            left_part, right_part = _encrypt_round(left_part, right_part, self._subkeys[i % 8])
            #Ключи K25…K32 являются ключами K1…K8, идущими в обратном порядке.
        for i in range(8):
            left_part, right_part = _encrypt_round(left_part, right_part, self._subkeys[7 - i])
        return (left_part << 32) | right_part #сливаем половинки вместе

    def decrypt(self, crypted_msg):
        """Дешифрование криптованого сообщения
        Расшифрование выполняется так же, как и зашифрование, но инвертируется порядок подключей Ki."""

        def _decrypt_round(left_part, right_part, round_key):
            return right_part ^ self._f(left_part, round_key), left_part

        assert isinstance(crypted_msg, (int, long))
        assert self._bit_length(crypted_msg) <= 64
        left_part = crypted_msg >> 32
        right_part = crypted_msg & 0xFFFFFFFF
        for i in range(8):
            left_part, right_part = _decrypt_round(left_part, right_part, self._subkeys[i])
        for i in range(24):
            left_part, right_part = _decrypt_round(left_part, right_part, self._subkeys[(7 - i) % 8])
        return (left_part << 32) | right_part #сливаем половинки вместе

def main(argv=None):
    if argv is None:
        argv = sys.argv
    sbox = [numpy.random.permutation(l) for l in itertools.repeat(range(16), 8)]
    sbox = (
        (4, 10, 9, 2, 13, 8, 0, 14, 6, 11, 1, 12, 7, 15, 5, 3),
        (14, 11, 4, 12, 6, 13, 15, 10, 2, 3, 8, 1, 0, 7, 5, 9),
        (5, 8, 1, 13, 10, 3, 4, 2, 14, 15, 12, 7, 6, 0, 9, 11),
        (7, 13, 10, 1, 0, 8, 9, 15, 14, 4, 6, 12, 11, 2, 5, 3),
        (6, 12, 7, 1, 5, 15, 13, 8, 4, 10, 9, 14, 0, 3, 11, 2),
        (4, 11, 10, 0, 7, 2, 1, 13, 3, 6, 8, 5, 9, 12, 15, 14),
        (13, 11, 4, 1, 3, 15, 5, 9, 0, 10, 14, 7, 6, 8, 2, 12),
        (1, 15, 13, 0, 5, 7, 10, 4, 9, 2, 3, 14, 6, 11, 8, 12),
        )
    text = 0xfedcba0987654321
    key = 18318279387912387912789378912379821879387978238793278872378329832982398023031
    gost = GostCrypt(key, sbox)
    crypted_text = gost.encrypt(text)
    encrypted_text = gost.decrypt(crypted_text)
    assert text == encrypted_text
    print 'plain text', text
    print 'crypted text', crypted_text
    print 'encrypted text', encrypted_text

if __name__ == "__main__":
    main()
