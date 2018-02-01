#/bin/env/python
#Author : Psycho_Coder
#Date : 7/11/2014

import os
import sys
import binascii

hex_link_pat = "".join("0A 2F 42 6F 72 64 65 72 20 5B 20 30 20 30 20 30 20 5D "
                       "0A 2F 41 20 3C 3C 0A 2F 54 79 70 65 20 2F 41 63 74 69 "
                       "6F 6E 0A 2F 53 20 2F 55 52 49 0A 2F 55 52 49 20 28 68 "
                       "74 74 70 3A 2F 2F 77 77 77 2E 69 74 2D 65 62 6F 6F 6B "
                       "73 2E 69 6E 66 6F 2F 29".split())

hex_text_pat = "".join("42 54 0A 31 20 30 20 30 20 31 20 30 20 30 20 54 6D 0A "
                       "28 77 77 77 2E 69 74 2D 65 62 6F 6F 6B 73 2E 69 6E 66 "
                       "6F 29 54 6A".split())


def remove_watermark(path):
    pdf_bin_data = ""
    if os.path.exists(path) and path.endswith(".pdf"):
        try:
            with open(path, "rb") as f:
                pdf_bin_data = f.read()
                pdf_bin_data = pdf_bin_data.replace(binascii.unhexlify(hex_link_pat), "")
                pdf_bin_data = pdf_bin_data.replace(binascii.unhexlify(hex_text_pat), "")
        except IOError:
            sys.stderr.write("Error in opening file")
    else:
        raise ValueError("Path invalid or file is not in PDF format")

    return pdf_bin_data


if __name__ == "__main__":
    testfile = os.path.join(os.getcwd(), "Cyber Threat.pdf")
    try:
        with open("ModifiedFile.pdf", "wb") as f:
            f.write(remove_watermark(testfile))
    except IOError:
        sys.stderr.write("Problem in writing file.")
