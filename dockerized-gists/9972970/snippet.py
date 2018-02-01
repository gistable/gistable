import csv, re, requests

pattern = re.compile('<li>REPRESENTATIVE: (\d\d)</li>\n\t\t\t<li>SENATORIAL: (\d\d)</li>')

infile = csv.reader(open('addresses.csv', 'r'))

with open('output.csv', 'wb') as outfile:
    for line in infile:
        unique_id = line[0]
        address = line[1]
        zipcode = line[2]
        r = requests.get("https://sos.ri.gov/vic/search.php?street={0}&aCityOrTown=&aZipCode={1}&generalVoterSearch=Search".format(address, zipcode))
        #print('Request for {0}, {1} returned status code: {2}'.format(address, zipcode, r.status_code))
        #print r.url
        try:
            m = pattern.search(r.text)
            found_address = '{0},{1},{2},{3},{4}'.format(unique_id, address, zipcode, m.group(1), m.group(2))
            outfile.write(found_address)
            outfile.write('\n')
            print(found_address)
        except AttributeError:
            print('{0},{1},{2},{3},{4}'.format(unique_id, address, zipcode, 'not found', ''))
outfile.close()

# Just for the record, here was the original curl request from the Chrome Developer Tools that worked
# curl 'https://sos.ri.gov/vic/search.php' --data 'street=22+Blurg+Ave&aZipCode=02906&aCityOrTown=&generalVoterSearch=Search'
#
# For the new revision in 2016, it looks like this works as a GET request (not POST anymore):
#
# https://sos.ri.gov/vic/search.php?street=228+potters+avenue&aCityOrTown=&aZipCode=02905&generalVoterSearch=Search