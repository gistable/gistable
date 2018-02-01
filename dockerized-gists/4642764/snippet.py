#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, getopt, os, re, time, locale, csv
from cStringIO import StringIO

try:
    from pdfminer.pdfinterp import PDFResourceManager, process_pdf
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
except ImportError:
    print "\nError:  Could not import PDFMiner. Please '$pip install pdfminer'.\n"\
          "\tModule description: http://www.unixuser.org/~euske/python/pdfminer/index.html"


def ensure_folder(path, folder_name):
    # Check for folder. If it doesn't exist create it.
    folder_path = (os.path.join(path, folder_name))
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)
        print "Created result folder '%s'.\n" % folder_name
    return folder_path


def download_raw_gist(gist_id, file_to_save='gist.txt'):
    # Import the additional modules needed.
    from urllib2 import Request, urlopen, HTTPError

    # Create the url and the request.
    gist_raw_url = 'http://raw.github.com/gist/%s' % gist_id
    request = Request(gist_raw_url)

    # Open url and write it to the file.
    try:
        print "Trying to download %s" % gist_raw_url
        keyword_file = urlopen(request)
        with open(file_to_save, 'w') as local_keyword_file:
            local_keyword_file.write(keyword_file.read())
            print "Successfully downloaded gist #%s.\n" % gist_id

    except HTTPError, e:
        print "Error: HTTP", e.code, gist_raw_url


def create_dict_from_csv(csv_file, gist_id):
    # If csv doesn't exist download it from github.
    if not os.path.exists(csv_file):
        print "Didn't find %s." % csv_file
        download_raw_gist(gist_id, csv_file)

    # Open file and parse the file line per line.
    keywords = {}
    try:
        with open(csv_file, 'rb') as file:
            keyword_lists = csv.reader(file, delimiter=';')
            for row in keyword_lists:
                if len(row) == 1:
                    keywords[row[0].strip(' \t')] = row[0].strip(' \t')
                else:
                    keywords[row[0].strip(' \t')] = row[1].strip(' \t')
    except:
        print "Couldn't create dictionary from csv."

    return keywords


def convert_pdf_to_text(path, maxpages=1):
    """
    Conversion of a pdf content to text.
    Source: http://stackoverflow.com/questions/5725278/python-help-using-pdfminer-as-a-library
    """

    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)

    with open(path, 'rb') as fp:
        process_pdf(rsrcmgr, device, fp, maxpages=maxpages)
        device.close()

    str = retstr.getvalue()
    retstr.close()
    return str


def find_date_in_string(text, debug=False):

    # The dictionary with all necessary data for the different date formats
    # For each date format we need:
    #   - regular expression
    #   - corresponding python date formats
    #   - locales which should be supported
    #   - a placeholder for the regex match object
    date_formats = {
        'alphanumeric' : {
            'regex' : r'([1-9]|[0-2][\d]|3[01])(\.\ |\.|\-|\/|\ )(Jan|JAN|Feb|FEB|Mar|MAR|Apr|APR|May|MAY|Jun|JUN|Jul|JUL|Aug|AUG|Sep|SEP|Oct|OCT|Nov|NOV|Dec|DEC|Mär|MÄR|Mai|MAI|Okt|OKT|Dez|DEZ|January|February|March|April|June|July|August|September|October|November|December|Januar|Februar|März|Juni|Juli|Oktober|Dezember)[\.\ \-\/]((199[\d]|20[0-2][\d]|2030)|9[\d]|(9[\d]|[12][\d]|30))',
            'python_date_formats' : [
                '%d. %B %Y', '%d. %B %y',
                '%d %B %Y', '%d %B %y',
                '%d. %b %Y', '%d. %b %y',
                '%d %b %Y', '%d %b %y',
                '%d-%b-%Y', '%d-%b-%y',
                '%d/%b/%Y', '%d/%b/%y',
                '%d.%B.%Y', '%d.%B.%y',
                '%d.%b.%Y', '%d.%b.%y',
                '%d-%B-%Y', '%d-%B-%y',
                '%d/%B/%Y', '%d/%B/%y',
                ],
            'locales' : [
                'de_DE',
                'en_US',
                ],
            'regex_match' : False,
            },
        'reverse numeric' : {
            'regex' : r'(199[\d]|20[0-2][\d]|2030)[\.\-\/\ ]([1-9]|[0-2][\d]|3[01])[\.\-\/\ ]([1-9]|[0-2][\d]|3[01])',
            'python_date_formats' : [
                '%Y-%m-%d',
                '%Y/%m/%d',
                '%Y.%m.%d',
                ],
            'regex_match' : False,
            'locales' : [ 'de_DE', ],
            },
        'numeric' : {
            'regex' : r'([1-9]|[0-2][\d]|3[01])[\.\-\/\ ]([1-9]|[012][\d]|3[01])[\.\-\/\ ]((199[\d]|20[0-2][\d]|2030)|9[\d]|(9[\d]|[0-2][\d]|30))',
            'python_date_formats' : [
                # 'Normal' dates
                '%d.%m.%Y', '%d.%m.%y',
                '%d-%m-%Y', '%d-%m-%y',
                '%d/%m/%Y', '%d/%m/%y',
                # US dates
                '%m.%d.%Y', '%m.%d.%y',
                '%m-%d-%Y', '%m-%d-%y',
                '%m/%d/%Y', '%m/%d/%y',
                ],
            'locales' : [ 'de_DE', ],
            'regex_match' : False,
            },
        'domaindiscount' : {
            'regex' : r'\d{2}/\d{2}th/\d{4}',
            'python_date_formats' : [
                '%m/%dth/%Y',
                ],
            'locales' : [ 'de_DE', ],
            'regex_match' : False,
            },
        }

    # Iterate over date formats.
    parsed_date = ''
    for date_format_name, date_format_data in date_formats.iteritems():
        found_date = False
        # Iterate over locales to have i18n date matching.
        #   (String formatting directives '%b' & '%B' are locale dependant.)
        for locale_value in date_format_data['locales']:
            locale.setlocale(locale.LC_ALL, locale_value)

            date_format_data['regex_match'] = re.search(date_format_data['regex'], text)
            if date_format_data['regex_match']:
                if debug: print "\tRegex match: %s" % date_format_data['regex_match'].group(0)

                for date_format in date_format_data['python_date_formats']:
                    try:
                        parsed_date = time.strptime(date_format_data['regex_match'].group(0), date_format)
                        if debug: print "\tFound %s date with the format of '%s'." % (date_format_name, date_format)
                        return parsed_date
                    except:
                        pass

    else:
        if debug: print "\tNotice: Could not retrieve a date."
        return


def find_first_keyword_in_string(text, keywords, debug=False):
    keyword_string = ''
    try:
        # Convert pdf_content to list.
        text_as_list = text.split()

        # Check for keywords:
        for word in text_as_list:
            for keyword, replacement in keywords.iteritems():
                if keyword in word:
                    keyword_string += "%s_" % replacement
                    if debug: print "\tFound the keyword '%s'." % keyword
                    return keyword_string
        else:
            if debug: print "\tDidn't find a keyword."
    except:
        if debug: print "\tError: Could not process for keywords."
        pass
    return keyword_string


def prefix_filename(filename, prefix):
    new_filename = prefix + filename
    os.rename(filename, new_filename)
    return new_filename


def main(argv):
    script_name = argv[0].split(os.sep)[-1]
    def usage():
        print ('Usage: %s [-v --verbose] [-d --debug] [-g --gist <gist-id>][-p --path <path-name>] '
               '[-f --date-format <python-date-format-string>] [-r --result-folder <result-folder>] '
               '[-a --all-pages] [-h --help]' % script_name)

    try:
        opts, arguments = getopt.getopt(argv[1:], "hvdg:f:r:p:ak:", ['help', 'verbose', 'debug', 'gist-id=', 'date-format=', 'result-folder=', 'path=', 'all-pages', 'keywords-file='])
    except getopt.GetoptError as err:
        # Print help information and exit.
        print "Error: %s.\nTry '%s --help' for more information." % (str(err), script_name)
        sys.exit()

    verbose = False
    debug = False
    pages_of_pdf_to_parse = 1
    prefix_date_format = '%Y-%m-%d'
    result_folder_name = 'processed'
    working_directory = os.getcwd()
    keywords_file = 'pdf-keywords.txt'
    gist_id = 4660290

    for opt, arg in opts:
        if opt in ('-v', '--verbose'):
            verbose = True
        elif opt in ('-d', '--debug'):
            debug = True
        elif opt in ('-g', '--gist-id'):
            gist_id = arg
        elif opt in ('-f', '--date-format'):
            prefix_date_format = arg
        elif opt in ('-r', '--result-folder'):
            result_folder_name = arg
        elif opt in ('-p', '--path'):
            os.chdir(arg)
            working_directory = os.getcwd()
        elif opt in ('-a', '--all-pages'):
            pages_of_pdf_to_parse = 0
        elif opt in ('-h', '--help'):
            usage()
            return
        elif opt in ('-k', '--keywords-file'):
            keywords_file = arg
        else:
            assert False, "unhandled option"

    # Get list of files and check if there are any files to work on.
    pdfs_to_process = [file for file in os.listdir(working_directory) if file.endswith('.pdf') or file.endswith('.PDF')]
    if len(pdfs_to_process) > 0:
        print '\nFound %s pdf-files to process.\n' % str(len(pdfs_to_process))
        if prefix_date_format != '%Y-%m-%d':
            print "Will use custom date format '%s'" % prefix_date_format
    else:
        print "\nDidn't find any pdf-files in the given folder.\n"
        return

    # Check if result folder exists.
    result_folder = ensure_folder(working_directory, result_folder_name)

    # Define keywords:
    keywords = create_dict_from_csv(keywords_file, gist_id)

    # Iterate over these files, try to parse the dates and build
    # a dictionary with all data we need to rename them.
    pdfs_to_rename = {}
    for pdf in pdfs_to_process:
        if verbose or debug: print "Processing '%s'" % pdf

        # Reset loop variables.
        pdf_content, pdf_date, pdf_keyword = '', '', ''
        try:
            pdf_content = convert_pdf_to_text(pdf, pages_of_pdf_to_parse)
            if pdf_content:
                pdf_date = time.strftime(prefix_date_format, find_date_in_string(pdf_content, debug)) # TODO: A Fail of find_date_in_sting() should be escaped separated.
                pdf_keyword = find_first_keyword_in_string(pdf_content, keywords, debug)
                pdfs_to_rename[pdf] = "%s_%s" % (pdf_date, pdf_keyword)
        except:
            print "Notice: Could not parse '%s'" % pdf

    # Rename & move the pdfs.
    for pdf, prefix in pdfs_to_rename.iteritems():
        new_pdf = prefix_filename(pdf, prefix)
        os.rename(new_pdf, os.path.join(result_folder, new_pdf))

    # Report how many PDFs could be matched to a date.
    print "\nI could extract a date from %s of %s PDFs.\n" % (str(len(pdfs_to_rename)), str(len(pdfs_to_process)))


if __name__ == '__main__': sys.exit(main(sys.argv))
