import glob
import xmltodict
import sys
import os
import logging
import hashlib
from gzip import GzipFile
from pprint import pprint

try:
    PUBMED_PATH = sys.argv[1]
except IndexError:
    PUBMED_PATH = "/Volumes/HDD/Installers/PubMed/ftp.nlm.nih.gov/projects/medleasebaseline/gz/"


def compute_md5_file(file_object, block_size=65535):
    m_sum = hashlib.md5()
    while True:
        block = file_object.read(block_size)
        if block == '':
            break
        m_sum.update(block)
    return m_sum.hexdigest()


def medline_files(path, default_extension=".gz", check_integrity=True):
    filelist = glob.glob(os.path.join(path, "*" + default_extension))
    for each_file in filelist:
        if check_integrity:
            expected_sum_file = each_file + ".md5"
            # The actual md5 sum is the righmost element contained in the file
            expected_sum = open(expected_sum_file, 'rU').read().strip().split()[-1]
            with open(each_file, "rb") as reader:
                file_sum = compute_md5_file(reader)
            if file_sum != expected_sum:
                raise ValueError("The md5 sum for %r is incorrect. It should be %r but it is %s.", each_file,
                                 expected_sum, file_sum)

        yield each_file

    return


def parse_articles(medline_filename, callback):
    logging.info("Parsing %r", medline_filename)
    xmltodict.parse(GzipFile(medline_filename), item_depth=2, item_callback=callback, dict_constructor=dict)


def test_parse_callback(_, MedlineCitation):
    if 'MeshHeadingList' in MedlineCitation:
        if 'Journal' in MedlineCitation:
            pprint(MedlineCitation['Journal'])
            pprint(MedlineCitation['MeshHeadingList'])
    return True


def parse_all_medline_serial(callback):
    for m in medline_files(PUBMED_PATH):
        parse_articles(m, callback)


if __name__ == "__main__":
    parse_all_medline_serial(test_parse_callback)




