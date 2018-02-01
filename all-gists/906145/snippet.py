#!/usr/bin/env python
# encoding: utf-8
"""
epub_to_opds_entry.py

Created by Keith Fahlgren on Tue Apr  5 21:21:02 PDT 2011
Copyright (c) 2011 Threepress. All rights reserved.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the Threepress nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Introspects an EPUB's metadata to create an OPDS Catalog entry
"""


import datetime
import logging
import sys
import uuid

from zipfile import ZipFile


from lxml import etree


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
logging.basicConfig() 

class InvalidEpubException(Exception): pass

CONTAINER = 'META-INF/container.xml'
NSS = {'atom': 'http://www.w3.org/2005/Atom',
       'container': 'urn:oasis:names:tc:opendocument:xmlns:container',
       'dc': 'http://purl.org/dc/elements/1.1/',
       'dcterms': 'http://purl.org/dc/terms/',
       'opf': 'http://www.idpf.org/2007/opf',
      }
STARTING_NOW = datetime.datetime.utcnow().replace(microsecond=0) # don't need ms precision in ISO-8601 datetimes
THIS_UUID = uuid.UUID('71D68359-1F0D-4A92-B068-95D5311C9B5D')



def entry_for_epub(epub_fn, pos_ix=0):
    opf = _opf_from_epub(epub_fn)
    metadata = _get_epub_metadata(opf)
    entry = _build_entry(epub_fn, metadata, pos_ix=pos_ix)
    return entry

# =================

def _build_entry(epub_fn, metadata, pos_ix=0):
    entry = etree.Element("{%s}entry" % NSS['atom'], nsmap={None: NSS['atom'], 'dc': NSS['dcterms']})
    _add_dc_metadata(entry, metadata)
    _add_required_metadata(entry, metadata, epub_fn, pos_ix=pos_ix)
    return entry

def _add_dc_metadata(entry, metadata):
    for el_name, el_values in metadata.iteritems():
        if el_values is not None:
            for val in el_values:
                if el_name == 'creator':
                    au = etree.SubElement(entry, "{%s}author" % (NSS['atom']))
                    etree.SubElement(au, "{%s}name" % (NSS['atom'])).text = val
                elif el_name == 'title':
                    etree.SubElement(entry, "{%s}%s" % (NSS['atom'], el_name)).text = val
                else:
                    etree.SubElement(entry, "{%s}%s" % (NSS['dcterms'], el_name)).text = val
    return entry

def _add_required_metadata(entry, metadata, epub_fn, pos_ix=0):
    entry_key = '%s;%s' % (''.join(metadata['title']), ''.join(metadata['identifier']))
    cleaned_entry_key = "".join(i for i in entry_key if ord(i) < 128) # no UTF8
    entry_id = 'urn:uuid:%s' % uuid.uuid5(THIS_UUID, str(cleaned_entry_key))
    etree.SubElement(entry, "{%s}id" % (NSS['atom'])).text = entry_id

    updated = (STARTING_NOW - datetime.timedelta(seconds=pos_ix)).isoformat() + 'Z'
    etree.SubElement(entry, "{%s}updated" % (NSS['atom'])).text = updated

    # Empty
    etree.SubElement(entry, "{%s}summary" % (NSS['atom']))

    acq_link = etree.SubElement(entry, "{%s}link" % (NSS['atom']))
    acq_link.set('rel', "http://opds-spec.org/acquisition")
    acq_link.set('href', epub_fn)
    acq_link.set('type', "application/epub+zip")


def _get_dc_metadata(opf, el_name):
    metadata_els = opf.xpath('/opf:package/opf:metadata/dc:%s' % el_name, namespaces=NSS) 
    if len(metadata_els) == 0:
        return None
    else:
        return [el.text.strip() for el in metadata_els if el.text is not None]

def _get_epub_metadata(opf):
    metadata = {}
    metadata['identifier'] = _get_publication_identifier(opf) 
    metadata['creator'] = _get_dc_metadata(opf, 'creator')
    metadata['rights'] = _get_dc_metadata(opf, 'rights')
    metadata['publisher'] = _get_dc_metadata(opf, 'publisher')
    metadata['title'] = _get_dc_metadata(opf, 'title')
    return metadata


def _get_publication_identifier(opf):
    unique_identifier_id = opf.xpath('/opf:package', namespaces=NSS)[0].get('unique-identifier')
    unique_identifiers = opf.xpath('/opf:package/opf:metadata/dc:identifier[@id="%s"]' % unique_identifier_id, namespaces=NSS)
    if len(unique_identifiers) > 1:
        raise InvalidEpubException("More than one unique-identifier in the EPUB package metadata")
    elif len(unique_identifiers) == 0:
        log.warn("No unique-id matching %s" % unique_identifier_id)
        raise InvalidEpubException("No unique-identifier found in the EPUB package metadata")
    else:
        return [ui.text.strip() for ui in unique_identifiers] # will only be one

def _opf_from_epub(epub_fn):
    try:
        z = ZipFile(open(epub_fn)) 
        container = etree.fromstring(z.read(CONTAINER))
        opf_filename = container.xpath('/container:container/container:rootfiles/container:rootfile', namespaces=NSS)[0].get('full-path')
        opf = etree.fromstring(z.read(opf_filename))
        return opf
    except KeyError as ke:
        raise InvalidEpubException(ke)
    except Exception:
        raise InvalidEpubException("EPUB not correctly formatted as a ZIP")


# =================


def main(argv):
    for pos_ix, epub_fn in enumerate(argv):
        try:
            entry = entry_for_epub(epub_fn, pos_ix=pos_ix)
            print etree.tostring(entry, pretty_print=True)
        except InvalidEpubException as ie:
            log.error("ERROR: Skipping %s due to invalidity! (%s)" % (epub_fn, ie))
        except Exception as e:
            log.error("ERROR: Skipping %s due to unknown error! (%s)" % (epub_fn, e))
            raise

if __name__ == "__main__":
    main(sys.argv[1:])
