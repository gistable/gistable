import base64,re

# Replace these filenames with your input and output filenames. 
# Or rewrite it to pass filenames on the command line.
infilename = 'replaceme.bib'
outfilename = 'replacemetoo.bib'

r = re.compile("Bdsk-File[^.]*(?P<ending>}}|},)")

with open(infilename,'r') as infile:
    with open(outfilename,'w') as outfile:
        lines = infile.readlines()

        for line in lines:
            line = line.strip()
            endings = r.search(line)
            if endings:
                clean = line.split('=',1)[1].strip().strip('{},')
                decoded = base64.b64decode(clean)
                # Modify this line.  Bibdesk seems to keep the file references as a base64 encoded string that
                # encodes a Cocoa Foundation framework object (NSUrl or something like that).
                # The path is relative, so for my setup, I had my bib files in ~/Dropbox/Documents/BibBase,
                # and the papers in BibBase/Papers.  The Bdsk-File urls were all in the form 'Papers/filename.pdf'
                # That's what this script matches.
                matches = re.search("Papers.*?(?:pdf|PDF)", decoded)
                if matches:
                    # Change this line as well to the correct path.
                    fn = 'file = {:/Users/steven/Dropbox/Documents/BibBase/' + matches.group(0) + ':pdf'+endings.group('ending') + '\n'
                    outfile.write(fn)
                    print fn
            else:
                outfile.write(line + '\n')
