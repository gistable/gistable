import string
class CesarCipher(object):
  shift = None
  alphabet = None
  
  def setAlphabet(self, alphabet):
    self.alphabet = alphabet

  def setShift(self, shift):
#    self.shift = shift % 26 # only 26 chars in alphabet
    self.shift = shift

  def encode(self, plainText):
    shifted = self.alphabet[self.shift:] + self.alphabet[:self.shift]
    table = string.maketrans(self.alphabet, shifted)
    return plainText.translate(table)



if __name__ == '__main__':
  caesar = CesarCipher()
  caesar.setAlphabet("ABCD")
  caesar.setShift(3)
  encoded = caesar.encode("AACBDEAA")
  print encoded
