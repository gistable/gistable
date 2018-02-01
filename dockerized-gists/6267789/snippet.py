import csv

# Extract float data from a csv to a python dict
def csv2dict( filename, delimiter = ',', has_header = True, text_columns = None ):

    # Open the csv file, extract the first line and initialize the data dict
    csvreader = csv.reader( open(filename, 'rb'), delimiter=delimiter )
    first_line = csvreader.next()
    data = {}

    # If there's a header line, use the items in the first line to generate the dict keys
    # If there isn't, use numeric keys and put the first item already in the data arrays
    if has_header:
        for item in first_line:
            data[item] = []
    else:
        counter = 0
        for value in first_line:
            if text_columns and counter in text_columns:
                data[counter] = [value]
            else:
                data[counter] = [to_float(value)]
            counter += 1

    # Extract the rest of the data
    for line in csvreader:

        if has_header:
            for key, value in zip( first_line, line ):
                if text_columns and key in text_columns:
                    data[key].append(value)
                else:
                    data[key].append(to_float(value))

        else:
            for key, value in zip( range(len(line)), line ):
                if text_columns and key in text_columns:
                    data[key].append(value)
                else:
                    data[key].append(to_float(value))

    # Return the extracted data
    return data


def dict2csv( data, filename, delimiter = ',', has_header = True, key_order = None ):

    # Open the csv file
    csvwriter = csv.writer( open(filename, 'wb'), delimiter=delimiter )

    # Extract the data keys
    keys = data.keys()

    # If a key order is provided, check all the keys exist
    if key_order:
        for key in key_order:
            if key not in keys:
                return False

        keys = key_order

    # Write the header line
    if has_header:
        csvwriter.writerow( keys )

    # Write the data
    for i in range(len(data[keys[0]])):
        row = []
        for key in keys:
            row.append( data[key][i] )
        csvwriter.writerow( row )

    return True


# Extract a float from a string and return a NaN if not possible
def to_float( str_value ):

    number = None

    try:
        number = float( str_value )
    except ValueError:
        number = float('nan')

    return number