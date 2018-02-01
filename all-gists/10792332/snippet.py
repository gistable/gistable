# So, this is a port of a fairly simple script from "normal Python" to "pure-lambda
# Python". This code contains no Python statements, and is a proof-of-concept to show
# what you can do without statements, and how powerful Python's lambdas are despite
# that they are crippled.
#
# A few notes on how to read this:
# 1. Almost everything happens in the arguments. Practially nothing happens 
#    inside function bodies, since the function bodies are usually just other 
#    functions. Go down to the bottom of the expression (using your editor's
#    paren matching) to see what the arguments are.
# 2. Python doesn't enforce any indentation requirements within parentheses, so
#    I've tried to lay out everything according to nesting depth.
# 3. This may be contorted, but it isn't supposed to be obfuscated! Leave a comment
#    if there's anything I can explain better.
#
# Enjoy - remember that I'm not responsible for any of the following:
#  - Sudden enlightenment
#  - Uncontrollable weeping
#  - Brain melting/explsion
#
# (Consider this licensed under the CC0, although I doubt you'll want to put this
# anywhere near your other code: it may bite)

(
    # 1. functools and xml.etree.ElementTree are required in order to define 
    #    the 'get_subnode' utillity function. This is a way to emulate Lisp's
    #    let* or ML's letrec.
    (lambda functools, ElementTree:
        # 2. Import a series of modules, useful constants, and the 'get_subnode' function.
        #    - SCANNER_XML_NS and SCAN_JOB_XML_NS are, as you probably guessed, 
        #      XML namespaces used by HP printers.
        #    - SCAN_PAYLOAD is a chunk of XML which directs the scanner to scan
        #      and return a JPEG image.
        #    - SCAN_HEADER modifies the HTTP headers to modify the Content-Type
        #      to XML.
        (lambda sys, time, urlrequest, get_subnode, SCANNER_XML_NS, SCAN_JOB_XML_NS, SCAN_PAYLOAD, SCAN_HEADER:
            # 3. Gets the current status on the scanner - if the scanner is 
            #    working (has a non-empty state), then exit the program.
            (lambda root:
                get_subnode(root, SCANNER_XML_NS + 'ScannerState').text != '\n        ' and
                #  4. Gets the list of jobs.
                (lambda root:
                    # 5. Find out which job is 
                    #    currently being processed. Get the query URL (so we can check
                    #    the printer and ask when the job is done) and the image URL
                    #    (to download the image itself).
                    (lambda job_image_url:
                        # 6. Poll the scanner, and wait until it is ready to
                        #    give us the image. The waiting is done via recursion,
                        #    which is implemented via what is basically the omega
                        #    combinator (similar to the Y, but the callee doesn't
                        #    take any arguments other than itself).
                        #
                        #    When the recursion exits, download the image itself,
                        #    and exit the program.
                        (lambda f:
                            [f(f), urlrequest.urlretrieve('/'.join(['http:/', sys.argv[1], job_image_url[1]]), filename=sys.argv[2])]
                        )(lambda g:
                            g([time.sleep(2), g][1]) 
                            if get_subnode(
                                ElementTree.parse(
                                    urlrequest.urlopen(
                                        '/'.join(['http:/', sys.argv[1], job_image_url[0]])
                                    )
                                ).getroot(),
                                SCANNER_XML_NS,
                                'ScanJob', 'PreScanPage', 'PageState'
                            ).text != 'ReadyToUpload'
                            else True
                        )
                    )(
                        [(job.find(SCAN_JOB_XML_NS + 'JobUrl').text.lstrip('/'),
                            get_subnode(job, SCANNER_XML_NS,
                                'ScanJob', 'PreScanPage', 'BinaryURL').text.lstrip('/'))
                            for job in root
                            if get_subnode(job, SCAN_JOB_XML_NS, 'JobState').text == 'Processing'
                        ][0]
                ))([
                        urlrequest.urlopen(
                            urlrequest.Request(
                                '/'.join(['http:/', sys.argv[1], 'Scan', 'Jobs']),
                                data=SCAN_PAYLOAD,
                                headers=SCAN_HEADER)).close(),
                        ElementTree.parse(
                            urlrequest.urlopen(
                                '/'.join(['http:/', sys.argv[1], 'Jobs', 'JobList'])
                            )
                        ).getroot()
                    ][1]
            ))(ElementTree.parse(
                urlrequest.urlopen(
                    '/'.join(['http:/', sys.argv[1], 'Scan', 'Status'])
                )
            ).getroot()
        ))(__import__('sys'), 
            __import__('time'),
            __import__('urllib.request').request, 

            # Digs down into an XML structure, and gets elements by name. Since
            # the XML returned by the scanner is namespaced, this function applies
            # an XML namespace to each of the element names.
            (lambda root, prefix, *elems: 
                functools.reduce(
                    ElementTree.Element.find,
                    map(lambda e: prefix + e, elems), 
                    root)), 

            '{http://www.hp.com/schemas/imaging/con/cnx/scan/2008/08/19}',
            '{http://www.hp.com/schemas/imaging/con/ledm/jobs/2009/04/30}',
            b'''<scan:ScanJob 
xmlns:scan="http://www.hp.com/schemas/imaging/con/cnx/scan/2008/08/19" 
xmlns:dd="http://www.hp.com/schemas/imaging/con/dictionaries/1.0/">
    <scan:XResolution>300</scan:XResolution>
    <scan:YResolution>300</scan:YResolution>
    <scan:XStart>0</scan:XStart>
    <scan:YStart>0</scan:YStart>
    <scan:Width>2550</scan:Width>
    <scan:Height>3300</scan:Height>
    <scan:Format>Jpeg</scan:Format>
    <scan:CompressionQFactor>25</scan:CompressionQFactor>
    <scan:ColorSpace>Color</scan:ColorSpace>
    <scan:BitDepth>8</scan:BitDepth>
    <scan:InputSource>Platen</scan:InputSource>
    <scan:GrayRendering>NTSC</scan:GrayRendering>
        <scan:ToneMap>
        <scan:Gamma>1000</scan:Gamma>
        <scan:Brightness>1000</scan:Brightness>
        <scan:Contrast>1000</scan:Contrast>
        <scan:Highlite>179</scan:Highlite>
        <scan:Shadow>25</scan:Shadow>
    </scan:ToneMap>
    <scan:ContentType>Photo</scan:ContentType>
</scan:ScanJob>''',
            {'Content-Type': 'text/xml'}
            ))(__import__('functools'), 
                __import__('xml.etree.ElementTree').etree.ElementTree)
)