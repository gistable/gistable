#!/usr/bin/python3

# This Script parses a couple of genotyping-files downloaded from openSNP.
# It supports deCODEme, FamilyTreeDNA and 23andme-files.
# If you don't like the Object Oriented Magic just comment out the lines with allSnps.append 
# and do your own magic.

# Example-Useage is name of the script followed by as many filenames as you like.
# ./megaparser.py 200.23andme.12 92.decodeme.1 [...]
# or:
# python3 megaparser.py 200.23andme.12 92.decodeme.1 [...]
#
# License is Public Domain. Made by Philipp Bayer in 2012

import argparse # to parse the arguments, argparse is the "new" optparse

# global array containing all SNPs
allSnps = []

class Snp:
    # Each SNP is one line in the original file
    def __init__(self, name, variation, chromosome, position, strand, uservariation):
        self.name = name # e.g. RS1234

	# only deCODEme lists possible variations and strand
        if variation is None:
            self.variation = "Unknown"
        else:
            self.variation = variation # e.g. A/T

        self.chromosome = chromosome # 1,2,3...
        self.position = position # e.g. 213412

        if strand is None:
            self.strand = "Unknown"
        else:
            self.strand = strand # +,-

        self.uservariation = uservariation # e.g. TT

    def printargs(self):
        print("Name: " + self.name)
        print("Possible variations: " + self.variation)
        print("Chromosome: " + self.chromosome)
        print("Position: " + self.position)
        print("Strand: " + self.strand)
        print("Uservariation: " + self.uservariation)
        print()

def parseDecodeme(filein):
    for line in filein:

        # skip the first line
        if "Name,Variation,Chromosome,Position,Strand,YourCode" in line:
            continue

        # Make an array containing all the elements of the line
        lineArray = line.replace("\n","").replace(" ","").split(",")
        # Make an object based on that array and append it to the global array of all SNPs
        allSnps.append(Snp(lineArray[0], lineArray[1], lineArray[2], lineArray[3], lineArray[4], lineArray[5]))

def parse23andme(filein):
    for line in filein:

        # skip comments
        if "#" in line:
            continue
        lineArray = line.replace(" ", "").replace("\n","").split("\t")
        allSnps.append(Snp(lineArray[0], None, lineArray[1], lineArray[2], None, lineArray[3]))

def parseFTDna(filein):
    for line in filein:
        # skip first line
        if "RSID,CHROMOSOME,POSITION,RESULT" in line:
            continue
        lineArray = line.replace('"','').replace("\n","").split(",")
        allSnps.append(Snp(lineArray[0], None, lineArray[1], lineArray[2], None, lineArray[3]))

def parseAllFiles(args):
    # go through all files, and call the relevant subroutines
    for element in args.filenames:

        # use openSNP's style of file-naming to see what's in the file
        if "23andme" not in element and "decodeme" not in element and "ftdna" not in element:
            print("File called " + element + "doesn't seem to be a proper file.")
            continue

        filein = open(element)

        if "23andme" in element:
            parse23andme(filein)
        elif "decodeme" in element:
            parseDecodeme(filein)
        elif "ftdna" in element:
            parseFTDna(filein)

        filein.close()

def printAllSnps():
    # Dummy function that just prints all SNPs to the command-line
    for element in allSnps:
        element.printargs()


# Define the parser for command-line arguments and add arguments
parser = argparse.ArgumentParser(description="Parses raw genotyping files from 23andme, deCODEme and FamilyTreeDNA based on the filenames openSNP provides.")
# There is an unlimited number of files, so nargs is +
parser.add_argument("filenames", metavar="filename", type=str, nargs="+", help="Name of the file(s) you want to parse.")
args = parser.parse_args()

# Start the main-program
parseAllFiles(args)

# Just print out all SNPs. Do your own thing here :)
printAllSnps()