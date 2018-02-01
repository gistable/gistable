#!/usr/bin/env python
# Initially written by Heather Piwowar, June 2011
# Public domain: have at it!
# For exporting bibtex info into csv for running stats

import csv
import re
from pybtex.database.input import bibtex as bibtex_in
from pybtex.database.output import bibtex as bibtex_out
from operator import itemgetter, attrgetter
from collections import defaultdict
import pprint
import sys

def read_bib(bib_filename):
    parser = bibtex_in.Parser()
    bib_data = parser.parse_file(bib_filename)
    #print(bib_data.entries['1'].fields['email'])
    return(bib_data)

def get_all_fieldnames(list_of_entries):
    fieldnames_set = set()
    for entry in list_of_entries:
        fieldnames_set = fieldnames_set.union(set(entry.keys()))
    fieldnames = sorted(list(fieldnames_set))
    return(fieldnames)
    
def get_encoded_row(row):
    encoded_row = {}
    for k, v in row.items():
        encoded_row[k] = v.encode('utf8')
    return(encoded_row)

TAG_HEADER_DICT = {"TAG repository": ["TreeBase", "Array Express", "GEO", "GEOROC", "Pangaea", "BMRB", "PDB", "TreeBASE"], 
                    "TAG source":["GS", "WoS"],
                    "TAG citation group":["citation group 1-3", "citation group 3-10", "citation group 10-30", "citation group 30-100", "citation group 100-300", "citation group 300-1000", "citation group 1000-3000", "citation group 3000-10000",],
                    "TAG data cited":["data cited", "does not cite"], 
                    "TAG dataset reused":["dataset reused", "dataset not reused", "dataset reuse ambiguous", "dataset reused as example", "database reuse"],
                    "TAG attribution location":["attribution in text", "attribution in table", "attribution in footnote", "attribution in reference", "attribution in abstract"],
                    "TAG confidence":["high confidence", "medium confidence", "low confidence"],
                    "TAG other":["multiple datasets cited"],
                    "TAG problem":["import error", "no full-text access"]}
TAG_HEADER_DICT_VALUES = [item for sublist in TAG_HEADER_DICT.values() for item in sublist]

def get_first_matching_key(dd, match_value):
    hit = (key for key,value in dd.items() if match_value in value).next()
    return(hit)
    
def expand_tags_to_columns(row):
    mendeley_tags = row["mendeley-tags"].replace(",", ";")
    mendeley_tags = [tag.strip() for tag in mendeley_tags.split(";")]
    expanded_row = row.copy()
    for tag in mendeley_tags:
        if tag in TAG_HEADER_DICT_VALUES:
            tag_header = get_first_matching_key(TAG_HEADER_DICT, tag)
            expanded_row[tag_header] = tag
    return(expanded_row)

def find_dataset_id(row):
    repository = row["TAG repository"]
    source = row["TAG source"]
    notes = row["annote"]
    dataset_id = ""
    try:
        if source == "WoS":
            dataset_id_match = re.search(r"data\\_id:(?P<id>.+); data\\_collection\\_article", notes)
            dataset_id = dataset_id_match.group("id")
        else:
            if repository == "GEO":
                dataset_id_match = re.search(r"(?P<id>GSE\d+)", notes)
                dataset_id = dataset_id_match.group("id")
            elif repository == "TreeBASE":
                dataset_id_match = re.search(r"(?P<id>S\d{3,})\S*?$", notes)
                dataset_id = dataset_id_match.group("id")
            elif repository == "BMRB":
                dataset_id_match = re.search(r"(?P<id>\d{3,})\S*?$", notes)
                dataset_id = dataset_id_match.group("id")
            elif repository == "Pangaea":
                dataset_id_match = re.search(r"(?P<id>10.\d+/PANGAEA.\d+)", notes)
                dataset_id = dataset_id_match.group("id")
            elif repository == "Array Express":
                dataset_id_match = re.search(r"(?P<id>\S-\S+-\S+)", notes)
                dataset_id = dataset_id_match.group("id")
            elif repository == "PDB":
                dataset_id_match = re.search(r"PMID.*(?P<id>[0-9][A-Z][0-9A-Z]{2})", notes)
                dataset_id = dataset_id_match.group("id")
    except:
        pass
    return(dataset_id)
            
def write_csv(bib_data, csv_filename):
    entries = bib_data.entries
    entries_list = []
    
    for entry in entries:
        raw_row = entries[entry].fields
        expanded_row = expand_tags_to_columns(raw_row)
        expanded_row["dataset_id"] = find_dataset_id(expanded_row)
        encoded_row = get_encoded_row(expanded_row)
        entries_list.append(encoded_row)
        
    fieldnames = get_all_fieldnames(entries_list)
    writer_dictwriter = csv.DictWriter(open(csv_filename, "wb"), 
                                        fieldnames=fieldnames)

    # write the header
    writer_dictwriter.writerow(dict((column,column) for column in fieldnames))
    
    # write the body
    for entry in entries_list:
        writer_dictwriter.writerow(entry)
    return(csv_filename)

def run_export(bib_filename, csv_filename=None):
    if not csv_filename:
        csv_filename = bib_filename.replace(".bib", ".csv")
    bib_data = read_bib(bib_filename)
    write_csv(bib_data, csv_filename)

#DIR = "Pangaea"
#DIR = "GEOROC"
#DIR = "GEO"
repository = "GEO"
#run_export("Mendeley Backup/all.bib")

