#!/bin/env python

import argparse
import csv

from xml.etree import ElementTree as ET


OFX_DECLARATION = [('OFXHEADER', 200),
                   ('VERSION', 211),
                   ('SECURITY', 'NONE'),
                   ('OLDFILEUID', 'NONE'),
                   ('NEWFILEUID', 'NONE')]

DEFAULT_CURRENCY = 'EUR'


def convert_date(date):
    day, month, year = date.split('-')
    return year + month + day + '12' + '00' + '00.000'


def convert_account(parent, bank_id, account_number, checksum):
    ET.SubElement(parent, 'BANKID').text = bank_id
    ET.SubElement(parent, 'ACCTID').text = account_number
    ET.SubElement(parent, 'ACCTKEY').text = checksum


def argenta_csv_to_ofx(csv_filename):
    with open(csv_filename) as csv_file:
        csv_reader = spamreader = csv.reader(csv_file, delimiter=';',
                                             quoting=csv.QUOTE_NONE)

        account_label, account_number, account_descr = next(csv_reader)
        account_number = account_number.replace(' ', '')
        assert account_label == 'Nr v/d rekening :'
        assert len(account_number) == 16
        assert account_number[:4] == 'BE42'

        root = ET.Element('OFX')
        messages = ET.SubElement(root, 'BANKMSGSRSV1')
        statement_transaction = ET.SubElement(messages, 'STMTTRNRS')
        statement = ET.SubElement(statement_transaction, 'STMTRS')
        ET.SubElement(statement, 'CURDEF').text = DEFAULT_CURRENCY

        from_account = ET.SubElement(statement, 'BANKACCTFROM')
        convert_account(from_account, account_number[4:7],
                        account_number[7:14], account_number[14:])

        next(csv_reader)
        transfers = ET.SubElement(statement, 'BANKTRANLIST')
        for row in csv_reader:
            (valuta_date, reference, description, amount, currency,
             date, to_account_number, to_name, comment1, comment2) = row
            assert currency == 'EUR'
            amount = amount.replace('.', '').replace(',', '.')
            transaction = ET.SubElement(transfers, 'STMTTRN')
            transaction_type = ET.SubElement(transaction, 'TRNTYPE')
            transaction_type.text = 'DEBIT' if amount[0] == '-' else 'CREDIT'
            ET.SubElement(transaction, 'TRNUID').text = reference
            ET.SubElement(transaction, 'TRNAMT').text = amount
            if currency != DEFAULT_CURRENCY:
                ET.SubElement(transaction, 'CURRENCY').text = currency
            to_account = ET.SubElement(transaction, 'BANKACCTTO')
            convert_account(to_account, *to_account_number.split('-'))
            ET.SubElement(transaction, 'DTPOSTED').text = convert_date(date)
            ET.SubElement(transaction, 'NAME').text = to_name
            ET.SubElement(transaction, 'MEMO').text = comment1 + comment2

        ofx_filename = csv_filename.rsplit('.')[0] + '.ofx'
        with open(ofx_filename, 'wb') as ofx_file:
            pi_text = ' '.join('{}="{}"'.format(key, value)
                               for key, value in OFX_DECLARATION)
            pi = ET.ProcessingInstruction('ofx', pi_text)
            pi_tree = ET.ElementTree(pi)
            pi_tree.write(ofx_file, xml_declaration=True)

            tree = ET.ElementTree(root)
            tree.write(ofx_file, xml_declaration=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                description='Convert an Argenta CSV bank statements to Open '
                            'Financial Exchange (OFX) format.')
    parser.add_argument('input', metavar='input', type=str,
                       help='the input Argenta CSV file')

    args = parser.parse_args()
    argenta_csv_to_ofx(args.input)

