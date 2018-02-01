import PyPDF2
import shutil
import sys
from pathlib import Path


def list_files(directory, pattern='*.pdf'):
    """ Get name of all pdf files on directory """
    return sorted(Path(directory).glob(pattern))

def extract_name(filename):
    with filename.open('rb') as f:
        reader = PyPDF2.PdfFileReader(f)
        page = reader.getPage(0)
        return page.extractText()


def rename(source, destination):
    print('Renaming %s to %s' % (source, destination))
    shutil.move(source, destination)

def main():
    """ It makes the magic happen: Leeeeeroy Jenkins"""

    if len(sys.argv) > 1:
        directory = sys.argv
    else:
        directory = '.'

    NAME = 'Certificado IBADPP - %s.pdf'

    for pdf_file in list_files(directory):
        new_filename = NAME % extract_name(pdf_file)
        rename(str(pdf_file), new_filename)


if __name__ == '__main__':
    main()
