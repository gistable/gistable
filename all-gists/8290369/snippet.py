import os, shutil
import xml.etree.ElementTree as ElementTree

#---------------------------------------------------------------------

namespace_prefix = ['dc',
                    'opf']

namespace_uri    = ['http://purl.org/dc/elements/1.1/',
                    'http://www.idpf.org/2007/opf']

namespaces = dict(zip(namespace_prefix, namespace_uri))

azw3_dir = "kindle_books"
epub_dir = "epub_books"

#---------------------------------------------------------------------

def get_metadata(opf_file):

    metadata_root = ElementTree.parse(opf_file).getroot()

    genre = metadata_root[0].find("dc:subject", namespaces=namespaces).text
    author = metadata_root[0].find("dc:creator", namespaces=namespaces).text
    title = metadata_root[0].find("dc:title",namespaces=namespaces).text

    series = None
    for x in metadata_root[0].findall("opf:meta", namespaces=namespaces):
        if x.get('name') == 'calibre:series':
            series = x.get('content')

    return (genre, author, title, series)

#---------------------------------------------------------------------

def copy_to_directories(books, target_dirs, metadata):

    genre, author, title, series = metadata

    short_target_dir = os.path.join(genre, author)

    if series is not None:
        short_target_dir = os.path.join(short_target_dir, series)

    for book, target_dir in zip(books, target_dirs):

        full_target_dir = os.path.join(target_dir, short_target_dir)

        if not os.path.exists(full_target_dir):
            os.makedirs(full_target_dir)

        shutil.copy(book, full_target_dir)

#---------------------------------------------------------------------

working_dir = os.getcwd()

azw3_dir = os.path.join(working_dir,azw3_dir)
epub_dir = os.path.join(working_dir,epub_dir)

results_dirs = (azw3_dir, epub_dir)

for path,_,filenames in os.walk(working_dir):

    azw3_books   = (x for x in filenames if '.azw3' in x)
    epub_books   = (x for x in filenames if '.epub' in x)
    metadata_opf = (x for x in filenames if '.opf' in x)

    for azw3, epub, opf in zip(azw3_books, epub_books, metadata_opf):

        opf_full_path = os.path.join(path, opf)
        azw3_full_path = os.path.join(path, azw3)
        epub_full_path = os.path.join(path, epub)

        books = (azw3_full_path, epub_full_path)

        metadata = get_metadata(opf_full_path)

        copy_to_directories(books, results_dirs, metadata)

