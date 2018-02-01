#!/usr/bin/env python -O

import argparse
import sys
import numpy
import h5py
import csv

class ColType:
    UNKNOWN = 1
    STRING = 2
    FLOAT = 3
    INT = 4

# trys to infer a type from a string value
def infer_col_type(str_val):
    str_val = str_val.strip()
    try:
        int(str_val)
        return ColType.INT
    except ValueError:
        try:
            float(str_val)
            return ColType.FLOAT
        except ValueError:
            return ColType.STRING

# takes a sequence of infered column types and returns the most specific type
# that can be used to hold any values in the sequence
def most_specific_common_type(col_types):
    if ColType.STRING in col_types:
        return ColType.STRING
    elif ColType.FLOAT in col_types:
        return ColType.FLOAT
    elif ColType.INT in col_types:
        return ColType.INT
    else:
        return ColType.UNKNOWN

# take a string value along with it's column type and convert it to the python
# native representation
def str_to_native(str_val, col_type):
    if col_type == ColType.STRING:
        return str_val
    elif col_type == ColType.FLOAT:
        return float(str_val)
    elif col_type == ColType.INT:
        return int(str_val)
    else:
        raise ValueError

# give the corresponding numpy type for the given column type info
def to_numpy_type_tuple(col_name, col_type, max_str_len, avg_str_len, len_diff_threshold):
    if col_type == ColType.STRING:
        if max_str_len - avg_str_len > len_diff_threshold:
            return (col_name, h5py.special_dtype(vlen=str))
        else:
            return (col_name, numpy.str_, max_str_len)
    elif col_type == ColType.FLOAT:
        return (col_name, 'f')
    elif col_type == ColType.INT:
        return (col_name, 'i')
    else:
        raise ValueError

# converts a CSV file into an HDF5 dataset
def csv_to_hdf5(csv_file_name, hdf_group, table_name, len_diff_threshold = sys.maxint):
    # the first pass through the CSV file is to infer column types
    csv_file = open(csv_file_name, 'rb')
    snp_anno_reader = csv.reader(csv_file)
    header = snp_anno_reader.next()
    col_count = len(header)
    max_str_lens = [0 for x in range(0, col_count)]
    avg_str_lens = [0 for x in range(0, col_count)]
    col_types = [ColType.UNKNOWN for x in range(0, col_count)]
    row_count = 0
    
    for row in snp_anno_reader:
        assert len(row) == col_count
        curr_str_lens = map(len, row)
        max_str_lens = map(max, zip(max_str_lens, curr_str_lens))
        avg_str_lens = map(sum, zip(avg_str_lens, curr_str_lens))
        col_types = map(most_specific_common_type, zip(map(infer_col_type, row), col_types))
        row_count += 1
    
    csv_file.close()
    avg_str_lens = [float(x) / row_count for x in avg_str_lens]

    table_type = numpy.dtype(
        [to_numpy_type_tuple(header[i], col_types[i], max_str_lens[i], avg_str_lens[i], len_diff_threshold)
            for i in range(0, col_count)])

    # the second pass through is to fill in the HDF5 structure
    hdf5_table = hdf_group.create_dataset(table_name, (row_count,), dtype = table_type)
    csv_file = open(csv_file_name, 'rb')
    snp_anno_reader = csv.reader(csv_file)
    header = snp_anno_reader.next()
    
    for row_index in range(0, row_count):
        row = snp_anno_reader.next()
        row_val = [str_to_native(row[i], col_types[i]) for i in range(0, col_count)]
        hdf5_table[row_index] = tuple(row_val)
    
    csv_file.close()

# main entry point for script
def main():
    parser = argparse.ArgumentParser(description = 'Convert a CSV file to HDF5')
    parser.add_argument(
        '--dataset-name',
        dest    = 'dataset_name',
        help    = 'the dataset name to use when adding the table to HDF5')
    parser.add_argument(
        '--len-diff-threshold',
        dest    = 'len_diff_threshold',
        type    = int,
        default = sys.maxint,
        help    = 'string data columns can either be fixed length or variable '
                  'length. This parameter specifies a threshold value for the '
                  'difference between a columns maximum string length and '
                  'average string length. When the threshold is exceeded the '
                  'column is set to variable length. The default behavior is '
                  'for all string columns to be fixed length.')
    parser.add_argument(
        'CSV_input_file',
        help = 'the CSV input file')
    parser.add_argument(
        'HDF5_output_file',
        help = 'the HDF5 output file')
    args = parser.parse_args()
    hdf5_file = h5py.File(args.HDF5_output_file, 'w')
    table_name = args.CSV_input_file if args.dataset_name is None else args.dataset_name
    csv_to_hdf5(args.CSV_input_file, hdf5_file, table_name, args.len_diff_threshold)

if __name__ == "__main__":
    main()
