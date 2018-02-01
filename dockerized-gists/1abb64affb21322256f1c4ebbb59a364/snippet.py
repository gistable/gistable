# Decrypt password-protected PDF in Python.
# cleaned-up version of http://stackoverflow.com/a/26537710/329263
# 
# Requirements:
# pip install PyPDF2
#
# Usage: decrypt_pdf('encrypted.pdf', 'decrypted.pdf', 'secret_password')

from PyPDF2 import PdfFileReader, PdfFileWriter

def decrypt_pdf(input_path, output_path, password):
  with open(input_path, 'rb') as input_file, \
    open(output_path, 'wb') as output_file:
    reader = PdfFileReader(input_file)
    reader.decrypt(password)

    writer = PdfFileWriter()

    for i in range(reader.getNumPages()):
      writer.addPage(reader.getPage(i))

    writer.write(output_file)

if __name__ == '__main__':
  # example usage:
  decrypt_pdf('encrypted.pdf', 'decrypted.pdf', 'secret_password')
