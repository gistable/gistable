def ocr_file(filename, languages, output_base, temp_dir):
    log.info("Launching tesseract on %s", filename)
    output = subprocess.check_output(['tesseract', filename, output_base,
                                      '-l', '+'.join(languages), TESSERACT_CONFIG],
                                     cwd=temp_dir,
                                     stderr=subprocess.STDOUT)

    with OCR_STORAGE.open('%s/%s/%s.log' % (item_id, group, index), 'w') as log_f:
        log_f.write(output)

    log.info("Processing hOCR output")
    hocr_file = os.path.join(temp_dir, '%s.html' % output_base)

    with open(hocr_file, 'rb') as f:
        hocr_bytes = f.read()

    OCR_STORAGE.save('%s/%s/%s.html.bz2' % (item_id, group, index),
                     ContentFile(bz2.compress(hocr_bytes)))

    log.info("Extracting plain text")
    # Kludge around https://bugs.launchpad.net/ubuntu/+source/tesseract/+bug/1094145
    html = lxml.html.document_fromstring(hocr_bytes.decode("utf-8", "replace").encode("utf-8"),
                                         parser=UTF8_PARSER)

    # Extract the text for Solr:
    text = []
    for p in html.cssselect('p'):
        text.append(u" ".join(i.text for i in p.iterdescendants() if i.text).strip())

    text = u"\n\n".join(filter(None, text))

    OCR_STORAGE.save('%s/%s/%s.txt.bz2' % (item_id, group, index),
                     ContentFile(bz2.compress(text.encode("utf-8"))))

    log.info("Extracting word coordinates")

    pages = html.cssselect('.ocr_page')
    assert len(pages) == 1
    page_elem = pages[0]
    page_info = [i.strip() for i in page_elem.attrib['title'].split(";")]

    for i in page_info:
        if i.startswith('bbox'):
            page_bbox = map(int, i.split()[1:5])
            break
    else:
        LOGGER.warning('Page did not contain bounding box information - no word coordinates!')
        return

    assert page_bbox[0] == 0
    assert page_bbox[1] == 0
    page_width = page_bbox[2]
    page_height = page_bbox[3]

    word_coords = defaultdict(list)

    for i in html.cssselect('.ocrx_word,.ocr_word'):
        term = inner_text(i)
        bbox = i.attrib['title'].split()
        assert bbox[0] == 'bbox'
        word_coords[term].append(map(int, bbox[1:5]))

    coordinates = {"height": page_height, "width": page_width,
                   "words": word_coords}

    coord_file = "%s/%s/%s.word_coordinates.json.bz2" % (item_id, group, index)
    coord_data = bz2.compress(simplejson.dumps(coordinates))
    OCR_STORAGE.save(coord_file, ContentFile(coord_data))
