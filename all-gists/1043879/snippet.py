#!/usr/bin/env python
# Initially written by Heather Piwowar, June 2011
# Public domain: have at it!
# For converting ISI Web of Science tab-delimited exports into bibtex format

import csv
import glob
import random
from collections import defaultdict
import codecs

lookup = dict(AF="author", TI="title", JI="journal", LA="language", DT="keywords", DI="doi",
            AB="abstract", DE="keywords", ID="keywords", C1="address", PU="publisher", 
            PI="address", PA="address", PD="month", PY="year", VL="volume", IS="issue", BP="pages", 
            AR="number",  SB="isbn", EM="email", FU="funding", UT="issn", SC="categories", 
            FX="acknowledgements")


def get_updated_heading(heading):
    try:
        lookup_value = lookup[heading]
    except:
        lookup_value = ""
    return(lookup_value)

def update_bib_dict(line, header_line, filename):
    bib_dict = defaultdict(str)
    bib_dict["filename"] = filename
    for (item, old_heading) in zip(line, header_line):
        new_heading = get_updated_heading(old_heading)
        if new_heading and item:
            if bib_dict[new_heading]:
                bib_dict[new_heading] = "; ".join([bib_dict[new_heading], item])
            else:
                bib_dict[new_heading] = item
    if bib_dict["author"]:
        bib_dict["author"] = bib_dict["author"].replace("; ", " and ")
    if bib_dict["doi"] and not bib_dict["url"]:
        bib_dict["url"] = "http://dx.doi.org/" + bib_dict["doi"]
    return(bib_dict)

def parse_wos_txt(filename):
    """Takes a filename and returns a dictionary"""
    print filename
    wos_txt_fh = csv.reader(open(filename, "r"), delimiter="\t")
    header = wos_txt_fh.next()
    bib_list = []
    for line in wos_txt_fh:
        bib_list.append(update_bib_dict(line, header, filename))
    return(bib_list)   

def export_as_bibtex(bib_list, fh, filename):
    counter = 0
    for bib_dict in bib_list:
        counter += 1
        bib_id = filename + "-" + str(counter)
        fh.write("@article{" + str(bib_id) + ",")
        lines = [heading + " = {" + str(bib_dict[heading]) + "}" for heading in bib_dict]
        fh.write(",\r\n".join(lines))
        fh.write("\r\n}\r\n")

def convert_dir_of_wos_txt_into_bibtex(mydir, output_filename):
    mydict = dict()
    counter = 0
    writing_fh = codecs.open(output_filename, "w", "utf-8")

    for filename in glob.glob(mydir + "/*.txt"):
        bib_list = parse_wos_txt(filename)
        export_as_bibtex(bib_list, writing_fh, filename)
    writing_fh.close()
    
#convert_dir_of_wos_txt_into_bibtex("Pangaea", "Pangaea_raw.bib")    
#convert_dir_of_wos_txt_into_bibtex("GEOROC", "GEOROC_raw.bib")    
#convert_dir_of_wos_txt_into_bibtex("GEO", "GEO_raw.bib")    
convert_dir_of_wos_txt_into_bibtex("TreeBase", "TreeBase_raw.bib")    
    
