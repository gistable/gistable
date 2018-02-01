"""
Export your keynote file to HTML.  Pass the keynote file (to extract the
presentation notes) and the extracted HTML directory to this script, and it
will attempt to inject the presenter notes it extracted from the Keynote file
into the HTML.

Only tested on Keynote '09, Chrome 24.0.1312.56
"""

import os
import random
import string
import subprocess
import sys

from lxml import etree, html


def extract_notes(keynote_file):
    # keynote file is a giant compressed xml file - uncompress it
    tempdir = '/tmp/keynote_thing.{0}.xml'.format(
        "".join(random.sample(string.ascii_letters, 10)))
    os.mkdir(tempdir)
    subprocess.check_call(['unzip', keynote_file, '-d', tempdir])
    xml = etree.parse(tempdir + '/index.apxl')
    root = xml.getroot()

    # get all the presenter note xml elements
    notes = root.xpath('.//key:notes//sf:text-body', namespaces=root.nsmap)

    # replace all the funky keynote tags with html tags - I am stupid and don't
    # know xslt, so do this the slow way
    sf_namespace = '{{{0}}}'.format(root.nsmap['sf'])

    def replace_node(node):
        if node.tag.startswith(sf_namespace):
            node.tag = node.tag.replace(sf_namespace, '')
            if node.tag == 'link':
                node.tag = 'a'
            else:
                if node.tag == 'text-body':
                    node.tag = 'div'
                node.attrib.clear()
            node.nsmap.clear()

        for child in node.getchildren():
            replace_node(child)

    for idx, note in enumerate(notes):
        replace_node(note)
        note.attrib['id'] = 'slidePresenterNotes{0}'.format(idx)
        note.attrib['class'] = 'presenterNotes'

    return notes


def inject_js(html_file, presenter_notes):
    doc = html.parse(html_file)
    head = doc.xpath("//head")[0]
    body = doc.xpath("//body")[0]

    style = etree.Element("style")
    style.text = """
        #presenterNotes {
            margin: auto 0; width: 15%; background-color: #CCCCCC;
            padding: 0 5px; color: black; border: 1px solid black;"
        }
        #presenterNotesSlideNumber {
            font-weight: bold;
        }
    """

    notes = etree.Element("div", **{"id": "presenterNotes"})
    notes.append(etree.Element("div", **{"id": "presenterNotesSlideNumber"}))
    notes.extend(presenter_notes)

    handler = etree.Element("script")
    handler.text = """
    function injectPresenterNotes () {

        injection_self = this;
        injection_self.presenterNotes = document.getElementById(
            "presenterNotes");

        injection_self.lastSlideNumber = -1;
        function updatePresenterNotes () {
            if (currentEventTimeline != injection_self.lastSlideNumber) {
                // hide other slide notes
                injection_self.presenterNotes.select(
                    '[class="presenterNotes"]').invoke('hide');
                // display the notes for the slide that is visible
                $('slidePresenterNotes' + currentEventTimeline).show();
                // update the slide number label
                $('presenterNotesSlideNumber').update(
                    "Presenter notes for Slide " + (currentEventTimeline + 1));
                injection_self.lastSlideNumber = currentEventTimeline;
            }
        };

        updatePresenterNotes();
        // update every 100 ms because it could take this number a little while
        // to change
        setInterval(updatePresenterNotes, 100);
    }
    """

    head.append(style)
    head.append(handler)
    body.insert(0, notes)
    body.attrib['onload'] = "; ".join(
        [x for x in (body.attrib.get('onload', '').rstrip(';'),
                     "injectPresenterNotes();") if x])

    doc.write(html_file, method="html")


def modify_all_html(html_dir, presenter_notes):
    find_output = subprocess.check_output(
        ['find', html_dir, '-name', '*.html'])
    all_html = [name for name in find_output.split('\n') if name]
    for html_file in all_html:
        inject_js(html_file, presenter_notes)


presenter_notes = extract_notes(sys.argv[1])
modify_all_html(sys.argv[2], presenter_notes)
