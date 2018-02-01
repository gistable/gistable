#!/usr/bin/env python
# Copyright (c) 2014 Lenna X. Peterson, all rights reserved
# lenna@purdue.edu

import argparse
import csv
import glob
import logging
import math
import os

# Package Bio can be obtained from http://www.biopython.org
from Bio import PDB

logging.basicConfig(level=logging.DEBUG)


class GetTorsion(object):
    """
    Calculate side-chain torsion angles (also known as dihedral or chi angles).
    Depends: Biopython (http://www.biopython.org)
    """

    chi_atoms = dict(
        chi1=dict(
            ARG=['N', 'CA', 'CB', 'CG'],
            ASN=['N', 'CA', 'CB', 'CG'],
            ASP=['N', 'CA', 'CB', 'CG'],
            CYS=['N', 'CA', 'CB', 'SG'],
            GLN=['N', 'CA', 'CB', 'CG'],
            GLU=['N', 'CA', 'CB', 'CG'],
            HIS=['N', 'CA', 'CB', 'CG'],
            ILE=['N', 'CA', 'CB', 'CG1'],
            LEU=['N', 'CA', 'CB', 'CG'],
            LYS=['N', 'CA', 'CB', 'CG'],
            MET=['N', 'CA', 'CB', 'CG'],
            PHE=['N', 'CA', 'CB', 'CG'],
            PRO=['N', 'CA', 'CB', 'CG'],
            SER=['N', 'CA', 'CB', 'OG'],
            THR=['N', 'CA', 'CB', 'OG1'],
            TRP=['N', 'CA', 'CB', 'CG'],
            TYR=['N', 'CA', 'CB', 'CG'],
            VAL=['N', 'CA', 'CB', 'CG1'],
        ),
        altchi1=dict(
            VAL=['N', 'CA', 'CB', 'CG2'],
        ),
        chi2=dict(
            ARG=['CA', 'CB', 'CG', 'CD'],
            ASN=['CA', 'CB', 'CG', 'OD1'],
            ASP=['CA', 'CB', 'CG', 'OD1'],
            GLN=['CA', 'CB', 'CG', 'CD'],
            GLU=['CA', 'CB', 'CG', 'CD'],
            HIS=['CA', 'CB', 'CG', 'ND1'],
            ILE=['CA', 'CB', 'CG1', 'CD1'],
            LEU=['CA', 'CB', 'CG', 'CD1'],
            LYS=['CA', 'CB', 'CG', 'CD'],
            MET=['CA', 'CB', 'CG', 'SD'],
            PHE=['CA', 'CB', 'CG', 'CD1'],
            PRO=['CA', 'CB', 'CG', 'CD'],
            TRP=['CA', 'CB', 'CG', 'CD1'],
            TYR=['CA', 'CB', 'CG', 'CD1'],
        ),
        altchi2=dict(
            ASP=['CA', 'CB', 'CG', 'OD2'],
            LEU=['CA', 'CB', 'CG', 'CD2'],
            PHE=['CA', 'CB', 'CG', 'CD2'],
            TYR=['CA', 'CB', 'CG', 'CD2'],
        ),
        chi3=dict(
            ARG=['CB', 'CG', 'CD', 'NE'],
            GLN=['CB', 'CG', 'CD', 'OE1'],
            GLU=['CB', 'CG', 'CD', 'OE1'],
            LYS=['CB', 'CG', 'CD', 'CE'],
            MET=['CB', 'CG', 'SD', 'CE'],
        ),
        chi4=dict(
            ARG=['CG', 'CD', 'NE', 'CZ'],
            LYS=['CG', 'CD', 'CE', 'NZ'],
        ),
        chi5=dict(
            ARG=['CD', 'NE', 'CZ', 'NH1'],
        ),
    )

    default_chi = [1]
    default_outfile = "torsion_list.csv"

    def __init__(self, input, outfile=None, chi=None, units=None):
        """Set parameters and calculate torsion values"""
        if outfile is None:
            outfile = self.default_outfile
        if os.path.isfile(outfile) and os.path.getsize(outfile):
            print "Outfile exists, it will be overwritten"
        # Configure chi
        if chi is None:
            chi = self.default_chi
        chi_names = list()
        for x in chi:
            reg_chi = "chi%s" % x
            if reg_chi in self.chi_atoms.keys():
                chi_names.append(reg_chi)
                alt_chi = "altchi%s" % x
                if alt_chi in self.chi_atoms.keys():
                    chi_names.append(alt_chi)
            else:
                logging.warning("Invalid chi %s", x)
        self.chi_names = chi_names
        self.fieldnames = ["id", "model", "chain", "resn", "resi"] + self.chi_names
        logging.debug("Calculating chi angles: %s", ", ".join(chi_names))

        # Configure units (degrees or radians)
        if units is None:
            units = "degrees"
        self.degrees = bool(units[0].lower() == "d")
        if self.degrees:
            message = "Using degrees"
        else:
            message = "Using radians"
        logging.debug(message)

        # Construct list of files
        files = list()
        unprocessed = list()
        for input_item in input:
            ext = os.path.splitext(input_item)[1].lower()
            if ext == ".pdb":
                if os.path.isfile(input_item):
                    files.append(input_item)
                else:
                    unprocessed.append(input_item)
            else:
                if os.path.isdir(input_item):
                    for pattern in ("*.pdb", "*.PDB"):
                        files.extend(glob.glob(
                            os.path.join(input_item, pattern)))
                elif os.path.isfile(input_item):
                    with open(input_item, "r") as ih:
                        for line in ih:
                            line = line.strip()
                            if os.path.isfile(line):
                                files.append(line)
                            else:
                                unprocessed.append((input_item, line))
                else:
                    unprocessed.append(input_item)

        logging.debug("%s file(s) to process", len(files))
        if unprocessed:
            logging.warning("%s input items could not be interpreted:", len(unprocessed))
            for item in unprocessed:
                logging.warning("    %s", item)

        # Load parser
        self.parser = PDB.PDBParser(QUIET=True)

        # Process files
        out_data = list()
        for fn in files:
            logging.debug(fn)
            torsion_list = self.calculate_torsion(fn)
            out_data.extend(torsion_list)

        with open(outfile, "w") as oh:
            w = csv.DictWriter(oh, fieldnames=self.fieldnames)
            w.writeheader()
            w.writerows(out_data)

    def calculate_torsion(self, fn):
        """Calculate side-chain torsion angles for given file"""
        id = os.path.splitext(os.path.basename(fn))[0]

        torsion_list = list()

        structure = self.parser.get_structure(id, fn)
        for model in structure:
            model_name = model.id
            for chain in model:
                chain_name = chain.id
                for res in chain:
                    # Skip heteroatoms
                    if res.id[0] != " ": continue
                    res_name = res.resname
                    if res_name in ("ALA", "GLY"): continue
                    chi_list = [""] * len(self.chi_names)
                    for x, chi in enumerate(self.chi_names):
                        chi_res = self.chi_atoms[chi]
                        try:
                            atom_list = chi_res[res_name]
                        except KeyError:
                            continue
                        try:
                            vec_atoms = [res[a] for a in atom_list]
                        except KeyError:
                            chi_list[x] = float("nan")
                            continue
                        vectors = [a.get_vector() for a in vec_atoms]
                        angle = PDB.calc_dihedral(*vectors)
                        if self.degrees:
                            angle = math.degrees(angle)
                        chi_list[x] = angle

                    resi = "{0}{1}".format(res.id[1], res.id[2].strip())
                    row = [id, model_name, chain_name, res_name, resi] + chi_list
                    torsion_list.append(dict(zip(self.fieldnames, row)))

        return torsion_list

    @classmethod
    def commandline(cls, module_args=None):
        desc = """Calculate side-chain torsion angles for PDB files.
        Angles with missing atoms will be nan."""
        a = argparse.ArgumentParser(description=desc)
        a.add_argument("input", nargs="*", default=".",
                       help="Input file(s) (any combination of PDB files, text lists of PDB files, and directories)")
        a.add_argument("-o", "--outfile", default=cls.default_outfile,
                       help="Outfile")
        a.add_argument("-c", "--chi", type=int, nargs="*", default=cls.default_chi,
                       help="Chi angles to calculate")
        a.add_argument("-u", "--units", default="degrees",
                       help="Angle units")

        args = a.parse_args(module_args)
        c = cls(**vars(args))
        return c


if __name__ == "__main__":
    GetTorsion.commandline()
