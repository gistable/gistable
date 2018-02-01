import unittest
import math
import base64
import bz2
import gzip
import StringIO
import struct

class BitSetEncoder(object):
  def encode(self, integers):
    output = 0
    for integer in integers:
      output |= 2**(integer-1)
    return output

  def decode(self, bitset):
    result = []
    for i in range(1, int(math.floor(math.log(bitset, 2))) + 2):
      if 1 & bitset:
        result.append(i)
      bitset >>= 1
    return result

class PackedIntegersEncoder(object):
  def encode(self, integers):
    return Int2ByteEncoder().decode(struct.pack('<' + 'I' * len(integers), *integers))

  def decode(self, bytestring):
    bytestring = Int2ByteEncoder().encode(bytestring)
    return list(struct.unpack('<' + 'I' * (len(bytestring) / 4), bytestring))

class SwitchingBitSetEncoder(object):
  def __init__(self, encoder_one, encoder_two, shell):
    self._encoder_one = encoder_one
    self._encoder_two = encoder_two
    self._shell = shell

  def encode(self, integers):
    res1 = self._shell.encode(self._encoder_one.encode(integers) * 2)
    res2 = self._shell.encode((self._encoder_two.encode(integers) * 2) | 1)

    return res1 if len(res1) < len(res2) else res2

  def decode(self, bytestring):
    bitset = self._shell.decode(bytestring)
    if bitset & 1:
      return self._encoder_two.decode(bitset >> 1)
    else:
      return self._encoder_one.decode(bitset >> 1)

class Int2ByteEncoder(object):
  def encode(self, integer):
    result = ""
    while integer > 0:
      result = chr(integer & 255) + result
      integer >>= 8

    return result

  def decode(self, bytestring):
    return sum(ord(c) << (i * 8) for i, c in enumerate(bytestring[::-1]))

class Base64Encoder(object):
  def encode(self, bytestring):
    return base64.urlsafe_b64encode(bytestring)

  def decode(self, bytestring):
    return base64.urlsafe_b64decode(bytestring)

class Bzip2Encoder(object):
  def encode(self, uncompressed):
    return bz2.compress(uncompressed)

  def decode(self, compressed):
    return bz2.decompress(compressed)

class GzEncoder(object):
  def encode(self, uncompressed):
    sio = StringIO.StringIO()
    gzf = gzip.GzipFile(fileobj=sio, mode="w")
    try:
      gzf.write(uncompressed)
    finally:
      gzf.close()
    return sio.getvalue()

  def decode(self, compressed):
    sio = StringIO.StringIO(compressed)
    gzf = gzip.GzipFile(fileobj=sio, mode="r")
    try:
      return gzf.read()
    finally:
      gzf.close()

class CompositeBitSetEncoder(object):
  def __init__(self, *encoders):
    self._encoders = [encoder() for encoder in encoders]

  def encode(self, result):
    for encoder in self._encoders:
      result = encoder.encode(result)
    return result

  def decode(self, result):
    for encoder in reversed(self._encoders):
      result = encoder.decode(result)
    return result


class BaseBitSetEncoderTest(unittest.TestCase):
  encoder = None

  def test_encode(self):
    if self.encoder:
      self.assertEqual(self.results[0], self.encoder.encode([1, 3]))
      self.assertEqual(self.results[1], self.encoder.encode([1]))
      self.assertEqual(self.results[2], self.encoder.encode([1, 4, 24]))
      self.assertEqual(self.results[3], self.encoder.encode([6, 10, 30, 200]))
      self.assertEqual(self.results[4], self.encoder.encode([320, 450, 520]))
      # self.assertEqual(self.results[5], self.encoder.encode(range(1, 100)))

  def test_decode(self):
    if self.encoder:
      self.assertEqual([1, 3], self.encoder.decode(self.results[0]))
      self.assertEqual([1], self.encoder.decode(self.results[1]))
      self.assertEqual([1, 4, 24], self.encoder.decode(self.results[2]))
      self.assertEqual([6, 10, 30, 200], self.encoder.decode(self.results[3]))
      self.assertEqual([320, 450, 520], self.encoder.decode(self.results[4]))
      # self.assertEqual(range(1, 100), self.encoder.decode(self.results[5]))

  def test_both_ways_on_large(self):
    if self.encoder:
      self.assertEqual([1, 4, 7, 20, 210, 450], self.encoder.decode(self.encoder.encode([1, 4, 7, 20, 210, 450])))

  def test_result_length(self):
    if self.encoder and self.results[5]:
      self.assertEqual(self.results[5], len(self.encoder.encode(range(1, 500))))
      self.assertEqual(range(1, 500), self.encoder.decode(self.encoder.encode(range(1, 500))))


class BitSetEncoderTest(BaseBitSetEncoderTest):
  encoder = CompositeBitSetEncoder(BitSetEncoder)
  results = [5, 1, 8388617,
    803469022129495137770981046170581301261101496891396954522144L,
    1716199415032652428746928877218939518098457472651602361417324215511278392425018190939854273517647735943237638275682715161205933153004583629285587757079461888L,
    False
  ]

class PackedIntegersEncoderTest(BaseBitSetEncoderTest):
  encoder = CompositeBitSetEncoder(PackedIntegersEncoder)
  results = [
    72057594088259584,
    16777216,
    309485010109575445279145984L,
    7975367977804345337798020873423159296L,
    19808249568365153746029772800L,
    False
  ]

class Base64BitSetEncoderTest(BaseBitSetEncoderTest):
  encoder = CompositeBitSetEncoder(BitSetEncoder, Int2ByteEncoder, Base64Encoder)
  results = [
    "BQ==",
    "AQ==",
    "gAAJ",
    "gAAAAAAAAAAAAAAAAAAAAAAAAAAAIAACIA==",
    "gAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
    84
  ]

class Base64PackedIntegersEncoderTest(BaseBitSetEncoderTest):
  encoder = CompositeBitSetEncoder(PackedIntegersEncoder, Int2ByteEncoder, Base64Encoder)
  results = [
    "AQAAAAMAAAA=",
    "AQAAAA==",
    "AQAAAAQAAAAYAAAA",
    "BgAAAAoAAAAeAAAAyAAAAA==",
    "QAEAAMIBAAAIAgAA",
    2664
  ]

class Base64SwitchingBitSetEncoderTest(BaseBitSetEncoderTest):
  encoder = SwitchingBitSetEncoder(
    BitSetEncoder(),
    PackedIntegersEncoder(),
    CompositeBitSetEncoder(Int2ByteEncoder, Base64Encoder)
  )
  results = [
    "Cg==",
    "Ag==",
    "AQAAEg==",
    "DAAAABQAAAA8AAABkAAAAQ==",
    "gAIAAYQCAAAQBAAB",
    84
  ]

class Bzip2Base64BitSetEncoderTest(BaseBitSetEncoderTest):
  encoder = CompositeBitSetEncoder(BitSetEncoder, Int2ByteEncoder, Bzip2Encoder, Base64Encoder)
  results = [
    "QlpoOTFBWSZTWaYyKyAAAABAAAIAIAAhGEaC7kinChIUxkVkAA==",
    "QlpoOTFBWSZTWbU2XfwAAABAACAAIAAhGEaC7kinChIWpsu_gA==",
    "QlpoOTFBWSZTWYYEMXAAAAFAQEAgQAAgACGYGYRhdyRThQkIYEMXAA==",
    "QlpoOTFBWSZTWVNBTCwAAATwQFAAQABAAEAAIAAhg0GaAiIw3F3JFOFCQU0FMLA=",
    "QlpoOTFBWSZTWcmNRnUAAAhQQFgECABAACAAIYTagwAsrS6MPF3JFOFCQyY1GdQ=",
    60
  ]

class GzipBase64BitSetEncoderTest(BaseBitSetEncoderTest):
  encoder = CompositeBitSetEncoder(BitSetEncoder, Int2ByteEncoder, GzEncoder, Base64Encoder)
  results = [
    "H4sIAIOUoU8C_2MFAAIbaKIBAAAA",
    "H4sIAIyVoU8C_2MEABvfBaUBAAAA",
    "H4sIAJ2VoU8C_2tg4AQANnqoZwMAAAA=",
    "H4sIAGSYoU8C_2tgwAIUGJgUAEjSj-0ZAAAA",
    "H4sIAPKYoU8C_2tggAAmBjTQwEAcAAChQEZMQQAAAA==",
    32
  ]

  def test_encode(self):
    # Bat shit crazy gzip doesn't produce consistent results
    pass


if __name__ == "__main__":
  unittest.main()